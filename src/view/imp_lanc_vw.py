import os.path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from lib.Genericos.QMessageHelper import MyMessagePopup
from lib.Genericos.log import logging
from lib.ImportacaoLanc.FirstStep import (
    AbrirExcelErro,
    ConfigImportacaoBlock,
    FirstStepFrame,
    NewLancamento,
    NewLancamentoStatus,
)
from lib.ImportacaoLanc.SecondStep import SecondStepFrame
from lib import CustomToolbar
from model import Conta, ORMLancamentos
from util import MyDialog, JanelaImportLancamentosSettings, Settings
from util.toaster import QToaster
import view.icons.icons as icons


class ImportarLancamentosView(MyDialog):
    """Janela principal de importacao de lancamentos"""

    # list[NewLancamento]
    importacao_finalizada = pyqtSignal(list)

    def __init__(self, parent: QWidget, conta_dc: Conta) -> None:
        super(ImportarLancamentosView, self).__init__(parent)

        self.conta_dc = conta_dc
        self.global_settings = Settings()
        self.settings: JanelaImportLancamentosSettings = self.global_settings.load_impo_lanc_settings(self.conta_dc.id)

        self.btn_procurar = QPushButton("Importar")
        self.first_table_frame = FirstStepFrame(self, self.settings)
        self.first_table_frame.passo_proximo.connect(self.on_proximo)

        self.second_table_frame = SecondStepFrame(self)
        self.second_table_frame.passo_anterior.connect(self.on_anterior)
        self.second_table_frame.import_linhas.connect(self.on_importar_clicked)

        self.toolbar = CustomToolbar()
        self.file_path = QLineEdit()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(f"Importar Lançamentos - (Conta {conta_dc.id} | {conta_dc.descricao})")
        self.restore_geometry()
        self.on_close_signal.connect(self.on_close)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.get_import_file_line())
        layout.addWidget(ConfigImportacaoBlock(self, self.settings))
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

    def get_import_file_line(self) -> QWidget:
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Importar arquivo:"))
        layout.addWidget(self.file_path)
        btn_choose_file = self.file_path.addAction(icons.find_file_dialog(), QLineEdit.TrailingPosition)
        btn_choose_file.triggered.connect(self.on_procurar_clicked)
        layout.addWidget(self.btn_procurar)
        self.btn_procurar.clicked.connect(self.processar_arquivo)

        container = QWidget()
        container.setLayout(layout)
        return container

    def on_procurar_clicked(self):
        """
        Chama popup de procura arquivo a ser importado
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        (file_name_fullpath, selectedFilter) = dialog.getOpenFileName()
        self.file_path.setText(file_name_fullpath)
        self.processar_arquivo()

    def processar_arquivo(self):
        try:
            file_name_fullpath = self.file_path.text()
            if not os.path.isfile(file_name_fullpath):
                MyMessagePopup(self).info(f"Arquivo: {file_name_fullpath} não encontrado.")
                return

            self.first_table_frame.csv_to_table(file_name_fullpath)
        except AbrirExcelErro as e:
            MyMessagePopup(self).warn(f"Erro no formato {e}")

    def on_importar_clicked(self, linhas: list[NewLancamento]) -> None:
        created_lines = 0
        for new_lancamento in linhas:
            if not new_lancamento.pode_inserir:
                new_lancamento.message = "Não inserido"
                continue

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
                new_lancamento.message = "Importação executada com sucesso."
                new_lancamento.message_status = NewLancamentoStatus.Sucesso
                new_lancamento.pode_inserir = False
                created_lines += 1
            else:
                new_lancamento.message = "Erro ao importar linha."
                new_lancamento.message_status = NewLancamentoStatus.Erro
                new_lancamento.pode_inserir = False

            # atualiza relação entre o lancamento e categoria
            if new_lancamento.categoria_id:
                self.model_lancamentos.update(new_lancamento_id, "categoria_id", new_lancamento.categoria_id)

        QToaster.showMessage(
            self,
            f"Foram criados { created_lines } novos lançamentos."
            if created_lines > 0
            else "Não foram criados lançamentos.",
            closable=False,
            timeout=2000,
            corner=Qt.BottomRightCorner,
        )
        self.importacao_finalizada.emit(linhas)
