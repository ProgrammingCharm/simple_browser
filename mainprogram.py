import sys
from PyQt5.QWidgets import QApplication, QMainWindow, QLineEdit, QTextEdit, QVBoxLayout, QWidget

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser")
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Creates a Vertical Box layout
        layout = QVBoxLayout(central_widget)
        # Create an Address Bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter a URL and then press Enter...")
        layout.addWidget(self.address_bar)
        # Create a Display Area
        self.display_area = QTextExit()
        self.display_area.setReadOnly(True)
        layout.addWidget(self.display_area)
        self.address_bar.returnPressed.connect(self.load_url)
    # When "Enter" is pressed, call the load_url() function.
    def load_url(self):
        url = self.address_bar.Text()
        self.display_area.setText(f"Loading URL: {url}\n(Not yet implemented)")

# Initialize the browser and run the application
__main__ = '__name__':
    app = QApplication(sys.argv)
browser = SimpleBrowser()
browser.show()
sys.exit(app.exec_())

        
