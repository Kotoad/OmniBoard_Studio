from Imports import (QThread, pyqtSignal, QSplashScreen, QPixmap, QColor, QProgressBar, QPainter, QPen, Qt, QRectF,
                     QTimer, QMessageBox, QApplication, QPalette, QObject, sys, time, QStackedWidget, QWidget,
                     json, os, threading, warnings, QProgressDialog, QMainWindow, QIcon, QVBoxLayout, QLabel,
                     QAction, QFont, QToolBar, QSize, QSizePolicy, QSlider, QShortcut, QKeySequence, QHBoxLayout,
                     QPushButton, QScrollArea, QListWidget, QSplitter, QInputDialog, QLineEdit, QUndoStack)
import urllib.request, ssl, certifi, tempfile, traceback as tb, glob, webbrowser
from Imports import (get_Utils, get_Code_Compiler, get_State_Manager, get_File_Manager, get_Data_Control, get_Translation_Manager,
                     get_Graphic_Programing_Window, get_Code_Editor_Window, get_Device_Settings_Mindow, get_Blocks_Window,
                     get_Commands)

Utils = get_Utils()
StateManager = get_State_Manager()
FileManager = get_File_Manager()
DataControl = get_Data_Control()
TranslationManager = get_Translation_Manager()
CodeCompiler = get_Code_Compiler()
CodeEditorWindow = get_Code_Editor_Window()
GraphicPrograminWindow = get_Graphic_Programing_Window()[0]
DeviceSettingsWindow = get_Device_Settings_Mindow()
BlocksWindow = get_Blocks_Window()
#MARK: - Loading Screen
class LoaderThread(QThread):
    """
    Handles heavy non-GUI initialization in the background.
    Move file reading, API calls, or config loading here.
    """
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def run(self):
        # PHASE 1: Load Settings (Example of moving logic to thread)
        self.status.emit("Loading App Settings...")
        Utils.compiler = CodeCompiler()
        Utils.state_manager = StateManager()
        Utils.file_manager = FileManager()
        Utils.data_control = DataControl()
        time.sleep(0.5) # Simulated delay (remove this in production)
        self.progress.emit(20)

        # PHASE 2: Check Resources
        self.status.emit("Checking Resources...")
        time.sleep(0.5) 
        self.progress.emit(40)

        # PHASE 3: Initialize Compiler
        self.status.emit("Initializing Compiler...")
        Utils.file_manager.load_app_settings()
        Utils.translation_manager = TranslationManager()
        time.sleep(0.5)
        self.progress.emit(60)
        
        # PHASE 4: Preparing UI
        self.status.emit("Preparing Interface...")
        time.sleep(0.5)
        self.progress.emit(80)

        # Done
        self.finished.emit()

class NativeSplash(QSplashScreen):
    def __init__(self):
        # Create a basic pixmap for the window size
        # We fill it with your app's dark background color
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#1F1F1F")) 
        super().__init__(pixmap)
        
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_spinner)
        self.timer.start(30) # Update every 30ms for smooth animation

        # UI Setup (Progress Bar)
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(20, 260, 360, 10)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #333;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #1F538D;
                border-radius: 5px;
            }
        """)
        self.progressBar.setTextVisible(False)
        self.loading_text = "Initializing..."

    def rotate_spinner(self):
        self.angle = (self.angle + 10) % 360
        self.repaint() # Force a redraw

    def paintEvent(self, event):
        # 1. Draw Background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1F1F1F"))
        
        # 2. Draw Loading Spinner
        center_x = self.width() // 2
        center_y = (self.height() // 2) - 20 # Slightly up to make room for text
        radius = 30
        
        painter.translate(center_x, center_y)
        painter.rotate(self.angle)
        
        # Draw 8 "spokes"
        for i in range(8):
            painter.rotate(45) # 360 / 8 = 45 degrees
            # Fade transparency
            opacity = int(255 * (i / 8))
            color = QColor("#1F538D") 
            color.setAlpha(opacity)
            
            pen = QPen(color)
            pen.setWidth(6)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            # Draw line segment
            painter.drawLine(radius - 10, 0, radius, 0)
            
        painter.resetTransform()
        
        # 3. Draw Text
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        
        # Draw text centered below spinner
        text_rect = QRectF(0, 220, 400, 30)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.loading_text)

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def update_status(self, text):
        self.loading_text = text
        self.repaint()
#MARK: - Update Checker
def check_for_updates():
    try:
        url = "https://www.omniboardstudio.cz/API/version.php"
        req = urllib.request.Request(url, headers={'User-Agent': 'OmniBoard-Updater'})
        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(req, timeout=5, context=context) as response:
            print(f"Update check HTTP response code: {response.status}")
            raw_response = response.read().decode()
            print(f"Raw server response: '{raw_response}'") # Look at this output to see what is breaking the parser
            data = json.loads(raw_response)
            print(f"Parsed JSON data: {data}, type: {type(data)}")
            if isinstance(data, dict):
                print(f"Latest release data: {data}")
                latest_version = data.get("tag_name", "")
                assets = data.get("assets", [])
                print(f"Latest version: {latest_version}, Assets: {assets}")
                if latest_version:
                    main_vesion, sub_version, patch_version = Utils.config['CURRENT_VERSION'].split(".")
                    latest_main, latest_sub, latest_patch = latest_version.split(".")
                    if (int(latest_main), int(latest_sub), int(latest_patch)) > (int(main_vesion), int(sub_version), int(patch_version)):
                        print("Update available!")
                        return True, latest_version, assets, "Update available"
                    else:
                        print("No update available.")
                        return False, latest_version, assets, "Up to date"
    except urllib.error.URLError as e:
        print(f"Update check failed (URL error): {e}")
        return False, None, None, "Network error"
    except Exception as e:
        print(f"Update check failed: {e}")
        #print(f"has_update = {has_update}, latest_version = {latest_version}, assets = {assets}, status = {str(e)}, current_version = {Utils.config['CURRENT_VERSION']}")
        return False, None, None, str(e)
    
    return False, None, None, "No releases found"

class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(str, list)
    up_to_date = pyqtSignal(str)
    connection_error = pyqtSignal()

    def run(self):
        has_update, version, assets, status = check_for_updates()
        print(f"Update check result: has_update={has_update}, version={version}, assets={assets}, status={status}")
        print(f"Current version: {Utils.config['CURRENT_VERSION']}")
        if status == "Network error":
            self.connection_error.emit()
        if has_update:
            self.update_available.emit(version, assets)
        elif version:
            self.up_to_date.emit(version)

class DownloadUpdateThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        temp_dir = tempfile.gettempdir()
        ext = ".exe" if sys.platform == "win32" else ".tar.gz"
        save_path = os.path.join(temp_dir, f"OmniBoard_Update{int(time.time())}{ext}")
        print(f"Downloading update to: {save_path}")
        def report(block_num, block_size, total_size):
            if total_size > 0:
                percent = int(block_num * block_size * 100 / total_size)
                self.progress.emit(min(percent, 100))

        try:
            urllib.request.urlretrieve(self.url, save_path, reporthook=report)
            self.finished.emit(save_path)
        except Exception as e:
            print(f"Download failed: {e}")

#MARK: - Universal Error Handler
class UniversalErrorHandler(QObject):
    """
    Captures:
    1. Uncaught Python Exceptions (sys.excepthook)
    2. Python Warnings (warnings.showwarning)
    3. Threading Exceptions (threading.excepthook)
    4. Qt Internal Messages (qInstallMessageHandler)
    """
    # Signal: (Title, Message, IconType)
    error_occurred = pyqtSignal(str, str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_hooks()

    def _setup_hooks(self):
        # 1. Standard Python Exceptions
        sys.excepthook = self.handle_exception

        # 2. Python Warnings
        self._original_showwarning = warnings.showwarning
        warnings.showwarning = self.handle_warning

        # 3. Threading Exceptions (Python 3.8+)
        threading.excepthook = self.handle_threading_exception

        # 4. Qt Internal Messages (Optional - can be noisy)
        # from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
        # qInstallMessageHandler(self.handle_qt_message)

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Catch standard crashes."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = "".join(tb.format_exception(exc_type, exc_value, exc_traceback))
        print(error_msg, file=sys.stderr)  # Also print to console for logging
        self.error_occurred.emit("Critical Error", error_msg, QMessageBox.Icon.Critical)

    def handle_warning(self, message, category, filename, lineno, file=None, line=None):
        """Catch warnings (e.g., DeprecationWarning)."""
        msg = f"{category.__name__}:\n{message}\n\nFile: {filename}\nLine: {lineno}"
        self.error_occurred.emit("Warning", msg, QMessageBox.Icon.Warning)
        print(f"Warning captured: {msg}", file=sys.stderr)  # Also print to console
        if self._original_showwarning:
            print("Original Warning Handler Output:")
            self._original_showwarning(message, category, filename, lineno, file, line)

    def handle_threading_exception(self, args):
        """Catch exceptions in threads that aren't joined."""
        error_msg = f"Thread: {args.thread.name}\n"
        if args.exc_type:
            error_msg += "".join(tb.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
        
        print(error_msg, file=sys.stderr)
        self.error_occurred.emit("Thread Error", error_msg, QMessageBox.Icon.Critical)

    # Optional: Handle Qt internal C++ messages
    # def handle_qt_message(self, mode, context, message):
    #     msg_type = "Info"
    #     if mode == QtMsgType.QtWarningMsg: msg_type = "Qt Warning"
    #     elif mode == QtMsgType.QtCriticalMsg: msg_type = "Qt Critical"
    #     elif mode == QtMsgType.QtFatalMsg: msg_type = "Qt Fatal"
    #     self.error_occurred.emit(msg_type, message, QMessageBox.Icon.Information)

    def show_error_dialog(self, title, body, icon):
        """Slot to show the GUI dialog. Must run on Main Thread."""
        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(f"An unexpected {title} occurred.")
        msg_box.setInformativeText("Please check the details below.")
        
        # Detailed text area (scrollable)
        msg_box.setDetailedText(body)
        
        # Allow resizing
        copy_btn = msg_box.addButton("Copy Error", QMessageBox.ButtonRole.ActionRole)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Force the detailed text to be visible/copyable nicely
        msg_box.setStyleSheet("QMessageBox { min-width: 600px; }")
        
        msg_box.exec()
        
        if msg_box.clickedButton() == copy_btn:
            clipboard = QApplication.clipboard()
            clipboard.setText(f"{title}:\n{body}")

#MARK: - Main Application Window
class HubWindow(QWidget):

    switch_widget_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.visual_programming_window = None
        self.setup_ui()

    def setup_ui(self):

        spliter = QSplitter(Qt.Orientation.Horizontal)
        spliter.setSizes([200, 400])  # Set initial sizes for the two panes
        spliter.setChildrenCollapsible(False)  # Prevent collapsing panes

        recent_projects = QScrollArea(spliter)
        recent_projects.setWidgetResizable(True)

        scroll_content = QWidget()
        recent_layout = QVBoxLayout(scroll_content)

        projects_path = Utils.get_base_path()/"projects"

        print(f"Looking for projects in: {projects_path}")
        os.makedirs(projects_path, exist_ok=True)
        print(f"Ensured projects directory exists at: {projects_path}")

        for i in projects_path.iterdir():
            print(f"Found file in projects directory: {i.name}")
            if i.is_file() and i.suffix == ".project":
                name = i.name.split(".")[0]
                project_button = QPushButton(f"Project {name}")
                project_button.setStyleSheet("text-align: left; padding: 10px;")
                recent_layout.addWidget(project_button)
                project_button.clicked.connect(lambda _, p=name: self.open_file(p))

        recent_layout.addStretch()

        recent_projects.setWidget(scroll_content)

        label = QLabel("Welcome to OmniBoard Studio!", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        spliter.addWidget(recent_projects)
        spliter.addWidget(label)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(spliter)

    def open_file(self, file_name):
        if self.visual_programming_window:
            self.visual_programming_window.on_open_specific_file(file_name)
            self.switch_widget_signal.emit(1)  # Switch to visual programming view

#MARK: - MainWindow
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.undo_stack = QUndoStack(self)

        
        self.reset_file()
        self.setup_ui()
        self.create_shortcuts()
        self.setup_auto_save_timer()

        #if getattr(sys, 'frozen', False):
        self.start_update_check()

    def setup_ui(self):
        self.setWindowTitle(self.t("main_GUI._metadata.app_title") + " " + Utils.config['CURRENT_VERSION'])
        self.setWindowIcon(QIcon('resources/images/APPicon.ico'))
        self.resize(1200, 800)

        self.create_stacked_widget()
        self.create_menu_bar()
        self.create_top_toolbar()
        self.create_bottom_toolbar()
        self.switch_widget(0)  # Start with Hub view
    
    def create_shortcuts(self):
        """Create Ctrl+S keyboard shortcut for saving"""
        #print("Creating save shortcut (Ctrl+S)")
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.on_save_file)

        open_shortcut = QShortcut(QKeySequence.StandardKey.Open, self)
        open_shortcut.activated.connect(self.on_open_file)

        new_shortcut = QShortcut(QKeySequence.StandardKey.New, self)
        new_shortcut.activated.connect(self.on_new_file)

        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.activated.connect(self.undo_stack.undo)

        redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        redo_shortcut.activated.connect(self.undo_stack.redo)

    def setup_auto_save_timer(self):
        """Setup auto-save timer for every 5 minutes"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_project)
        
        # 5 minutes = 300,000 milliseconds
        self.auto_save_timer.start(300000)  # 300000 ms = 5 minutes
        
        #print("Auto-save timer started (every 5 minutes)")

    def reset_file(self):
        try:
            if os.path.exists("File.py"):
                with open("File.py", "w") as f:
                    f.write("")
            else:
                with open("File.py", "x") as f:
                    f.write("")
        except Exception as e:
            print(f"Error resetting File.py: {e}")
        Reports_path = Utils.get_base_path()/"resources"
        try:
            with open(Reports_path/"last_report.json", "w") as f:
                f.write("")
        except Exception as e:
            print(f"Error resetting last_report.json: {e}")

    def create_stacked_widget(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.hub_widget = HubWindow()
        self.stacked_widget.addWidget(self.hub_widget)

        self.visual_programming_window = GraphicPrograminWindow(self)
        self.stacked_widget.addWidget(self.visual_programming_window)

        self.code_editor_window = CodeEditorWindow()
        self.stacked_widget.addWidget(self.code_editor_window)

        self.visual_programming_window.ensurePolished()  # Ensure it's fully initialized before connecting signals
        self.code_editor_window.ensurePolished()

        self.hub_widget.switch_widget_signal.connect(self.switch_widget)

        self.hub_widget.visual_programming_window = self.visual_programming_window

    #MARK: - UI Creation Methods
    def create_menu_bar(self):
        """Create the menu bar"""
        self.menubar = self.menuBar()
        #print(f"Menubar Height: {menubar.height()}")
        # File menu
        file_menu = self.menubar.addMenu(self.t("main_GUI.menu.file"))
        
        new_action = file_menu.addAction(self.t("main_GUI.menu.new"))
        new_action.triggered.connect(self.on_new_file)
        
        open_action = file_menu.addAction(self.t("main_GUI.menu.open"))
        open_action.triggered.connect(self.on_open_file)
        
        save_action = file_menu.addAction(self.t("main_GUI.menu.save"))
        save_action.triggered.connect(self.on_save_file)
        
        save_as_action = file_menu.addAction(self.t("main_GUI.menu.save_as"))
        save_as_action.triggered.connect(self.on_save_file_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction(self.t("main_GUI.menu.exit"))
        exit_action.triggered.connect(self.close)
        
        view_menu = self.menubar.addMenu(self.t("main_GUI.menu.view"))

        hub_window_action = view_menu.addAction(self.t("main_GUI.menu.hub"))
        hub_window_action.triggered.connect(lambda: self.switch_widget(0))

        visual_programming_window_action = view_menu.addAction(self.t("main_GUI.menu.visual_editor"))
        visual_programming_window_action.triggered.connect(lambda: self.switch_widget(1))

        code_editor_window_action = view_menu.addAction(self.t("main_GUI.menu.code_editor"))
        code_editor_window_action.triggered.connect(lambda: self.switch_widget(2))

        # blocks menu
        blocks_menu = self.menubar.addMenu(self.t("main_GUI.menu.blocks"))
        
        add_element = blocks_menu.addAction(self.t("main_GUI.menu.add_block"))
        add_element.triggered.connect(self.open_blocks_window)
        
        settings_menu = self.menubar.addMenu(self.t("main_GUI.menu.settings"))
        settings_menu_action = settings_menu.addAction(self.t("main_GUI.menu.settings"))
        settings_menu_action.triggered.connect(self.open_settings_window)
        
        Help_menu = self.menubar.addMenu(self.t("main_GUI.menu.help"))
        
        Get_stared = Help_menu.addAction(self.t("main_GUI.menu.get_started"))
        Get_stared.triggered.connect(lambda: self.open_help_window(0))
        
        tutorials = Help_menu.addAction(self.t("main_GUI.menu.tutorials"))
        tutorials.triggered.connect(lambda: self.open_help_window(1))
        
        FAQ = Help_menu.addAction(self.t("main_GUI.menu.faq"))
        FAQ.triggered.connect(lambda: self.open_help_window(2))
        
        # Compile menu
        compile_menu = self.menubar.addMenu(self.t("main_GUI.menu.compile"))
        
        compile_action = compile_menu.addAction(self.t("main_GUI.menu.compile_code"))
        compile_action.triggered.connect(self.compile_and_upload)
    
    def create_top_toolbar(self):

        icon_path = "resources/images/Tool_bar/"

        toolbar = QToolBar(self.t("main_GUI.top_toolbar.toolbar"))
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        
        if Utils.app_settings.theme == 'light':
            save_icon = QAction(QIcon(icon_path+"Save_black.png"), self.t("main_GUI.top_toolbar.save"), self)
        else:
            save_icon = QAction(QIcon(icon_path+"Save.png"), self.t("main_GUI.top_toolbar.save"), self)
        save_icon.triggered.connect(self.on_save_file)
        toolbar.addAction(save_icon)

        if Utils.app_settings.theme == 'light':
            open_icon = QAction(QIcon(icon_path+"Open_file_black.png"), self.t("main_GUI.top_toolbar.open"), self)
        else:
            open_icon = QAction(QIcon(icon_path+"Open_file.png"), self.t("main_GUI.top_toolbar.open"), self)
        open_icon.triggered.connect(self.on_open_file)
        toolbar.addAction(open_icon)

        if Utils.app_settings.theme == 'light':
            new_icon = QAction(QIcon(icon_path+"New_file_black.png"), self.t("main_GUI.top_toolbar.new"), self)
        else:
            new_icon = QAction(QIcon(icon_path+"New_file.png"), self.t("main_GUI.top_toolbar.new"), self)
        new_icon.triggered.connect(self.on_new_file)
        toolbar.addAction(new_icon)

        toolbar.addSeparator()

        if Utils.app_settings.theme == 'light':
            add_block_icon = QAction(QIcon(icon_path+"Add_block_black.png"), self.t("main_GUI.top_toolbar.add_block"), self)
        else:
            add_block_icon = QAction(QIcon(icon_path+"Add_block.png"), self.t("main_GUI.top_toolbar.add_block"), self)
        add_block_icon.triggered.connect(self.open_blocks_window)
        toolbar.addAction(add_block_icon)

        toolbar.addSeparator()

        if Utils.app_settings.theme == 'light':             
            settings_icon = QAction(QIcon(icon_path+"Settings_black.png"), self.t("main_GUI.top_toolbar.settings"), self)
        else:
            settings_icon = QAction(QIcon(icon_path+"Settings.png"), self.t("main_GUI.top_toolbar.settings"), self)
        settings_icon.triggered.connect(self.open_settings_window)
        toolbar.addAction(settings_icon)

        toolbar.addSeparator()

        if Utils.app_settings.theme == 'light':
            run_and_compile_icon = QAction(QIcon(icon_path+"Run_and_compile_black.png"), self.t("main_GUI.top_toolbar.compile_upload"), self)
        else:
            run_and_compile_icon = QAction(QIcon(icon_path+"Run_and_compile.png"), self.t("main_GUI.top_toolbar.compile_upload"), self)
        run_and_compile_icon.triggered.connect(self.compile_and_upload)
        toolbar.addAction(run_and_compile_icon)

        if Utils.app_settings.theme == 'light':
            run_icon = QAction(QIcon(icon_path+"Run_black.png"), self.t("main_GUI.top_toolbar.run"), self)
        else:
            run_icon = QAction(QIcon(icon_path+"Run.png"), self.t("main_GUI.top_toolbar.run"), self)
        run_icon.triggered.connect(self.execute_on_rpi_ssh_background)
        toolbar.addAction(run_icon)

        if Utils.app_settings.theme == 'light':
            stop_execution_icon = QAction(QIcon(icon_path+"Stop_execution_black.png"), self.t("main_GUI.top_toolbar.stop"), self)
        else:
            stop_execution_icon = QAction(QIcon(icon_path+"Stop_execution.png"), self.t("main_GUI.top_toolbar.stop"), self)
        stop_execution_icon.triggered.connect(self.stop_execution)
        toolbar.addAction(stop_execution_icon)

        toolbar.addSeparator()

        if Utils.app_settings.theme == 'light':
            to_hub_icon = QAction(QIcon(icon_path+"To_Hub_black.png"), self.t("main_GUI.top_toolbar.hub"), self)
        else:
            to_hub_icon = QAction(QIcon(icon_path+"To_Hub.png"), self.t("main_GUI.top_toolbar.hub"), self)
        to_hub_icon.triggered.connect(lambda: self.switch_widget(0))
        toolbar.addAction(to_hub_icon)

        if Utils.app_settings.theme == 'light':
            to_GUI_icon = QAction(QIcon(icon_path+"To_GUI_black.png"), self.t("main_GUI.top_toolbar.visual_editor"), self)
        else:
            to_GUI_icon = QAction(QIcon(icon_path+"To_GUI.png"), self.t("main_GUI.top_toolbar.visual_editor"), self)
        to_GUI_icon.triggered.connect(lambda: self.switch_widget(1))
        toolbar.addAction(to_GUI_icon)

        if Utils.app_settings.theme == 'light':
            to_code_editor_icon = QAction(QIcon(icon_path+"To_code_editor_black.png"), self.t("main_GUI.top_toolbar.code_editor"), self)
        else:
            to_code_editor_icon = QAction(QIcon(icon_path+"To_code_editor.png"), self.t("main_GUI.top_toolbar.code_editor"), self)
        to_code_editor_icon.triggered.connect(lambda: self.switch_widget(2))
        toolbar.addAction(to_code_editor_icon)

        #test_icon = QAction(QIcon(icon_path+"Test.png"), self.t("main_GUI.toolbar.test"), self)
        #test_icon.triggered.connect(self.simulate_pinch)
        #toolbar.addAction(test_icon)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.top_toolbar = toolbar

    def create_bottom_toolbar(self):

        toolbar = QToolBar(self.t("main_GUI.bottom_toolbar.toolbar"))
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        font = QFont("Consolas", 16)
        font.setBold(True)

        spacer = QWidget()

        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if Utils.app_settings.theme == 'light':
            self.pan_button = QAction(QIcon("resources/images/Tool_bar/Hand_black.png"), self.t("main_GUI.bottom_toolbar.pan"), self)
        else:
            self.pan_button = QAction(QIcon("resources/images/Tool_bar/Hand.png"), self.t("main_GUI.bottom_toolbar.pan"), self)
        self.pan_button.setCheckable(True)
        self.pan_button.toggled.connect(lambda checked: self.toggle_pan_mode(checked))

        minus_label = QLabel("-")

        minus_label.setFont(font)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        #zoom_slider.setSpecificTicks([50, 100, 200])

        self.zoom_slider.valueChanged.connect(lambda value: self.zoom_changed(value))

        plus_label = QLabel("+")

        plus_label.setFont(font)

        toolbar.addWidget(spacer)
        toolbar.addAction(self.pan_button)
        toolbar.addWidget(minus_label)
        toolbar.addWidget(self.zoom_slider)
        toolbar.addWidget(plus_label)

        
        self.visual_programming_window.zoom_slider = self.zoom_slider  # Pass reference to visual programming window for sync

        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, toolbar)
        self.bottom_toolbar = toolbar

    def switch_widget(self, index):
        if index == 1:
            self.zoom_slider.setEnabled(True)
            self.pan_button.setEnabled(True)
        else:
            self.zoom_slider.setEnabled(False)
            self.pan_button.setEnabled(False)
        self.stacked_widget.setCurrentIndex(index)

    def zoom_changed(self, value):
        if self.stacked_widget.currentWidget() == self.visual_programming_window:
            self.visual_programming_window.current_canvas.zoom_change(value)

    def on_new_file(self):
        # Placeholder for new file logic
        print("New file action triggered")
        has_content = (
                len(Utils.main_canvas.get("blocks", {})) > 0 or
                len(Utils.functions) > 0 or
                len(Utils.variables.get("main_canvas", {})) > 0 or
                len(Utils.devices.get("main_canvas", {})) > 0
            )
        projects = Utils.file_manager.list_projects()
        items = [p['name'] for p in projects]
        if Utils.config['opend_project'] is not None and has_content is False:
            self.visual_programming_window.on_new_file()
        elif has_content and Utils.config['opend_project'] is not None and Utils.config['opend_project'] not in items:
            text, ok = QInputDialog.getText(
                self,
                self.t("main_GUI.dialogs.file_dialogs.save_project_as"), 
                self.t("main_GUI.dialogs.file_dialogs.enter_project_name"),
                QLineEdit.EchoMode.Normal, 
                Utils.project_data.metadata.get('name', ''))
        
            if ok and text:
                Utils.project_data.metadata['name'] = text
                if Utils.file_manager.save_project(text):
                    print(f"Project saved as '{text}'")
                    self.visual_programming_window.on_new_file()  # Clear current project after saving
            elif not ok:
                print("New file action cancelled by user")
                self.visual_programming_window.on_new_file()  # Clear current project without saving
        elif has_content and Utils.config['opend_project'] is not None and Utils.config['opend_project'] in items:
            reply = QMessageBox.question(
                self, self.t("main_GUI.dialogs.file_dialogs.confirm_new_title"),
                self.t("main_GUI.dialogs.file_dialogs.confirm_new_message"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.visual_programming_window.on_new_file()
            else:
                print("New file action cancelled by user")
        elif has_content and Utils.config['opend_project'] is None:
            text, ok = QInputDialog.getText(
                self,
                self.t("main_GUI.dialogs.file_dialogs.save_project_as"), 
                self.t("main_GUI.dialogs.file_dialogs.enter_project_name"),
                QLineEdit.EchoMode.Normal, 
                Utils.project_data.metadata.get('name', ''))
        
            if ok and text:
                Utils.project_data.metadata['name'] = text
                if Utils.file_manager.save_project(text):
                    print(f"Project saved as '{text}'")
                    self.visual_programming_window.on_new_file()  # Clear current project after saving
            elif not ok:
                print("New file action cancelled by user")
                self.visual_programming_window.on_new_file()  # Clear current project without saving
        self.switch_widget(1)  # Switch back to Visual Programming for now
        

    def on_open_file(self):
        # Placeholder for open file logic
        print("Open file action triggered")
        self.switch_widget(1)  # Switch back to Visual Programming for now
        self.visual_programming_window.on_open_file()

    def on_save_file(self):
        # Placeholder for save file logic
        print("Save file action triggered")
        if self.stacked_widget.currentWidget() == self.visual_programming_window:
            self.visual_programming_window.on_save_file()
        # Implement save logic here
    
    def on_save_file_as(self):
        # Placeholder for save as logic
        print("Save As action triggered")
        if self.stacked_widget.currentWidget() == self.visual_programming_window:
            self.visual_programming_window.on_save_file_as()
        # Implement save as logic here
    
    def open_blocks_window(self):
        """Open the blocks window"""
        #print("Opening blocks window")
        if self.stacked_widget.currentWidget() == self.visual_programming_window:
            blocks_window = BlocksWindow.get_instance(parent=self.visual_programming_window.current_canvas)
            print("blocks window instance:", blocks_window)
            try:
                print("Checking if blocks dialog can be opened...")
                if Utils.state_manager.app_state.on_blocks_dialog_open():
                    print("Opening blocks dialog...")
                    blocks_window.open()
            except Exception as e:
                print(f"Error opening blocks window: {e}")

    def open_help_window(self, which):
        """Open the help window"""
        urls = {
            0: "https://www.omniboardstudio.cz",
            1: "https://www.omniboardstudio.cz/Tutorials.php",
            2: "https://www.omniboardstudio.cz/FAQ.php"
        }

        url = urls.get(which, "https://www.omniboardstudio.cz")
        print(f"Opening help URL: {url}")
        webbrowser.open(url)    
    
    def open_settings_window(self):
        """Open the device settings window"""
        settings_window = DeviceSettingsWindow.get_instance(parent=self)
        settings_window.reload_requested.connect(self.on_reload_reqested)
        if Utils.state_manager.app_state.on_settings_dialog_open():
            settings_window.open()

    def compile_and_upload(self):
        # Placeholder for compile and upload logic
        print("Compile and Upload action triggered")
        self.visual_programming_window.compile_and_upload()
        # Implement compile and upload logic here

    def execute_on_rpi_ssh_background(self):
        # Placeholder for SSH execution logic
        print("Execute on Raspberry Pi via SSH action triggered")
        if Utils.app_settings.rpi_model_index != 0:
            self.visual_programming_window.execute_on_rpi_ssh_background()
        # Implement SSH execution logic here   

    def stop_execution(self):
        # Placeholder for stopping execution logic
        print("Stop Execution action triggered")
        self.visual_programming_window.stop_execution()
        # Implement logic to stop execution on Raspberry Pi here 

    def toggle_pan_mode(self, checked):
        if self.stacked_widget.currentWidget() == self.visual_programming_window:
            print(f"Pan mode toggled: {'ON' if checked else 'OFF'}")
            self.setCursor(Qt.CursorShape.OpenHandCursor if checked else Qt.CursorShape.ArrowCursor)
            if Utils.app_settings.theme == 'light':
                self.pan_button.setIcon(QIcon("resources/images/Tool_bar/Cursor_black.png") if checked else QIcon("resources/images/Tool_bar/Hand_black.png"))
            else:
                self.pan_button.setIcon(QIcon("resources/images/Tool_bar/Cursor.png") if checked else QIcon("resources/images/Tool_bar/Hand.png"))
            self.visual_programming_window.setCursor(Qt.CursorShape.OpenHandCursor if checked else Qt.CursorShape.ArrowCursor)
            self.visual_programming_window.current_canvas.setCursor(Qt.CursorShape.OpenHandCursor if checked else Qt.CursorShape.ArrowCursor)
            self.visual_programming_window.current_canvas.pan_mode = checked
            print(f"Pan mode on canvas {self.visual_programming_window.current_canvas} set to: {self.visual_programming_window.current_canvas.pan_mode}")

    def keyPressEvent(self, event):
        print(f"[MainWindow] Key Pressed: {event.key()} (Text: '{event.text()}')")
        if event.key() == Qt.Key.Key_F1:
            print("F1 pressed - opening help window")
            self.open_help_window(0)  # Open "Get Started" tab
        elif event.key() == Qt.Key.Key_Escape:
            print("Escape pressed - toggling pan mode")
            if self.visual_programming_window.current_canvas.pan_mode:
                self.pan_button.setChecked(False)  # This will toggle pan mode off
        else:
            super().keyPressEvent(event)  # Ensure other key events are processed normally

    def on_reload_reqested(self, reqested):
        if reqested:
            self.reload_ui_language()

    def reload_ui_language(self):
        
        self.auto_save_project()

        self.setWindowTitle(self.t("main_GUI._metadata.app_title"))

        self.menubar.clear()
        self.create_menu_bar()

        if hasattr(self, 'top_toolbar'):
            self.removeToolBar(self.top_toolbar)
            self.top_toolbar.deleteLater()
            del self.top_toolbar
        if hasattr(self, 'bottom_toolbar'):
            self.removeToolBar(self.bottom_toolbar)
            self.bottom_toolbar.deleteLater()
            del self.bottom_toolbar
        self.create_top_toolbar()
        self.create_bottom_toolbar()

        self.visual_programming_window.wipe_canvas()

        self.visual_programming_window.open_project()

    def auto_save_project(self):
        """Auto-save current project"""
        name = Utils.project_data.metadata.get('name', 'Untitled')
        print(f"Auto-saving project '{name}'")
        Utils.config['opend_project'] = name
        try:
            if Utils.file_manager.save_project(name, is_autosave=True):
                print(f"Auto-saved '{name}' at {self.get_current_time()}")
                pass
            else:
                print(f" Auto-save failed for '{name}'")
        except Exception as e:
            print(f" Auto-save error: {e}")

    def get_current_time(self):
        """Get current time for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    #MARK: - Update manager
    def start_update_check(self):
        self.update_thread = UpdateCheckerThread()
        self.update_thread.update_available.connect(self.prompt_update)
        self.update_thread.up_to_date.connect(self.notify_up_to_date)
        self.update_thread.connection_error.connect(self.notify_connection_error)
        self.update_thread.start()

    def notify_up_to_date(self, version):
        QMessageBox.information(
            self, self.t("main_GUI.dialogs.update_manager.no_update_available"),
            self.t("main_GUI.dialogs.update_manager.version_up_to_date", version=version),
            QMessageBox.StandardButton.Ok
        )

    def notify_connection_error(self):
        QMessageBox.warning(
            self, self.t("main_GUI.dialogs.update_manager.connection_error_title"),
            self.t("main_GUI.dialogs.update_manager.connection_error_message"),
            QMessageBox.StandardButton.Ok
        )

    def prompt_update(self, version, assets):
        reply = QMessageBox.question(
            self, self.t("main_GUI.dialogs.update_manager.update_available_title"),
            self.t("main_GUI.dialogs.update_manager.update_available_message", version=version),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            download_url = None
            target_extension = ".exe" if sys.platform == "win32" else ".tar.gz"
            
            for asset in assets:
                if asset['name'].endswith(target_extension):
                    download_url = asset['download_url']
                    break
            
            if download_url:
                print(f"Starting update download from: {download_url}")
                self.show_update_progress(download_url)

    def show_update_progress(self, url):
        self.progress_dialog = QProgressDialog(self.t("main_GUI.dialogs.update_manager.downloading_update"), self.t("main_GUI.dialogs.update_manager.cancel"), 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.show()

        self.download_thread = DownloadUpdateThread(url)
        self.download_thread.progress.connect(self.progress_dialog.setValue)
        self.download_thread.finished.connect(self.apply_update)
        self.progress_dialog.canceled.connect(self.download_thread.terminate)
        self.download_thread.start()

    def apply_update(self, save_path):
        from updater import perform_update
        perform_update(save_path)
        os._exit(0)

    #MARK: - Cleanup on Close
    def closeEvent(self, event):
        """Handle window close event - prompt to save if there are unsaved changes"""
        print("Close event triggered - checking for unsaved changes")
        # Stop auto-save timer
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        
        # Stop execution thread
        self.visual_programming_window.stop_execution()
        
        name = Utils.project_data.metadata.get("name", "Untitled")
        
        if name == "Untitled":
            # Check if untitled project has any content
            has_content = (
                len(Utils.main_canvas.get("blocks", {})) > 0 or
                len(Utils.functions) > 0 or
                len(Utils.variables.get("main_canvas", {})) > 0 or
                len(Utils.devices.get("main_canvas", {})) > 0
            )
            
            if not has_content:
                # Empty untitled project, just close
                self.visual_programming_window.clear_canvas()
                self.visual_programming_window.close_child_windows()
                import gc
                gc.collect()
                event.accept()
                return
            
            # Has content but untitled
            reply = QMessageBox.question(
                self, self.t("main_GUI.dialogs.file_dialogs.save_project"),
                self.t("main_GUI.dialogs.file_dialogs.save_project_close"),
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.on_save_file_as()
            elif reply != QMessageBox.StandardButton.Discard:
                event.ignore()
                return
        
        else:
            # Compare with saved version
            comparison = Utils.file_manager.compare_projects(name)
            print(f"Comparison result for '{name}': {comparison}")
            print(f"Has changes: {comparison}")
            if comparison == True:
                print("Unsaved changes detected, prompting user")
                
                reply = QMessageBox.question(
                    self, self.t("main_GUI.dialogs.file_dialogs.save_project"),
                    f"{self.t('main_GUI.dialogs.file_dialogs.unsaved_changes').format(name=name)}",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save
                ) 
                if reply == QMessageBox.StandardButton.Save:
                    Utils.file_manager.save_project(name)
                elif reply != QMessageBox.StandardButton.Discard:
                    event.ignore()
                    return
        
        # Cleanup and close
        self.visual_programming_window.clear_canvas()
        self.visual_programming_window.close_child_windows()
        event.accept()

def apply_scale():
    with open(Utils.get_base_path()/"app_settings.json", "r") as f:
        app_settings = json.load(f)
    scale = app_settings.get("ui_scale", "medium")
    print(f"Applying UI scale: {scale}")

    if scale == 'small':
        print("Setting QT_SCALE_FACTOR to 0.8 for small UI scale")
        os.environ["QT_SCALE_FACTOR"] = "0.8"
    elif scale == 'medium':
        print("Setting QT_SCALE_FACTOR to 1.0 for medium UI scale")
        os.environ["QT_SCALE_FACTOR"] = "1.0"
    elif scale == 'large':
        print("Setting QT_SCALE_FACTOR to 1.2 for large UI scale")
        os.environ["QT_SCALE_FACTOR"] = "1.2"

def apply_theme(app):
    with open(Utils.get_base_path()/"app_settings.json", "r") as f:
        app_settings = json.load(f)
    theme = app_settings.get("theme", "dark")
    print(f"Applying theme: {theme}")

    palette = QPalette()

    if theme == 'dark':
        palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.NoRole, QColor(105, 105, 105))
        palette.setColor(QPalette.ColorRole.Accent, QColor(255, 0, 0))
    elif theme == 'light':
        palette.setColor(QPalette.ColorRole.Window, QColor(253, 245, 230))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, QColor(224, 218, 202))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(225, 225, 225))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(253, 245, 230))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.NoRole, QColor(169, 169, 169))
        palette.setColor(QPalette.ColorRole.Accent, QColor(255, 0, 0))
    
    app.setPalette(palette)
def main():

    apply_scale()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    

    

    app.setStyleSheet("QToolTip { color: palette(text); background-color: palette(highlight); border: 1px solid white; }")

    error_handler = UniversalErrorHandler()

    error_handler.error_occurred.connect(error_handler.show_error_dialog)
    # 1. SETUP SPLASH
    # Use a .gif path here. If you don't have one, it will default to a dark screen.
    splash = NativeSplash() 
    splash.show()
    
    # 2. SETUP WORKER THREAD
    loader = LoaderThread()
    
    # 3. DEFINE WHAT HAPPENS WHEN THREAD FINISHES
    def on_loaded():
        # Update splash one last time
        splash.update_status("Starting GUI...")
        splash.update_progress(100)
        
        apply_theme(app)
        # CRITICAL: Initialize MainWindow on the MAIN THREAD
        # We define 'window' global or attached to app so it doesn't get garbage collected
        global window 
        window = MainWindow()
        window.show()
        
        # Close splash when window is ready
        splash.finish(window)
    
    # 4. CONNECT SIGNALS
    loader.progress.connect(splash.update_progress)
    loader.status.connect(splash.update_status)
    loader.finished.connect(on_loaded)
    
    # 5. START LOADING
    loader.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()