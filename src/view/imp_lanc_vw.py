import os.path
from re import L

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from lib.Genericos.log import logging
from lib.ImportacaoLanc.FirstStep import AbrirExcelErro, FirstStepFrame, NewLancamento
from lib.ImportacaoLanc.SecondStep import SecondStepFrame
from model.Conta import Conta
from model.Lancamento import Lancamentos as ORMLancamentos
from util.my_dialog import MyDialog
from util.settings import JanelaImportLancamentosSettings, Settings
from util.toaster import QToaster


class ImportarLancamentosView(MyDialog):
    """ Janela principal de importacao de lancamentos"""

    # list[NewLa]
    importacao_finalizada = pyqtSignal(list)

    def __init__(self, parent: QWidget, conta_dc: Conta) -> None:
        super(ImportarLancamentosView, self).__init__(parent)

        self.conta_dc = conta_dc
        self.global_settings = Settings()
        self.settings: JanelaImportLancamentosSettings = \
            self.global_settings.load_impo_lanc_settings(self.conta_dc.id)

        self.btn_procurar = QPushButton("Procurar...")
        self.first_table_frame = FirstStepFrame(self, self.settings)
        self.first_table_frame.passo_proximo.connect(self.on_proximo)

        self.second_table_frame = SecondStepFrame(self)
        self.second_table_frame.passo_anterior.connect(self.on_anterior)
        self.second_table_frame.import_linhas.connect(self.on_importar_clicked)

        self.toolbar = QToolBar()
        self.file_path = QLineEdit()
        self.decimal_separator = QLineEdit(self.settings.separador_decimal)
        self.decimal_separator.setObjectName("separador_decimal")
        self.decimal_separator.editingFinished.connect(
            lambda: self._on_change_params(self.decimal_separator)
        )
        self.mil_separator = QLineEdit(self.settings.separador_milhar)
        self.mil_separator.setObjectName("separador_milhar")
        self.mil_separator.editingFinished.connect(
            lambda: self._on_change_params(self.mil_separator)
        )
        self.date_format = QLineEdit(self.settings.formato_data)
        self.date_format.setObjectName("formato_data")
        self.date_format.editingFinished.connect(
            lambda: self._on_change_params(self.date_format)
        )

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(
            f"Importar Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})"
        )
        self.restore_geometry()
        self.on_close_signal.connect(self.on_close)

        # layout
        layout = QVBoxLayout()
        layout.addLayout(self.get_import_file_line())
        layout.addLayout(self.get_config_line())
        layout.addWidget(self.first_table_frame)
        layout.addWidget(self.second_table_frame)
        self.second_table_frame.setVisible(False)

        self.setLayout(layout)

        # model
        self.model_lancamentos = ORMLancamentos(conta_dc)

    def on_anterior(self) -> None:
        self.first_table_frame.setVisible(True)
        self.second_table_frame.setVisible(False)

    def on_proximo(self, linhas: list) -> None:
        self.first_table_frame.setVisible(False)
        self.second_table_frame.setVisible(True)
        self.second_table_frame.set_linhas(linhas)

    def on_close(self):
        self.settings.dimensoes = self.saveGeometry()

    def restore_geometry(self) -> None:
        self.setMinimumSize(800, 600)
        try:
            self.restoreGeometry(self.settings.dimensoes)
        except Exception as e:
            logging.error(str(e))
            self.resize(1600, 900)

    def _on_change_params(self, source: QLineEdit):
        """Grava configuracoes de importação diretamente nos settings"""
        logging.debug("Entrou no on change")
        if source.objectName() == "separador_decimal":
            self.settings.separador_decimal = source.text()
        elif source.objectName() == "separador_milhar":
            self.settings.separador_milhar = source.text()
        elif source.objectName() == "formato_data":
            self.settings.formato_data = source.text()

    def get_import_file_line(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Importar arquivo:"))
        layout.addWidget(self.file_path)
        self.file_path.setEnabled(False)
        layout.addWidget(self.btn_procurar)
        self.btn_procurar.clicked.connect(self.on_procurar_clicked)
        return layout

    def get_config_line(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Separador Milhar:"))
        layout.addWidget(self.mil_separator)
        layout.addWidget(QLabel("Separador Decimal:"))
        layout.addWidget(self.decimal_separator)
        layout.addWidget(QLabel("Formato Data:"))
        layout.addWidget(self.date_format)

        return layout

    def on_procurar_clicked(self):
        """
        Chama popup de procura arquivo a ser importado
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        (file_name_fullpath, selectedFilter) = dialog.getOpenFileName()
        if os.path.isfile(file_name_fullpath):
            self.file_path.setText(file_name_fullpath)
            try:
                self.first_table_frame.csv_to_table(file_name_fullpath)
            except AbrirExcelErro as e:
                QMessageBox(
                    QMessageBox.Warning,
                    f"Erro no formato {e}",
                    str(e),
                    QMessageBox.Ok,
                ).exec_()
                self.file_path.setText("")

    def on_importar_clicked(self, linhas:list[NewLancamento]) -> None:
        created_lines = 0
        for new_lancamento in linhas:
            new_lancamento.conta_id = int(self.conta_dc.id)
            # criar novo lancamento
            new_lancamento_id = self.model_lancamentos.add_new(
                conta_id=new_lancamento.conta_id,
                nr_referencia=new_lancamento.nr_referencia,
                descricao=new_lancamento.descricao,
                descricao_user=new_lancamento.descricao_user,
                data=new_lancamento.data,
                valor=new_lancamento.valor,
            )
            if new_lancamento_id > 0:
                new_lancamento.id = new_lancamento_id
                new_lancamento.status_import = "Importação executada com sucesso."
                created_lines += 1
            else:
                new_lancamento.status_import = "Erro ao importar linha."
            # atualiza relação entre o lancamento e categoria
            if new_lancamento.categoria_id:
                self.model_lancamentos.update(new_lancamento_id, 'categoria_id', new_lancamento.categoria_id)

        QToaster.showMessage(
            self,
            f"Foram criados { created_lines } novos lançamentos." if created_lines > 0
                else "Não foram criados lançamentos.",
            closable=False,
            timeout=2000,
            corner=Qt.BottomRightCorner,
        )                
        self.importacao_finalizada.emit(linhas)


