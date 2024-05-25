from lib.Genericos.log import logging
import os.path

from lib.ImportacaoLanc.FirstStep import AbrirExcelErro, FirstStepFrame, NewLancamento
from model.Conta import Conta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QToolBar,
    QLabel,
    QMessageBox,
)
from model.Lancamento import Lancamentos as ORMLancamentos
from util.my_dialog import MyDialog
from util.settings import Settings, JanelaImportLancamentosSettings
from util.toaster import QToaster


class ImportarLancamentosView(MyDialog):
    def __init__(self, parent: QWidget, conta_dc: Conta):
        super(ImportarLancamentosView, self).__init__(parent)

        self.conta_dc = conta_dc
        self.global_settings = Settings()
        self.settings: JanelaImportLancamentosSettings = \
            self.global_settings.load_impo_lanc_settings(self.conta_dc.id)

        self.btn_procurar = QPushButton("Procurar...")
        self.table_frame = FirstStepFrame(self, self.settings)
        self.table_frame.importar_linhas_clicked.connect(self.on_importar_clicked)

        self.table = self.table_frame.table
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

        self.model_lancamentos = ORMLancamentos(conta_dc)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(
            f"Importar Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})"
        )
        self.restore_geometry()
        self.on_close_signal.connect(self.on_close)

        layout = QVBoxLayout()
        layout.addLayout(self.get_import_file_line())
        layout.addLayout(self.get_config_line())
        layout.addWidget(self.table_frame)

        self.setLayout(layout)

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
                self.table_frame.csv_to_table(file_name_fullpath)
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
                created_lines += 1
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


