from cProfile import label
from Imports import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
QPushButton, QLabel, QTabWidget, Qt, QFont, QTimer, QRect,
pyqtSignal, QScrollArea, QScroller, QIcon, QPropertyAnimation, QEasingCurve)

from Imports import get_Spawn_Blocks, get_Utils

Utils = get_Utils()
spawning_blocks = get_Spawn_Blocks()[1]

class blocksWindow(QDialog):
    """blocks selection window with tabs - synced with spawn_blocks"""
    
    _instance = None
    
    # Signals for element spawning
    element_requested = pyqtSignal(str)  # element_type
    
    def __init__(self, parent=None):
        super().__init__()
        print(f"blocksWindow __init__ called with parent: {parent}")
        self.parent_canvas = parent
        print(f"blocksWindow parent_canvas set to: {self.parent_canvas}")
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        
        self.is_hidden = True
        self.f_tab = None
        self.now_created = False

        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent=None):
        print(f"blocksWindow get_instance called with parent: {parent}")
        if cls._instance is not None:
            try:
                _ = cls._instance.isVisible()
                if cls._instance.is_hidden:
                    return cls._instance
            except RuntimeError:
                cls._instance = None

            except Exception as e:
                cls._instance = None

        if cls._instance is None:
            cls._instance = cls(parent)
        
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(self.t("blocks_window.window_title"))
        self.setWindowIcon(QIcon('resources/images/APPicon.ico'))
        self.resize(550, 400)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: palette(window);
            }}
            QTabWidget::pane {{
                border: 1px solid palette(base);
                background-color: palette(window);
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: palette(window);
                color: palette(text);
                padding: 8px 20px;
                border: 1px solid palette(base);
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: palette(highlight);
            }}
            QTabBar::tab:hover {{
                background-color: palette(highlight);
            }}
            QLabel {{
                color: palette(text);
            }}
            QPushButton {{
                background-color: palette(window);
                color: palette(text);
                border: none;
                padding: 10px;
                border: 1px solid palette(base);
                border-radius: 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: palette(highlight);
            }}
            QPushButton:pressed {{
                background-color: palette(highlight);
            }}
            QWidget {{ background-color: palette(window); }}
            QLabel {{
                background-color: palette(window);
                border: 1px solid palette(base);
                padding: 10px;
            }}
        """)
        
        self.dropdown_menus = []

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_basic_tab()
        self.create_logic_tab()
        self.create_io_tab()
        self.create_math_tab()
        for canvas_id, canvas_info in Utils.canvas_instances.items():
            if canvas_info['canvas'] == self.parent_canvas:
                if canvas_info['ref'] == 'function':
                    print("Creating Functions tab for function canvas")
                    self.create_functions_tab()
                    break
    
    def mousePressEvent(self, event):
        """Debug: Track if blocks window gets mouse press"""
        super().mousePressEvent(event)
    #MARK: Basic Tab
    def create_basic_tab(self):
        """Create basic tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        left_widget.setMinimumWidth(200)

        left_label = QLabel(self.t("blocks_window.basic_blocks_tab.tab_title"))
        left_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(left_label)
        left_layout.addSpacing(10)
        # Buttons - MAPPED TO SPAWNING blocks
        basic_blocks = [
            (self.t("blocks_window.basic_blocks_tab.Start"), "Start"),
            (self.t("blocks_window.basic_blocks_tab.End"), "End"),
            (self.t("blocks_window.basic_blocks_tab.Timer"), "Timer"),
            (self.t("blocks_window.basic_blocks_tab.Networks"), "Networks")
        ]

        for label, element_type in basic_blocks:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=element_type, t='basic': self.on_block_selected(s, t))
            left_layout.addWidget(btn)

        self.basic_description_text = QLabel("")
        self.basic_description_text.setWordWrap(True)

        scroll_area = QScrollArea()
        QScroller.grabGesture(
            scroll_area.viewport(),
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )

        scroll_area.setWidget(self.basic_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel(self.t("blocks_window.block_details"))
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton(self.t("blocks_window.add_block"))
        add_button.clicked.connect(lambda: self.spawn_element(self.basic_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.basic_blocks_tab.tab_title"))
        self.show_block_details("Start", 'basic')  # Show default details
    
    #MARK: Logic Tab
    def create_logic_tab(self):
        """Create logic tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)


        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        
        # Title
        title = QLabel(self.t("blocks_window.logic_blocks_tab.tab_title"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING blocks
        logic_blocks = [
            (self.t("blocks_window.logic_blocks_tab.If"), "If"),
            (self.t("blocks_window.logic_blocks_tab.While"), "While"),
            (self.t("blocks_window.logic_blocks_tab.While_true"), "While_true"),
            (self.t("blocks_window.logic_blocks_tab.Switch"), "Switch"),
            (self.t("blocks_window.logic_blocks_tab.For_Loop"), "For_Loop")
        ]
        
        for label, logic_type in logic_blocks:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=logic_type, t='logic': self.on_block_selected(s, t))
            left_layout.addWidget(btn)
        
        self.logic_description_text = QLabel("")
        self.logic_description_text.setWordWrap(True)
        scroll_area = QScrollArea()
        QScroller.grabGesture(
            scroll_area.viewport(),
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll_area.setWidget(self.logic_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel(self.t("blocks_window.block_details"))
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton(self.t("blocks_window.add_block"))
        add_button.clicked.connect(lambda: self.spawn_element(self.logic_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.logic_blocks_tab.tab_title"))
        self.show_block_details("If", 'logic')  # Show default details
    #MARK: I/O Tab
    def create_io_tab(self):
        """Create I/O tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        self.IO_left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        
        # Title
        title = QLabel(self.t("blocks_window.io_blocks_tab.tab_title"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.IO_left_layout.addWidget(title)
        self.IO_left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING blocks

        io_blocks = {
            self.t("blocks_window.io_blocks_tab.Button"): {'name': 'Button', 'is_dropdown': False},
            self.t("blocks_window.io_blocks_tab.LED"): {'name': 'LED', 'is_dropdown': True},
        }
        
        for label, element in io_blocks.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, e=element['name'], t='io', is_d=element['is_dropdown']: self.on_block_selected(e, t, is_d))
            self.IO_left_layout.addWidget(btn)
        
        self.IO_description_text = QLabel("")
        self.IO_description_text.setWordWrap(True)
    
        scroll_area = QScrollArea()
        QScroller.grabGesture(
            scroll_area.viewport(),
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll_area.setWidget(self.IO_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel(self.t("blocks_window.block_details"))
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton(self.t("blocks_window.add_block"))
        add_button.clicked.connect(lambda: self.spawn_element(self.IO_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        self.IO_left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.io_blocks_tab.tab_title"))
        self.show_block_details("Button", 'io')  # Show default details
    #MARK: Math Tab
    def create_math_tab(self):
        """Create math tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Title
        title = QLabel(self.t("blocks_window.math_blocks_tab.tab_title"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING blocks
        math_blocks = [
            (self.t("blocks_window.math_blocks_tab.basic_operations"), "Basic_operations"),
            (self.t("blocks_window.math_blocks_tab.plus_one"), "Plus_one"),
            (self.t("blocks_window.math_blocks_tab.minus_one"), "Minus_one"),
            (self.t("blocks_window.math_blocks_tab.exponential_operations"), "Exponential_operations"), 
            (self.t("blocks_window.math_blocks_tab.random_number"), "Random_number")
        ]
        
        for label, element in math_blocks:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, e=element, t='math': self.show_block_details(e, t))
            left_layout.addWidget(btn)
        
        self.math_description_text = QLabel("")
        self.math_description_text.setWordWrap(True)

        scroll_area = QScrollArea()
        QScroller.grabGesture(
            scroll_area.viewport(),
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll_area.setWidget(self.math_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel(self.t("blocks_window.block_details"))
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton(self.t("blocks_window.add_block"))
        add_button.clicked.connect(lambda: self.spawn_element(self.math_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.math_blocks_tab.tab_title"))
        self.show_block_details("Basic_operations", 'math')  # Show default details
    #MARK: Functions Tab
    def create_functions_tab(self):
        """Create functions tab"""
        #print("Creating Functions tab in blocksWindow")
        #print(F" Self f_tab: {self.f_tab if hasattr(self, 'f_tab') else 'Not defined'}")
        
        if self.f_tab is not None and self.layout.count() > 0:
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for i in range(self.layout.count() - 1, -1, -1):
                item = self.layout.itemAt(i)
                if item and item.spacerItem():
                    self.layout.takeAt(i)

        if self.f_tab is None:
            self.f_tab = QWidget()
            self.layout = QVBoxLayout(self.f_tab)
            self.layout.setSpacing(5)
            self.now_created = True
            # Title
            title = QLabel(self.t("blocks_window.function_blocks_tab.tab_title"))
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(title)
            self.layout.addSpacing(10)
            
        

        function_blocks = []
            # Buttons - MAPPED TO SPAWNING blocks
        for f, f_info in Utils.functions.items():
            #print(f"Function available: {f} with info {f_info}")
            function_blocks.append(f_info['name'])
        #print(f"Function blocks collected: {function_blocks}")
        for element in function_blocks:
            btn = QPushButton(element)
            element_type = "Function"
            btn.clicked.connect(lambda checked, e=element_type, n=element if element else None: self.spawn_element(e, n))
            self.layout.addWidget(btn)
        self.layout.addStretch()

        if self.now_created:
            #print("Adding Functions tab to blocksWindow")
            self.tab_widget.addTab(self.f_tab, self.t("blocks_window.function_blocks_tab.tab_title"))
    #MARK: Block Details
    def on_block_selected(self, element_type, tab_name, is_dropdown=False):
        """Handle selection of basic block from list"""
        if is_dropdown:
            self.open_dropdown_menu(element_type, tab_name)
        else:
            self.show_block_details(element_type, tab_name)

    def open_dropdown_menu(self, element_type, tab_name):

        if element_type == "LED":
            led_blocks = ((self.t("blocks_window.io_blocks_tab.Blink_LED"), 'Blink_LED'),
                            (self.t("blocks_window.io_blocks_tab.Toggle_LED"), 'Toggle_LED'),
                            (self.t("blocks_window.io_blocks_tab.PWM_LED"), 'PWM_LED'),
                            (self.t("blocks_window.io_blocks_tab.RGB_LED"), 'RGB_LED'),
                            (self.t("blocks_window.io_blocks_tab.LED_ON"), 'LED_ON'),
                            (self.t("blocks_window.io_blocks_tab.LED_OFF"), 'LED_OFF')
                            )
            if element_type not in self.dropdown_menus:
                self.dropdown_menus.append(element_type)
                for blocks in led_blocks:
                    label, block_name = blocks
                    btn = QPushButton(label)
                    btn.clicked.connect(lambda checked, e=block_name, t=tab_name: self.on_block_selected(e, t))
                    self.IO_left_layout.insertWidget(self.IO_left_layout.count() - 1, btn)
            elif element_type in self.dropdown_menus:
                # Remove dropdown options
                self.dropdown_menus.remove(element_type)
                for i in range(self.IO_left_layout.count() - 1, -1, -1):
                    item = self.IO_left_layout.itemAt(i)
                    if item and item.widget() and item.widget().text() in [b[0] for b in led_blocks]:
                        widget = item.widget()
                        self.IO_left_layout.removeWidget(widget)
                        widget.deleteLater()
            

    def show_block_details(self, element_type, tab_name):
        """Show details for selected basic block"""
        # Clear previous details
        block_data = self.t("blocks_window.blocks_descriptions." + element_type)
        # Add details based on element_type
        if block_data:
            if tab_name == 'basic':
                self.basic_description_text.setText(f"{element_type}:\n\n{block_data}")
            elif tab_name == 'logic':
                self.logic_description_text.setText(f"{element_type}:\n\n{block_data}")
            elif tab_name == 'math':
                self.math_description_text.setText(f"{element_type}:\n\n{block_data}")
            elif tab_name == 'io':
                self.IO_description_text.setText(f"{element_type}:\n\n{block_data}")
        else:
            data = self.t("blocks_window.blocks_descriptions.no_description")
            if tab_name == 'basic':
                self.basic_description_text.setText(f"{element_type}:\n\n{data}")
            elif tab_name == 'logic':
                self.logic_description_text.setText(f"{element_type}:\n\n{data}")
            elif tab_name == 'math':
                self.math_description_text.setText(f"{element_type}:\n\n{data}")
            elif tab_name == 'io':
                self.IO_description_text.setText(f"{element_type}:\n\n{data}")
    #MARK: Spawn Element
    def spawn_element(self, element_type, name=None):
        """
        Spawn a shape/logic/IO element
        
        Args:
            element_type: "Start", "End", "Timer", "If", "While", "Switch", etc.
        """
        
        try:
            print(f"blocksWindow spawn_element called: {element_type}")
            
            # Get CURRENT canvas
            print(f" Parent canvas in blocksWindow: {self.parent_canvas}, main_window: {getattr(self.parent_canvas, 'main_window', None)}")
            if self.parent and hasattr(self.parent_canvas, 'main_window'):
                #print(" Getting current canvas from main window")
                current_canvas = self.parent_canvas.GUI.current_canvas
            else:
                current_canvas = self.parent_canvas
            print(f"Current canvas determined for spawning: {current_canvas}")
            if current_canvas is None:
                return
            print(f"Spawner {getattr(current_canvas, 'spawner', None)} on canvas {id(current_canvas)} will spawn element: {element_type} with name: {name}")
            # ✓ Use CURRENT canvas's spawner, not stored self.element_spawner!
            if hasattr(current_canvas, 'spawner'):
                print("Current state of canvas before spawning:", self.state_manager.canvas_state.current_state())
                if self.state_manager.canvas_state.on_adding_block():
                    print("Current state of canvas before spawning:", self.state_manager.canvas_state.current_state())
                    current_canvas.spawner.start(current_canvas, element_type, name=name)
                    print(f"Element spawn initiated on canvas {id(current_canvas)}")
                else:
                    print("Canvas cannot add block right now.")
            else:
                print("ERROR: Canvas has no spawner!")
            
        except Exception as e:
            print(f"Error spawning {element_type}: {e}")
            import traceback
            traceback.print_exc()
    
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
        highlight_style = original_style + "QDialog { background-color: palette(norole); }"
        
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
        #print("Opening blocksWindow")
        if self.is_hidden:
            #print("Initially hidden, showing window")
            self.is_hidden = False
            for canvas_info in Utils.canvas_instances.values():
                #print(f"Checking canvas {id(canvas_info['canvas'])} with ref {canvas_info['ref']} against parent_canvas {self.parent_canvas}")
                if canvas_info['canvas'] == self.parent_canvas:
                    #print("Found matching canvas for blocksWindow open")
                    if canvas_info['ref'] == 'canvas' and len(Utils.canvas_instances) > 1:
                        #print("Ensuring Functions tab is created for main canvas")
                        self.create_functions_tab()
                        break
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            #print("blocksWindow already open, raising to front")
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
        print("blocksWindow closeEvent called")
        self.is_hidden = True
        self.state_manager.app_state.on_blocks_dialog_close()
        event.accept()
