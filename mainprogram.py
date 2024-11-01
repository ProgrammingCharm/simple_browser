import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QProgressBar, QMessageBox, QComboBox, QDialog, QLabel)
from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QFont
import nest_asyncio
nest_asyncio.apply()
import requests
import time
import asyncio
import aiohttp 
from urllib.parse import urlparse



class SettingsDialog(QDialog):
    def __init__(self, apply_font_size_callback, current_font_size):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        # Create a dropdown for font sizes
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["10", "12", "14", "16", "18", "20"])
        self.font_size_combo.setCurrentText(str(current_font_size))  # Set the current font size
        layout.addWidget(QLabel("Select Font Size:"))
        layout.addWidget(self.font_size_combo)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_changes)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)
        self.apply_font_size_callback = apply_font_size_callback

    def apply_changes(self):
        font_size = int(self.font_size_combo.currentText())
        self.apply_font_size_callback(font_size)  # Call the callback function with the selected size
        self.close()  # Close the settings dialog


class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser")
        self.setGeometry(100, 100, 800, 600)
        self.history = [] # Track list of visited URLs
        self.current_index = -1 # Current page in history
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Creates a main layout as a Vertical Box 
        main_layout = QVBoxLayout(central_widget)

        # Create top navigation bar
        nav_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.back_button = QPushButton("Back")
        self.forward_button = QPushButton("Forward")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)
        self.progress_bar.setVisible(False)

        # Add front, back, refresh buttons and progress bar to navigation layout
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.progress_bar)

        # Add navigation layout to main layout
        main_layout.addLayout(nav_layout)

        # Create an Address Bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter a URL and then press Enter...")
        main_layout.addWidget(self.address_bar)
        
        # Help "?" button to use the Address Bar
        self.help_button = QPushButton("?")
        self.help_button.setToolTip("Click to learn how to use the address bar")
        self.help_button.clicked.connect(self.show_help_dialog)
        nav_layout.addWidget(self.help_button)
        
        # Settings button to open settings dialog
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        nav_layout.addWidget(self.settings_button)

        # Create a Display Area
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        main_layout.addWidget(self.display_area)

        # Error Toggle button for Inclusivity Heurisitic #3
        self.toggle_error_button = QPushButton("Show Details")
        self.toggle_error_button.setVisible(False)
        self.toggle_error_button.clicked.connect(self.toggle_error_details)
        main_layout.addWidget(self.toggle_error_button)

        #Initialize error_expanded attribute
        self.error_expanded = False

        # When "Enter is pressed, call load_url()
        self.address_bar.returnPressed.connect(lambda: asyncio.run(self.load_url()))
        self.refresh_button.clicked.connect(self.refresh_page)
        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)

        # Disable back and forward buttons initially
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)

    def open_settings_dialog(self):
        current_font_size = self.display_area.fontPointSize()
        settings_dialog = SettingsDialog(self.change_font_size, current_font_size)  # Pass the callback function
        settings_dialog.exec_()  # Show dialog

    def change_font_size(self, size):
        font = QFont()
        font.setPointSize(size)
        self.display_area.setFont(font)
        self.display_area.setFontPointSize(size)  # Change the font size of the display area

    async def load_url(self):
        url = self.address_bar.text().strip()
        if not self.is_valid_url(url):
            self.display_area.setText("Invalid URL.")
            return
        self.start_loading()
        await self.fetch_content(url)
        self.update_history(url)

    def show_help_dialog(self):
        QMessageBox.information(self, "Address Bar Help",
            "Use the address bar to enter a website URL (e.g., 'http://example.com') to navigate to it. "
            "Entering a valid URL can help you access content directly.")
    
    def display_error_message(self, brief_message, detailed_message):
        suggested_correction = " (e.g., 'http://example.com')"
        self.display_area.setText(brief_message + suggested_correction)
        self.toggle_error_button.setVisible(True)
        self.error_brief = brief_message
        self.error_detail = detailed_message + suggested_correction
    
    def toggle_error_details(self):
        if self.error_expanded:
            self.display_area.setText(self.error_brief)
            self.toggle_error_button.setText("Show Details")
        else:
            self.display_area.setText(self.error_brief + "\n\n" + self.error_detail)
            self.toggle_error_button.setText("Hide Details")
        self.error_expanded = not self.error_expanded
        
    
    async def fetch_content(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(url, timeout=5) as response:
                    content_size = int(response.headers.get('Content-Length', 0))
                    if content_size < 1024 * 1024:
                        elapsed_time = time.time() - start_time
                        content = await response.text()
                        self.stop_loading()
                        self.display_area.setText(content)
                        if elapsed_time <= 1.0:
                            self.display_area.append(f"\nContent loaded in {elapsed_time:.2f} seconds.")
                        else:
                            self.display_area.append(f"\nContent loaded in {elapsed_time:.2f}, exceeding 1-second goal.")
                    else: 
                        self.display_areas.setText("Page exceeds lightweight criteria (> 1 MB).")
                        self.stop_loading()
        except aiohttp.ClientError as e:
            self.display_error_message("An error occurred while fetching content", str(e))
        finally:
            self.stop_loading()

    def refresh_page(self):
        if self.current_index >= 0 and self.current_index < len(self.history):
            self.async_run(self.load_url_from_history(self.history[self.current_index]))

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.async_run(self.load_url_from_history(self.history[self.current_index]))

    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.async_run(self.load_url_from_history(self.history[self.current_index]))

    async def load_url_from_history(self, url):
        self.address_bar.setText(url)
        await self.load_url()

    # Update history
    def update_history(self, url):
        # If navigating back and then a new URL is loaded, truncate forward history
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        self.history.append(url)
        self.current_index = len(self.history) - 1

        # Update back/forward button states
        self.back_button.setEnabled(self.current_index > 0)
        self.forward_button.setEnabled(self.current_index < len(self.history) - 1)

    # Show progress bar and start loading
    def start_loading(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate state

    # Stop loading and hide progress bar
    def stop_loading(self):
        self.progress_bar.setVisible(False)
    
    # Validate the URL, prepend with https it not proper. 
    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "http://" + url
            parsed_url = urlparse(url)
        self.address_bar.setText(url)
        if parsed_url.scheme in ("http", "https") and bool(parsed_url.netloc):
            return True
        else:
            self.display_error_message(
                "Invalid URL. No personal data is shared when entering a URL.",
                "Please ensure the URL is in the correct format (e.g., 'http://example.com')."
            )
            return False
    
    @staticmethod
    def async_run(coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(coro, loop)
            else:
                loop.run_until_complete(coro)
            
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)


# Initialize the browser and run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec_())

        
