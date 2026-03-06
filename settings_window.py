from operator import index
from Imports import get_Utils
Utils = get_Utils()
from Imports import (QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QMessageBox, QPushButton, QHBoxLayout,
QComboBox, Qt, QEvent, QFont, QMouseEvent, json, QLineEdit, QApplication, QProgressDialog, QPoint, QRect,
QObject, pyqtSignal, QTimer, sys, os, subprocess, time, QIcon, QPropertyAnimation, QEasingCurve,  QAction, QIcon)
from rpi_autodiscovery import RPiAutoDiscovery, RPiConnectionWizard

class DetectionWorker(QObject):
    """Emits signals for thread-safe UI updates"""
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, detect_func):
        super().__init__()
        self.detect_func = detect_func
    
    def run(self):
        """Run in background thread"""
        try:
            result = self.detect_func()
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MaxWidthComboBox(QComboBox):
    def __init__(self, parent=None, max_popup_width="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._max_popup_width = max_popup_width
        self.setStyleSheet("""
            QComboBox::drop-down { width: 0px; border: none; }
            QComboBox::down-arrow { width: 0px; image: none; }
        """)

    def showPopup(self):
        super().showPopup()

        view = self.view()
        popup = view.parentWidget()   # usually the QFrame that draws the background
        # 2) Apply to view (for text)
        view.setFixedWidth(self._max_popup_width)

        # 3) Apply to popup frame (for background)
        if popup is not None:
            geo = popup.geometry()
            geo.setWidth(self._max_popup_width)
            popup.setGeometry(geo)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Open dropdown if clicked anywhere on the widget"""
        if self.rect().contains(event.pos()):
            self.showPopup()
        else:
            super().mousePressEvent(event)

#MARK: - Device Settings Window
class DeviceSettingsWindow(QDialog):
    _instance = None

    reload_requested = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__()
        self.parent_canvas = parent
        self.is_hidden = True
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate

        self.models = {
            "RPI pico/pico W": {"name": "RPI pico/pico W", "index": 0},
            "RPI zero/zero W": {"name": "RPI zero/zero W", "index": 1},
            "RPI 2 zero W": {"name": "RPI 2 zero W", "index": 2},
            "RPI 1 Model B/B+": {"name": "RPI 1 Model B/B+", "index": 3},
            "RPI 2 Model B": {"name": "RPI 2 Model B", "index": 4},
            "RPI 3 Model B/B+": {"name": "RPI 3 Model B/B+", "index": 5},
            "RPI 4 Model B": {"name": "RPI 4 Model B", "index": 6},
            "RPI 5": {"name": "RPI 5", "index": 7}
        }

        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent=None):
        """Get or create singleton instance"""
        if cls._instance is not None:
            try:
                _ = cls._instance.isVisible()
                if not cls._instance.is_hidden:
                    return cls._instance
            except RuntimeError:
                cls._instance = None
            
            except Exception as e:
                print(f"Error accessing existing DeviceSettingsWindow instance: {e}")
                cls._instance = None
        
        if cls._instance is None:
            cls._instance = cls(parent=parent)
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(self.t("setting_window.title"))
        self.setWindowIcon(QIcon('resources/images/APPicon.ico'))
        self.resize(400, 300)
        self.setWindowFlags(Qt.WindowType.Window)
    
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QTabWidget::pane {
                border: 1px solid #3A3A3A;
                background-color: #2B2B2B;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #1F1F1F;
                color: #FFFFFF;
                padding: 8px 20px;
                border: 1px solid #3A3A3A;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1F538D;
            }
            QTabBar::tab:hover {
                background-color: #2667B3;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #1F538D;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.create_basic_tab()
        self.create_rpi_settings_section()
    
    #MARK: - Basic Settings Tab
    def create_basic_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(5)

        title = QLabel(self.t("setting_window.basic_settings_tab.title"))
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        language_label = QLabel(self.t("setting_window.basic_settings_tab.select_language"))

        self.language_combo = MaxWidthComboBox(self, max_popup_width=358)

        theme_label = QLabel(self.t("setting_window.basic_settings_tab.select_theme"))

        self.theme_combo = MaxWidthComboBox(self, max_popup_width=358)
        self.theme_combo.addItem(self.t("setting_window.basic_settings_tab.light"), "light")
        self.theme_combo.addItem(self.t("setting_window.basic_settings_tab.datk"), 'dark')

        size_label = QLabel(self.t("setting_window.basic_settings_tab.ui_scale"))

        self.size_combo = MaxWidthComboBox(self, max_popup_width=358)
        self.size_combo.addItem(self.t("setting_window.basic_settings_tab.small"), 'small')
        self.size_combo.addItem(self.t("setting_window.basic_settings_tab.medium"), 'medium')
        self.size_combo.addItem(self.t("setting_window.basic_settings_tab.large"), 'large')

        reload_ui_btn = QPushButton(self.t("setting_window.basic_settings_tab.reload_ui"))

        languages = self.translation_manager.get_available_languages()
        for lang_code, name in languages.items():
            self.language_combo.addItem(name, lang_code)

        current_lang = Utils.app_settings.language
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        current_theme = Utils.app_settings.theme if hasattr(Utils.app_settings, 'theme') else 'dark'
        theme_index = 0 if current_theme == 'light' else 1
        self.theme_combo.setCurrentIndex(theme_index)

        current_size = Utils.app_settings.ui_scale if hasattr(Utils.app_settings, 'ui_scale') else 'medium'
        size_index = {'small': 0, 'medium': 1, 'large': 2}.get(current_size, 1)
        self.size_combo.setCurrentIndex(size_index)

        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.size_combo.currentIndexChanged.connect(self.on_size_changed)
        reload_ui_btn.clicked.connect(lambda: self.reload_requested.emit(True))
        tab_layout.addWidget(title)
        tab_layout.addSpacing(10)
        tab_layout.addWidget(language_label)
        tab_layout.addWidget(self.language_combo)
        tab_layout.addWidget(theme_label)
        tab_layout.addWidget(self.theme_combo)
        tab_layout.addWidget(size_label)
        tab_layout.addWidget(self.size_combo)
        tab_layout.addWidget(reload_ui_btn)
        tab_layout.addStretch()
        self.tab_widget.addTab(tab, self.t("setting_window.basic_settings_tab.title"))
    
    #MARK: - RPI Settings Tab
    def create_rpi_settings_section(self):
        """Create RPI connection settings group"""
        tab = QWidget()
        self.main_layout = QVBoxLayout(tab)
        # Title
        rpi_title = QLabel(self.t("setting_window.rpi_settings_tab.title"))
        rpi_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.main_layout.addWidget(rpi_title)

        self.rpi_model_combo = MaxWidthComboBox(self, max_popup_width=358)
        self.rpi_model_combo.addItems([model["name"] for model in self.models.values()])
        self.rpi_model_combo.setCurrentIndex(Utils.app_settings.rpi_model_index if hasattr(Utils.app_settings, 'rpi_model_index') else 0)
        self.rpi_model_combo.currentIndexChanged.connect(self.on_model_changed)
        self.main_layout.addWidget(self.rpi_model_combo)

        if self.rpi_model_combo.currentIndex != 0:
            # Auto-Detect Button
            self.auto_detect_btn = QPushButton(self.t("setting_window.rpi_settings_tab.auto_detect"))
            self.auto_detect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1F538D;
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2667B3;
                }
            """)
            self.auto_detect_btn.clicked.connect(self.auto_detect_rpi)
            self.main_layout.addWidget(self.auto_detect_btn)
        
        # Status label
        self.rpi_status_label = QLabel(self.t("setting_window.rpi_settings_tab.status_not_connected"))
        self.rpi_status_label.setStyleSheet("color: #FF9800; font-size: 10px;")
        self.main_layout.addWidget(self.rpi_status_label)
        
        # Manual settings (fallback)
        manual_label = QLabel(self.t("setting_window.rpi_settings_tab.manual_entry"))
        manual_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.main_layout.addWidget(manual_label)
        
        # Host input
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel(self.t("setting_window.rpi_settings_tab.rpi_host")))
        self.rpi_host_input = QLineEdit()
        self.rpi_host_input.setText(Utils.app_settings.rpi_host)
        self.rpi_host_input.setPlaceholderText(self.t("setting_window.rpi_settings_tab.rpi_host_placeholder"))
        host_layout.addWidget(self.rpi_host_input)
        self.main_layout.addLayout(host_layout)
        
        # Username input
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel(self.t("setting_window.rpi_settings_tab.rpi_user")))
        self.rpi_user_input = QLineEdit()
        self.rpi_user_input.setText(Utils.app_settings.rpi_user)
        self.rpi_user_input.setPlaceholderText(self.t("setting_window.rpi_settings_tab.rpi_user_placeholder"))
        user_layout.addWidget(self.rpi_user_input)
        self.main_layout.addLayout(user_layout)
        
        # Password input
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel(self.t("setting_window.rpi_settings_tab.rpi_password")))
        self.rpi_password_input = QLineEdit()
        self.rpi_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.rpi_password_input.setText(Utils.app_settings.rpi_password)
        self.rpi_password_input.setPlaceholderText(self.t("setting_window.rpi_settings_tab.rpi_password_placeholder"))
        self.toggle_password_action = QAction(QIcon('resources/images/Settings/eye_closed_icon.png'), self.t("setting_window.rpi_settings_tab.toggle_password"), self)
        
        self.rpi_password_input.addAction(self.toggle_password_action, QLineEdit.ActionPosition.TrailingPosition)

        pwd_layout.addWidget(self.rpi_password_input)

        self.rpi_host_input.textChanged.connect(lambda text: self.save_settings())
        self.rpi_user_input.textChanged.connect(lambda text: self.save_settings())
        self.rpi_password_input.textChanged.connect(lambda text: self.save_settings())
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)

        self.main_layout.addLayout(pwd_layout)
        self.tab_widget.addTab(tab, self.t("setting_window.rpi_settings_tab.title"))
    
    #MARK: - Settings Methods
    def on_model_changed(self, index):
        """Handle model change"""
        Utils.app_settings.rpi_model = self.rpi_model_combo.itemText(index)
        Utils.app_settings.rpi_model_index = index

        self.save_settings()
    
        if index == 0:
            # Hide auto-detect if "Pico" is selected
            if hasattr(self, 'auto_detect_btn'):
                self.auto_detect_btn.hide()
        else:
            # Show auto-detect for other models
            if hasattr(self, 'auto_detect_btn'):
                self.auto_detect_btn.show()
        #print(f"Model changed to: {Utils.app_settings.rpi_model}")

    def toggle_password_visibility(self):
        print("Toggling password visibility")
        print(f"Current echo mode: {self.rpi_password_input.echoMode()}")
        if self.rpi_password_input.echoMode() == QLineEdit.EchoMode.Password:
            print("Showing password")
            self.rpi_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_action.setIcon(QIcon("resources/images/Settings/eye_open_icon.png"))
        else:
            print("Hiding password")
            self.rpi_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_action.setIcon(QIcon("resources/images/Settings/eye_closed_icon.png"))

    def save_settings(self):
        
        filename = os.path.join(Utils.get_base_path(), 'app_settings.json')

        app_settings_dict = self.build_save_data()

        print("Saving settings:", app_settings_dict)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(app_settings_dict, f, indent=2)
        
        print("Settings saved.")

    def build_save_data(self):

        print(f"Theme {self.theme_combo.currentData()} selected, scale {self.size_combo.currentData()}")
        data = {
            'rpi_model': self.rpi_model_combo.currentText(),
            'rpi_model_index': self.rpi_model_combo.currentIndex(),
            'rpi_host': self.rpi_host_input.text(),
            'rpi_user': self.rpi_user_input.text(),
            'rpi_password': self.rpi_password_input.text(),
            'language': self.language_combo.currentData(),
            'theme': self.theme_combo.currentData(),
            'ui_scale': self.size_combo.currentData()
        }

        Utils.app_settings.rpi_model = data['rpi_model']
        Utils.app_settings.rpi_model_index = data['rpi_model_index']
        Utils.app_settings.rpi_host = data['rpi_host']
        Utils.app_settings.rpi_user = data['rpi_user']
        Utils.app_settings.rpi_password = data['rpi_password']
        Utils.app_settings.language = data['language']
        Utils.app_settings.theme = data['theme']
        Utils.app_settings.ui_scale = data['ui_scale']
        return data

    def on_language_changed(self):
        lang_code = self.language_combo.currentData()
        self.translation_manager.set_language(lang_code)
        Utils.app_settings.language = lang_code
        self.save_settings()
    
    def on_theme_changed(self):
        theme = 'light' if self.theme_combo.currentIndex() == 0 else 'dark'
        Utils.app_settings.theme = theme
        print(f"Theme changed to: {theme}, current data {self.theme_combo.currentData()}")
        self.save_settings()

    def on_size_changed(self):
        size = {0: 'small', 1: 'medium', 2: 'large'}.get(self.size_combo.currentIndex(), 'medium')
        Utils.app_settings.ui_scale = size
        print(f"UI scale changed to: {size}, current data {self.size_combo.currentData()}")
        self.save_settings()

    def auto_detect_rpi(self):
        """Auto-detect Raspberry Pi on network"""
        #print("🔍 Starting auto-detection...")
        self.lower()
        self.process = QProgressDialog(self.t("setting_window.auto_detect_dialog.process"), self.t("setting_window.auto_detect_dialog.cancel"), 0, 0, self)
        self.process.setWindowModality(Qt.WindowModality.WindowModal)
        self.process.show()
        
        try:
            def detect():
                result = RPiConnectionWizard.auto_detect_rpi()
                #print("🔍 Auto-detection result:", result)
                return result
            
            # Create worker
            self.worker = DetectionWorker(detect)
            
            # Connect signals to slots (these run on main thread!)
            self.worker.result_ready.connect(self._on_detection_success)
            self.worker.error_occurred.connect(self._on_detection_error)
            
            # Create thread
            import threading
            thread = threading.Thread(target=self.worker.run, daemon=True)
            thread.start()
            
            #print("Starting auto-detection thread...")
        
        except Exception as e:
            print(f"❌ Error starting thread: {e}")
            self.process.cancel()
            self.lower()
            QMessageBox.critical(
                self,
                self.t("setting_window.auto_detect_dialog.detection_error_title"),
                self.t("setting_window.auto_detect_dialog.detection_error_message"),
                QMessageBox.StandardButton.Ok
            )
            self.raise_()


    def _on_detection_success(self, result):
        """SLOT - Called on main thread when detection succeeds"""
        #print("🔍 Detection completed on main thread")
        
        try:
            # Validate result
            if result is None:
                #print("No Raspberry Pi found")
                self.rpi_status_label.setText(self.t("setting_window.rpi_settings_tab.status_not_detected"))
                self.rpi_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
                self.lower()
                self.process.cancel()
                QMessageBox.warning(
                    self, self.t("setting_window.auto_detect_dialog.fail_title"),
                    self.t("setting_window.auto_detect_dialog.fail_message"),
                    QMessageBox.StandardButton.Ok
                )
                self.raise_()
                return
            
            # Validate result is a dict
            if not isinstance(result, dict):
                #print(f"Invalid result type: {type(result)}")
                self._on_detection_error(self.t("setting_window.auto_detect_dialog.invalid_result"))
                return
            
            if 'ip' not in result or 'hostname' not in result:
                #print("❌ Result missing required keys")
                self.rpi_status_label.setText(self.t("setting_window.rpi_settings_tab.status_incomplete"))
                self.rpi_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
                self.lower()
                self.process.cancel()
                QMessageBox.critical(
                    self,
                    self.t("setting_window.auto_detect_dialog.incomplete_error_title"),
                    self.t("setting_window.auto_detect_dialog.incomplete_error_message"),
                    QMessageBox.StandardButton.Ok
                )
                self.raise_()
                return
            
            # Extract values
            ip = str(result.get('ip', ''))
            hostname = str(result.get('hostname', self.t("setting_window.rpi_settings_tab.unknown_hostname")))
            username = str(result.get('username', 'pi'))
            password = str(result.get('password', ''))
            model = str(result.get('model', self.t("setting_window.rpi_settings_tab.unknown_model")))
            

            model.strip()  # Remove whitespace
            print(f"Raw model from detection: '{model}'")
            model = model.replace("Raspberry Pi", "RPI")  # Normalize name
            print(f"Normalized model: '{model}'")
            model = model.split("with")[0].strip()  # Remove "with Raspbian" suffix if present
            print(f"Model after removing OS suffix: '{model}'")
            model = model.split("Rev")[0].strip()  # Remove "Rev 1.2" suffix if present
            print(f"Detected model: {model}")
            if model in self.models.keys():
                self.rpi_model_combo.setCurrentIndex(self.models[model]["index"])
            else:
                print(f"Unknown model detected: {model}")          


            #print(f"✓ Got valid result - IP: {ip}, User: {username}")
            
            # Block signals and update UI
            self.rpi_host_input.blockSignals(True)
            self.rpi_user_input.blockSignals(True)
            self.rpi_password_input.blockSignals(True)
            
            self.rpi_host_input.setText(ip)
            self.rpi_user_input.setText(username)
            self.rpi_password_input.setText(password)
            
            self.rpi_host_input.blockSignals(False)
            self.rpi_user_input.blockSignals(False)
            self.rpi_password_input.blockSignals(False)
            
            #print("✓ Updated UI fields")
            
            # Update settings
            Utils.app_settings.rpi_host = ip
            Utils.app_settings.rpi_user = username
            Utils.app_settings.rpi_password = password
            Utils.app_settings.rpi_model_name = model
            Utils.app_settings.auto_detected = True
            
            #print("✓ Updated settings")
            
            # Update status
            status_text = (self.t("setting_window.rpi_settings_tab.status_connected").format(hostname=hostname, ip=ip, model=model))
            self.rpi_status_label.setText(status_text)
            self.rpi_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
            
            #print("✓ Updated status label")
            self.process.cancel()
            # Show success message
            self.lower()
            QMessageBox.information(
                self,
                self.t("setting_window.auto_detect_dialog.success_title"),
                self.t("setting_window.auto_detect_dialog.success_message").format(hostname=hostname, ip=ip, model=model),
                QMessageBox.StandardButton.Ok
            )
            self.raise_()

            self.save_settings()
            #print("✓✓✓ Auto-detection completed successfully ✓✓✓\n")
        
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
            self._on_detection_error(str(e))


    def _on_detection_error(self, error_msg):
        """SLOT - Called on main thread when detection fails"""
        print(f"❌ Detection error: {error_msg}")
        
        self.rpi_status_label.setText(self.t("setting_window.rpi_settings_tab.status_error"))
        self.rpi_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
        
        self.lower()
        self.process.cancel()
        QMessageBox.critical(
            self,
            self.t("setting_window.auto_detect_dialog.detection_error_title"),
            self.t("setting_window.auto_detect_dialog.detection_error_message"),
            QMessageBox.StandardButton.Ok
        )
        self.raise_()

    def pulse_window(self):
        if hasattr(self, "_pulse_animation") and self._pulse_animation.state() == QPropertyAnimation.State.Running:
            return

        self._pulse_animation = QPropertyAnimation(self, b"geometry")
        self._pulse_animation.setDuration(100)
        self._pulse_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Get current geometry
        orig = self.geometry()
        
        # Calculate a larger geometry (expanding from the center)
        offset = 5  # Pixels to expand
        expanded = QRect(
            orig.x() - offset, 
            orig.y() - offset, 
            orig.width() + (offset * 2), 
            orig.height() + (offset * 2)
        )

        # Define keyframes: Start -> Expanded -> Original
        self._pulse_animation.setStartValue(orig)
        self._pulse_animation.setKeyValueAt(0.5, expanded)
        self._pulse_animation.setEndValue(orig)

        self._pulse_animation.start()

    def flash_window(self):
        original_style = self.styleSheet()
        highlight_style = original_style + "QDialog { background-color: #696969; }"
        
        def toggle_style(step):
            if step >= 8:  # 4 flashes = 8 toggles (on/off)
                self.setStyleSheet(original_style)
                return
            
            # If step is even, show highlight; if odd, show original
            if step % 2 == 0:
                self.setStyleSheet(highlight_style)
                self.pulse_window()  # Add pulse effect on highlight
            else:
                self.setStyleSheet(original_style)
            
            # Schedule the next toggle in 150ms
            QTimer.singleShot(100, lambda: toggle_style(step + 1))

        # Start the sequence
        toggle_style(0)

    def open(self):
        #print("Opening DeviceSettingsWindow")
        if self.is_hidden:
            #print("Initially hidden, showing window")
            self.is_hidden = False
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            #print("DeviceSettingsWindow already open, raising to front")
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            self.raise_()           # Brings the widget to the top of the stack
            self.activateWindow()    # Gives the window keyboard focus   
            self.flash_window()
        return self

    def reject(self):
        """Redirect Esc key (reject) to close() so closeEvent fires"""
        self.close()

    def closeEvent(self, event):
        """Handle close event"""
        self.is_hidden = True
        self.state_manager.app_state.on_settings_dialog_close()
        event.accept()