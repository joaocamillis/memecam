from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

from PySide6.QtCore import QThread, Signal, QTimer

from ui.main_window import MainWindow

class LoginWorker(QThread):
    success = Signal(dict)
    error = Signal(str)
    
    def __init__(self, api_client, login_value, password):
        super().__init__()
        self.api_client = api_client
        self.login_value = login_value
        self.password = password
        
    def run(self):
        try:
            self.api_client.login(self.login_value, self.password)
            user_data = self.api_client.get_me()
            
            self.success.emit(user_data)
            
        except Exception as e:
            self.error.emit(str(e))  

class LoginWindow(QWidget):
    def __init__(self, api_client):
        super().__init__()
        
        self.api_client = api_client
        self.main_window = None
        self.worker = None
        
        self.setWindowTitle("MemeCam - Login")
        self.resize(400, 200)
        
        self.layout = QVBoxLayout()
        
        self.title_label = QLabel("Login no MemeCam")
      
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Digite seu username ou email")
      
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.handle_login)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.login_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        
        self.setLayout(self.layout)
        
    def handle_login(self):
        login_value = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not login_value or not password:
            QMessageBox.warning(self, "Atenção", "Preencha login e senha")
            return
        
        self.login_button.setEnabled(False)
        self.login_button.setText("Entrando...")
        
        self.worker = LoginWorker(self.api_client, login_value, password)
        
        self.worker.success.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        
        self.worker.start()
        
        
    def on_login_success(self, user_data):
        self.main_window = MainWindow(self.api_client, user_data)
        self.main_window.show()
        QTimer.singleShot(100, self.close)
        
        
    def on_login_error(self, error_message):
        QMessageBox.critical(self, "Erro no login", error_message)
        
        self.login_button.setEnabled(True)
        self.login_button.setText("Entrar") 
            