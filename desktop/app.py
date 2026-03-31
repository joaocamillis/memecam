import sys

from PySide6.QtWidgets import QApplication

from services.api_client import ApiClient
from ui.login_window import LoginWindow



def main():
    
    app = QApplication(sys.argv)
    
    api_client = ApiClient()
    window = LoginWindow(api_client)
    window.show()
    
    sys.exit(app.exec())
    
    
if __name__ == "__main__":
    main()