import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget, QHeaderView, QComboBox, QFrame, QTextEdit, QDialog, QDesktopWidget, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PyQt5.QtCore import Qt, QTimer
from pix_app.pix_utils import gerar_payload_pix, gerar_qr_pix

CONFIG_FILE = "pix_config.json"
PERFIS_FILE = "perfis.json"
COR_PRIMARIA = "#036da1"
COR_FUNDO = "white"

# Textos
MSG_CAMPOS_OBRIGATORIOS = "Campos obrigatórios"
MSG_PREENCHER_CAMPOS = "Preencha chave Pix, cidade, valor e nome."
MSG_PREENCHER_CAMPOS_PIX = "Preencha chave Pix e cidade."
LABEL_NOME_EMPRESA = "Nome da empresa"
MSG_VALOR_INVALIDO = "Valor inválido"
MSG_DIGITE_VALOR_VALIDO = "Digite um valor válido."
MSG_SUCESSO = "Sucesso"
MSG_QR_SALVO = "QR Code salvo em {}"
MSG_QRS_GERADOS = "{} QR Codes gerados na pasta {}"
MSG_PERFIL_SALVO_TITULO = "Perfil salvo"
MSG_PERFIL_SALVO = "Perfil salvo com sucesso!"
MSG_PERFIL_REMOVIDO_TITULO = "Perfil removido"
MSG_PERFIL_REMOVIDO = "Perfil removido com sucesso!"

# Dimensões
ALTURA_INPUT = 42  # altura dos campos de entrada

# Estilos
ESTILO_INPUT = "padding:10px 12px; border-radius:8px; border:1px solid #ccc; margin-bottom:12px; font-size: 13px;"
ESTILO_BTN_PRIMARIO = f"background-color: {COR_PRIMARIA}; color: white; font-weight: bold; border-radius:8px; padding:2px 24px; font-size:16px; border: none;"
ESTILO_BTN_SECUNDARIO = f"background-color: {COR_PRIMARIA}; color: white; font-weight: bold; border-radius:8px; padding:2px 20px; font-size:14px; border: none;"
ESTILO_LABEL = "border:none; font-weight:bold; margin-bottom:2px; font-size:12px;"
ESTILO_BTN_CONFIG = "border:none; background:none; margin:8px;"
ESTILO_TOOLBAR = "background:transparent; border:none;"
ESTILO_QR_LABEL = "margin:16px;"
ESTILO_COPIA_COLA = "background:#f7f7f7; border-radius:8px; border:1px solid #ccc; margin-top:8px; padding:2px;"
ESTILO_POPUP = "background:#333;color:white;padding:2px;border-radius:6px;"

class PerfisManager:
    def __init__(self, path):
        self.path = path
        self.perfis = []
        self.load()
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.perfis = json.load(f)
            except Exception:
                self.perfis = []
        else:
            self.perfis = []
    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.perfis, f, ensure_ascii=False, indent=2)
    def add(self, perfil):
        self.perfis.append(perfil)
        self.save()
    def update(self, idx, perfil):
        self.perfis[idx] = perfil
        self.save()
    def remove(self, idx):
        del self.perfis[idx]
        self.save()
    def get(self, idx):
        return self.perfis[idx] if 0 <= idx < len(self.perfis) else None
    def all(self):
        return self.perfis

class PixConfig:
    def __init__(self, path):
        self.path = path
        self.data = {"chave_pix": "", "cidade": ""}
        self.load()
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass
    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
    def get(self, k):
        return self.data.get(k, "")
    def set(self, k, v):
        self.data[k] = v
        self.save()

class PixUnitarioWidget(QWidget):
    def __init__(self, config, perfil_destaque):
        super().__init__()
        self.config = config
        self.perfil_destaque = perfil_destaque
        self.qr_pixmap = None
        self.payload = None
        self.init_ui()
        self.perfil_destaque.combo.currentIndexChanged.connect(self.preencher_campos_perfil)
        self.preencher_campos_perfil()
    def init_ui(self):
        # layout principal: formulário à esquerda, QR + copia/cola à direita
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        # Card visual
        card = QFrame()
        card.setStyleSheet(f"background: {COR_FUNDO}; border-radius: 16px; border: 2px solid {COR_PRIMARIA};")
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)
        # tornar o card mais largo para dar espaço aos inputs
        # janela principal tem 680px, então deixamos o card com largura mínima confortável
        card.setMinimumWidth(620)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Chave Pix
        self.chave_pix = QLineEdit()
        self.chave_pix.setPlaceholderText("CNPJ ou chave Pix")
        self.chave_pix.setFont(font)
        self.chave_pix.setStyleSheet(ESTILO_INPUT)
        self.chave_pix.setMinimumHeight(ALTURA_INPUT)

        # Cidade
        self.cidade = QLineEdit()
        self.cidade.setPlaceholderText("Cidade")
        self.cidade.setFont(font)
        self.cidade.setStyleSheet(ESTILO_INPUT)
        self.cidade.setMinimumHeight(ALTURA_INPUT)

        # Valor
        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Valor (ex: 150,00 ou 150.00)")
        self.valor.setFont(font)
        self.valor.setStyleSheet(ESTILO_INPUT)
        self.valor.setMinimumHeight(ALTURA_INPUT)

        # Descrição
        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Descrição (máx 25 bytes)")
        self.descricao.setFont(font)
        self.descricao.setStyleSheet(ESTILO_INPUT)
        self.descricao.setMinimumHeight(ALTURA_INPUT)

        # Nome da empresa
        self.nome_empresa = QLineEdit()
        self.nome_empresa.setPlaceholderText(LABEL_NOME_EMPRESA)
        self.nome_empresa.setFont(font)
        self.nome_empresa.setStyleSheet(ESTILO_INPUT)
        self.nome_empresa.setMinimumHeight(ALTURA_INPUT)

        # CNPJ da empresa
        self.cnpj_empresa = QLineEdit()
        self.cnpj_empresa.setPlaceholderText("CNPJ/CPF")
        self.cnpj_empresa.setFont(font)
        self.cnpj_empresa.setStyleSheet(ESTILO_INPUT)
        self.cnpj_empresa.setMinimumHeight(ALTURA_INPUT)

        # Botão gerar
        btn_gerar = QPushButton("Gerar QR Code")
        btn_gerar.setStyleSheet(ESTILO_BTN_PRIMARIO)
        btn_gerar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_gerar.clicked.connect(self.gerar_qr)

        # Área de exibição do QR e copia e cola (lado direito)
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet(ESTILO_QR_LABEL)
        # tamanho do QR reduzido em 15% (era 360 -> agora 306)
        self.qr_label.setFixedSize(200, 200)

        self.copia_cola = QTextEdit()
        self.copia_cola.setReadOnly(True)
        self.copia_cola.setFont(QFont("Consolas", 11))
        self.copia_cola.setStyleSheet(ESTILO_COPIA_COLA)
        self.copia_cola.setFixedHeight(100)
        self.copia_cola.viewport().setCursor(Qt.PointingHandCursor)
        self.copia_cola.mousePressEvent = self.copiar_codigo

        # Botão baixar QR
        self.btn_baixar = QPushButton("Baixar QR Code")
        self.btn_baixar.setStyleSheet(ESTILO_BTN_SECUNDARIO)
        # manter o botão visível mas desabilitado até que um QR seja gerado
        self.btn_baixar.setEnabled(False)
        self.btn_baixar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_baixar.clicked.connect(self.baixar_qr)

        # Labels sem borda azul
        def label(text):
            l = QLabel(text)
            # tamanho e espaçamento moderados para evitar aparência achatada
            l.setStyleSheet(ESTILO_LABEL)
            return l

        # esquerda: inputs / direita: qr + copia
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(10)
        left_layout.addWidget(label("Chave Pix:"))
        left_layout.addWidget(self.chave_pix)
        left_layout.addWidget(label("Cidade:"))
        left_layout.addWidget(self.cidade)
        left_layout.addWidget(label("Valor:"))
        left_layout.addWidget(self.valor)
        left_layout.addWidget(label("Descrição:"))
        left_layout.addWidget(self.descricao)
        left_layout.addWidget(label("Nome da empresa:"))
        left_layout.addWidget(self.nome_empresa)
        left_layout.addWidget(label("CNPJ/CPF:"))
        left_layout.addWidget(self.cnpj_empresa)
        # botões: Gerar e Baixar lado a lado
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(10)
        # garantir que os dois botões partilhem o espaço disponível
        btn_row.addWidget(btn_gerar)
        btn_row.addWidget(self.btn_baixar)
        btn_row.setStretch(0, 1)
        btn_row.setStretch(1, 1)
        # aumentar um pouco a altura dos botões para melhor presença
        btn_gerar.setMinimumHeight(44)
        self.btn_baixar.setMinimumHeight(44)
        # envolver em widget para garantir que a linha ocupe toda a largura disponível
        btn_container = QWidget()
        btn_container.setLayout(btn_row)
        btn_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_layout.addWidget(btn_container)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        right_layout.addWidget(self.qr_label)

        content_layout = QHBoxLayout()
        # aumentar espaço para os labels (coluna esquerda) — dar mais peso à esquerda
        # usamos proporção 7:3 para favorecer a área de inputs e permitir botões largos
        content_layout.addLayout(left_layout, 7)
        content_layout.addLayout(right_layout, 3)

        card_layout.addLayout(content_layout)
        # copia e cola abaixo, ocupando toda a largura do card
        card_layout.addWidget(label("Copia e Cola:"))
        card_layout.addWidget(self.copia_cola)

        card.setLayout(card_layout)
        main_layout.addStretch()
        main_layout.addWidget(card)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def gerar_qr(self):
        chave = self.chave_pix.text().strip()
        cidade = self.cidade.text().strip()
        valor = self.valor.text().strip()
        descricao = self.descricao.text().strip()
        nome = self.nome_empresa.text().strip()
        if not chave or not cidade or not valor or not nome:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha chave Pix, cidade, valor e nome.")
            return
        try:
            valor_float = float(valor.replace(".", ".").replace(",", "."))
        except Exception:
            QMessageBox.warning(self, "Valor inválido", "Digite um valor válido.")
            return
        self.config.set("chave_pix", chave)
        self.config.set("cidade", cidade)
        self.payload = gerar_payload_pix(chave, nome, cidade, valor_float, descricao)
        # Gera QR temporário
        temp_path = "temp_qr_pix.png"
        gerar_qr_pix(self.payload, temp_path)
        pixmap = QPixmap(temp_path)
        self.qr_label.setPixmap(pixmap.scaled(306,306, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.copia_cola.setText(self.payload)
        self.btn_baixar.setEnabled(True)
        try:
            os.remove(temp_path)
        except Exception:
            pass

    def copiar_codigo(self, event):
        if self.payload:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.payload)
            self.show_temp_popup("Código copiado!")
        QTextEdit.mousePressEvent(self.copia_cola, event)

    def show_temp_popup(self, text: str, duration_ms: int = 2000):
        popup = QLabel(text, self)
        popup.setStyleSheet(ESTILO_POPUP)
        popup.setAttribute(Qt.WA_TransparentForMouseEvents)
        popup.adjustSize()
        # posiciona acima do centro da area de copia
        g = self.copia_cola.mapToGlobal(self.copia_cola.rect().center())
        local = self.mapFromGlobal(g)
        x = max(10, local.x() - popup.width() // 2)
        y = max(10, local.y() - popup.height() - 10)
        popup.move(x, y)
        popup.show()
        QTimer.singleShot(duration_ms, popup.deleteLater)

    def baixar_qr(self):
        if self.payload:
            file_path, _ = QFileDialog.getSaveFileName(self, "Salvar QR Code", "qrcode_pix.png", "PNG Files (*.png)")
            if file_path:
                gerar_qr_pix(self.payload, file_path)
                QMessageBox.information(self, MSG_SUCESSO, MSG_QR_SALVO.format(file_path))

    def gerar_qr(self):
        chave = self.chave_pix.text().strip()
        cidade = self.cidade.text().strip()
        valor = self.valor.text().strip()
        descricao = self.descricao.text().strip()
        nome = self.nome_empresa.text().strip()
        if not chave or not cidade or not valor or not nome:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha chave Pix, cidade, valor e nome.")
            return
        try:
            valor_float = float(valor.replace(",", "."))
        except Exception:
            QMessageBox.warning(self, MSG_VALOR_INVALIDO, MSG_DIGITE_VALOR_VALIDO)
            return
        self.config.set("chave_pix", chave)
        self.config.set("cidade", cidade)
        self.payload = gerar_payload_pix(chave, nome, cidade, valor_float, descricao)
        # Gera QR temporário
        temp_path = "temp_qr_pix.png"
        gerar_qr_pix(self.payload, temp_path)
        pixmap = QPixmap(temp_path)
        self.qr_label.setPixmap(pixmap.scaled(306,306, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.copia_cola.setText(self.payload)
        self.btn_baixar.setEnabled(True)
        # Remove arquivo temporário
        try:
            os.remove(temp_path)
        except Exception:
            pass

    def preencher_campos_perfil(self):
        perfil = self.perfil_destaque.perfil_ativo()
        if perfil:
            self.chave_pix.setText(perfil.get("chave_pix", ""))
            self.cidade.setText(perfil.get("endereco", ""))
            self.nome_empresa.setText(perfil.get("nome", ""))
            self.cnpj_empresa.setText(perfil.get("cnpj_cpf", ""))

class PixMassaWidget(QWidget):
    def __init__(self, config, perfil_destaque):
        super().__init__()
        self.config = config
        self.perfil_destaque = perfil_destaque
        self.init_ui()
        self.perfil_destaque.combo.currentIndexChanged.connect(self.preencher_campos_perfil)
        self.preencher_campos_perfil()
    def init_ui(self):
        layout = QVBoxLayout()
        font = QFont()
        font.setPointSize(11)
        # Chave Pix
        self.chave_pix = QLineEdit()
        self.chave_pix.setPlaceholderText("CNPJ ou chave Pix")
        self.chave_pix.setFont(font)
        # Cidade
        self.cidade = QLineEdit()
        self.cidade.setPlaceholderText("Cidade")
        self.cidade.setFont(font)
        # Nome da empresa
        self.nome_empresa = QLineEdit()
        self.nome_empresa.setPlaceholderText("Nome da empresa")
        self.nome_empresa.setFont(QFont("Arial", 11))
        # CNPJ da empresa
        self.cnpj_empresa = QLineEdit()
        self.cnpj_empresa.setPlaceholderText("CNPJ/CPF")
        self.cnpj_empresa.setFont(QFont("Arial", 11))
        # Tabela de valores/descrições
        self.table = QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["Valor", "Descrição"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Botão gerar em massa
        btn_gerar = QPushButton("Gerar QRs em Massa")
        btn_gerar.setStyleSheet(f"background-color: {COR_PRIMARIA}; color: white; font-weight: bold;")
        btn_gerar.clicked.connect(self.gerar_qrs)
        # Layout
        layout.addWidget(QLabel("Chave Pix:"))
        layout.addWidget(self.chave_pix)
        layout.addWidget(QLabel("Cidade:"))
        layout.addWidget(self.cidade)
        layout.addWidget(QLabel("Nome da empresa:"))
        layout.addWidget(self.nome_empresa)
        layout.addWidget(QLabel("CNPJ/CPF:"))
        layout.addWidget(self.cnpj_empresa)
        layout.addWidget(QLabel("Tabela de valores e descrições:"))
        layout.addWidget(self.table)
        layout.addWidget(btn_gerar)
        self.setLayout(layout)
    def gerar_qrs(self):
        chave = self.chave_pix.text().strip()
        cidade = self.cidade.text().strip()
        if not chave or not cidade:
            QMessageBox.warning(self, MSG_CAMPOS_OBRIGATORIOS, MSG_PREENCHER_CAMPOS_PIX)
            return
        self.config.set("chave_pix", chave)
        self.config.set("cidade", cidade)
        # Seleciona pasta para salvar
        pasta, _ = QFileDialog.getExistingDirectory(self, "Selecionar pasta para salvar QRs")
        if not pasta:
            return
        count = 0
        for row in range(self.table.rowCount()):
            valor_item = self.table.item(row, 0)
            desc_item = self.table.item(row, 1)
            valor = valor_item.text().strip() if valor_item else ""
            descricao = desc_item.text().strip() if desc_item else ""
            if not valor:
                continue
            try:
                valor_float = float(valor.replace(",", "."))
            except Exception:
                continue
            payload = gerar_payload_pix(chave, "Seu Nome", cidade, valor_float, descricao)
            file_path = os.path.join(pasta, f"qrcode_pix_{row+1}.png")
            gerar_qr_pix(payload, file_path)
            count += 1
        QMessageBox.information(self, MSG_SUCESSO, MSG_QRS_GERADOS.format(count, pasta))

    def preencher_campos_perfil(self):
        perfil = self.perfil_destaque.perfil_ativo()
        if perfil:
            self.chave_pix.setText(perfil.get("chave_pix", ""))
            self.cidade.setText(perfil.get("endereco", ""))
            self.nome_empresa.setText(perfil.get("nome", ""))
            self.cnpj_empresa.setText(perfil.get("cnpj_cpf", ""))

class PerfilCadastroDialog(QDialog):
    def __init__(self, perfis_manager):
        super().__init__()
        self.setWindowTitle("Perfis de Empresa")
        self.setMinimumWidth(400)
        self.perfis_manager = perfis_manager
        self.selected_idx = None
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        font = QFont()
        font.setPointSize(11)
        self.combo = QComboBox()
        self.combo.setFont(font)
        self.combo.currentIndexChanged.connect(self.carregar_perfil)
        layout.addWidget(QLabel("Selecione ou cadastre um perfil de empresa:"))
        layout.addWidget(self.combo)
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome da empresa")
        self.nome.setFont(font)
        layout.addWidget(self.nome)
        self.cnpj_cpf = QLineEdit()
        self.cnpj_cpf.setPlaceholderText("CNPJ ou CPF")
        self.cnpj_cpf.setFont(font)
        layout.addWidget(self.cnpj_cpf)
        self.chave_pix = QLineEdit()
        self.chave_pix.setPlaceholderText("Chave Pix")
        self.chave_pix.setFont(font)
        layout.addWidget(self.chave_pix)
        self.endereco = QLineEdit()
        self.endereco.setPlaceholderText("Endereço")
        self.endereco.setFont(font)
        layout.addWidget(self.endereco)
        self.logo_path = QLineEdit()
        self.logo_path.setPlaceholderText("Caminho do logotipo")
        self.logo_path.setFont(font)
        layout.addWidget(self.logo_path)
        btn_logo = QPushButton("Selecionar logotipo")
        btn_logo.clicked.connect(self.selecionar_logo)
        layout.addWidget(btn_logo)
        btn_salvar = QPushButton("Salvar perfil")
        btn_salvar.setStyleSheet(f"background-color: {COR_PRIMARIA}; color: white; font-weight: bold;")
        btn_salvar.clicked.connect(self.salvar_perfil)
        layout.addWidget(btn_salvar)
        btn_novo = QPushButton("Novo perfil")
        btn_novo.clicked.connect(self.novo_perfil)
        layout.addWidget(btn_novo)
        btn_remover = QPushButton("Remover perfil")
        btn_remover.clicked.connect(self.remover_perfil)
        layout.addWidget(btn_remover)
        self.setLayout(layout)
        self.atualizar_combo()
    def atualizar_combo(self):
        self.combo.clear()
        for perfil in self.perfis_manager.all():
            self.combo.addItem(perfil.get("nome", "(sem nome)"))
        self.combo.addItem("<Novo perfil>")
        self.combo.setCurrentIndex(len(self.perfis_manager.all()))
        self.novo_perfil()
    def carregar_perfil(self, idx):
        if idx < len(self.perfis_manager.all()):
            perfil = self.perfis_manager.get(idx)
            if perfil:
                self.nome.setText(perfil.get("nome", ""))
                self.cnpj_cpf.setText(perfil.get("cnpj_cpf", ""))
                self.chave_pix.setText(perfil.get("chave_pix", ""))
                self.endereco.setText(perfil.get("endereco", ""))
                self.logo_path.setText(perfil.get("logotipo", ""))
                self.selected_idx = idx
            else:
                self.novo_perfil()
        else:
            self.novo_perfil()
    def novo_perfil(self):
        self.nome.setText("")
        self.cnpj_cpf.setText("")
        self.chave_pix.setText("")
        self.endereco.setText("")
        self.logo_path.setText("")
        self.selected_idx = None
    def selecionar_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar logotipo", "", "Imagens (*.png *.jpg *.jpeg)")
        if file_path:
            self.logo_path.setText(file_path)
    def salvar_perfil(self):
        perfil = {
            "nome": self.nome.text().strip(),
            "cnpj_cpf": self.cnpj_cpf.text().strip(),
            "chave_pix": self.chave_pix.text().strip(),
            "endereco": self.endereco.text().strip(),
            "logotipo": self.logo_path.text().strip()
        }
        if self.selected_idx is not None and self.selected_idx < len(self.perfis_manager.all()):
            self.perfis_manager.update(self.selected_idx, perfil)
        else:
            self.perfis_manager.add(perfil)
        self.atualizar_combo()
        QMessageBox.information(self, MSG_PERFIL_SALVO_TITULO, MSG_PERFIL_SALVO)
    def remover_perfil(self):
        idx = self.combo.currentIndex()
        if idx < len(self.perfis_manager.all()):
            self.perfis_manager.remove(idx)
            self.atualizar_combo()
            QMessageBox.information(self, MSG_PERFIL_REMOVIDO_TITULO, MSG_PERFIL_REMOVIDO)

class PerfilDestaqueWidget(QWidget):
    def __init__(self, perfis_manager):
        super().__init__()
        self.perfis_manager = perfis_manager
        self.combo = QComboBox()
        self.combo.setFont(QFont("Arial", 11))
        self.combo.currentIndexChanged.connect(self.atualizar_destaque)
        self.nome_label = QLabel()
        self.cnpj_label = QLabel()
        self.endereco_label = QLabel()
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(60,60)
        layout = QHBoxLayout()
        layout.addWidget(self.logo_label)
        vbox = QVBoxLayout()
        vbox.addWidget(self.combo)
        vbox.addWidget(self.nome_label)
        vbox.addWidget(self.cnpj_label)
        vbox.addWidget(self.endereco_label)
        layout.addLayout(vbox)
        self.setLayout(layout)
        self.atualizar_combo()
        self.atualizar_destaque()
    def atualizar_combo(self):
        self.combo.clear()
        for perfil in self.perfis_manager.all():
            self.combo.addItem(perfil.get("nome", "(sem nome)"))
        if not self.perfis_manager.all():
            self.combo.addItem("<Cadastre um perfil>")
    def atualizar_destaque(self):
        idx = self.combo.currentIndex()
        perfil = self.perfis_manager.get(idx) if idx < len(self.perfis_manager.all()) else None
        if perfil:
            self.nome_label.setText(f"Nome: {perfil.get('nome','')}")
            self.cnpj_label.setText(f"CNPJ/CPF: {perfil.get('cnpj_cpf','')}")
            self.endereco_label.setText(f"Endereço: {perfil.get('endereco','')}")
            logo_path = perfil.get("logotipo","")
            if logo_path and os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                self.logo_label.setPixmap(pixmap.scaled(60,60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.clear()
        else:
            self.nome_label.setText("")
            self.cnpj_label.setText("")
            self.endereco_label.setText("")
            self.logo_label.clear()
    def perfil_ativo(self):
        idx = self.combo.currentIndex()
        return self.perfis_manager.get(idx) if idx < len(self.perfis_manager.all()) else None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # abrir com tamanho fixo 680x850 e centralizar
        self.setWindowTitle("Pix QR Code")
        self.setFixedSize(680, 850)
        # centraliza a janela
        center_point = QDesktopWidget().availableGeometry().center()
        self.move(center_point.x() - 680 // 2, center_point.y() - 850 // 2)
        self.config = PixConfig(CONFIG_FILE)
        self.perfis_manager = PerfisManager(PERFIS_FILE)
        self.init_ui()
    def init_ui(self):
        central_widget = QWidget()
        # layout horizontal: esquerda = painel principal (perfil + tabs)
        central_layout = QHBoxLayout()

        left_container = QWidget()
        left_vlayout = QVBoxLayout()
        self.perfil_destaque = PerfilDestaqueWidget(self.perfis_manager)
        left_vlayout.addWidget(self.perfil_destaque)
        self.tabs = QTabWidget()
        self.tabs.addTab(PixUnitarioWidget(self.config, self.perfil_destaque), "Gerar Pix Unitário")
        self.tabs.addTab(PixMassaWidget(self.config, self.perfil_destaque), "Gerar Pix em Massa")
        left_vlayout.addWidget(self.tabs)
        left_container.setLayout(left_vlayout)

        central_layout.addWidget(left_container, 3)
        # espaço restante à direita ficará com o conteúdo responsivo (QR está dentro do tab)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(COR_FUNDO))
        self.setPalette(pal)
        logo_path = os.path.join(os.path.dirname(__file__), "Logo Oficial.png")
        btn_config = QPushButton()
        if os.path.exists(logo_path):
            btn_config.setIcon(QIcon(logo_path))
        else:
            btn_config.setIcon(QIcon())
        btn_config.setToolTip("Configurar perfis de empresa")
        btn_config.setStyleSheet(ESTILO_BTN_CONFIG)
        btn_config.setFixedSize(32,32)
        btn_config.clicked.connect(self.abrir_perfis)
        self.addToolBarBreak()
        self.toolbar = self.addToolBar("")
        self.toolbar.setMovable(False)
        self.toolbar.addWidget(btn_config)
        self.toolbar.setStyleSheet(ESTILO_TOOLBAR)
    def abrir_perfis(self):
        dialog = PerfilCadastroDialog(self.perfis_manager)
        dialog.exec_()
        self.perfil_destaque.atualizar_combo()
        self.perfil_destaque.atualizar_destaque()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
