from cProfile import label
from Imports import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
QPushButton, QLabel, QTabWidget, Qt, QFont, QTimer, QRect,
pyqtSignal, QScrollArea, QScroller, QIcon, QPropertyAnimation, QEasingCurve, logging)

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
        #logging.info(f"blocksWindow __init__ called with parent: {parent}")
        self.parent_canvas = parent
        #logging.debug(f"blocksWindow parent_canvas set to: {self.parent_canvas}")
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        
        self.is_hidden = True
        self.f_tab = None
        self.now_created = False

        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent=None):
        #logging.info(f"blocksWindow get_instance called with parent: {parent}")
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
        
        self.dropdown_menus = {}
        self.dropdown_blocks = {}

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
                    #logging.info("Creating Functions tab for function canvas")
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

        main_scroll = QScrollArea()
        main_scroll.setWidget(left_widget)
        main_scroll.setWidgetResizable(True)

        self.basic_left_layout = QVBoxLayout(left_widget)
        

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        left_widget.setMinimumWidth(200)

        left_label = QLabel(self.t("blocks_window.basic_blocks_tab.tab_title"))
        left_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.basic_left_layout.addWidget(left_label)
        self.basic_left_layout.addSpacing(10)
        # Buttons - MAPPED TO SPAWNING blocks
        basic_blocks = [
            (self.t("blocks_window.basic_blocks_tab.Start"), "Start"),
            (self.t("blocks_window.basic_blocks_tab.End"), "End"),
            (self.t("blocks_window.basic_blocks_tab.Timer"), "Timer"),
            (self.t("blocks_window.basic_blocks_tab.Networks"), "Networks"),
            (self.t("blocks_window.basic_blocks_tab.Return"), "Return")
        ]

        for label, element_type in basic_blocks:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=element_type, t='basic': self.on_block_selected(s, t))
            self.basic_left_layout.addWidget(btn)

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

        self.basic_left_layout.addStretch()
        layout.addWidget(main_scroll)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.basic_blocks_tab.tab_title"))
        self.show_block_details("Start", 'basic')  # Show default details
    
    #MARK: Logic Tab
    def create_logic_tab(self):
        """Create logic tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        main_scroll = QScrollArea()
        main_scroll.setWidget(left_widget)
        main_scroll.setWidgetResizable(True)

        self.logic_left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)


        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        
        # Title
        title = QLabel(self.t("blocks_window.logic_blocks_tab.tab_title"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logic_left_layout.addWidget(title)
        self.logic_left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING blocks
        logic_blocks = {
            self.t("blocks_window.logic_blocks_tab.Cycles"): {'name': 'Cycles', 'is_dropdown': True, 'id': 0},
            self.t("blocks_window.logic_blocks_tab.Comparison"): {'name': 'Comparison', 'is_dropdown': True, 'id': 1},
            self.t("blocks_window.logic_blocks_tab.Bool logic"): {'name': 'Bool logic', 'is_dropdown': True, 'id': 2},
        }
        for label, element in logic_blocks.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=element['name'], t='logic', is_d=element['is_dropdown'], id=element['id'], m_id=3: self.on_block_selected(s, t, is_d, id, m_id))
            self.logic_left_layout.addWidget(btn)
        
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

        self.logic_left_layout.addStretch()
        layout.addWidget(main_scroll)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.logic_blocks_tab.tab_title"))
        self.show_block_details("If", 'logic')  # Show default details
    #MARK: I/O Tab
    def create_io_tab(self):
        """Create I/O tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        main_scroll = QScrollArea()
        main_scroll.setWidget(left_widget)
        main_scroll.setWidgetResizable(True)
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
            self.t("blocks_window.io_blocks_tab.Button"): {'name': 'Button', 'is_dropdown': False, 'id': 0},
            self.t("blocks_window.io_blocks_tab.LED"): {'name': 'LED', 'is_dropdown': True, 'id': 1},
        }
        
        for label, element in io_blocks.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, e=element['name'], t='IO', is_d=element['is_dropdown'], id=element['id'], m_id=2: self.on_block_selected(e, t, is_d, id, m_id))
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
        layout.addWidget(main_scroll)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.io_blocks_tab.tab_title"))
        self.show_block_details("Button", 'io')  # Show default details
    #MARK: Math Tab
    def create_math_tab(self):
        """Create math tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        main_scroll = QScrollArea()
        left_widget = QWidget()

        main_scroll.setWidget(left_widget)
        main_scroll.setWidgetResizable(True)
        self.math_left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Title
        title = QLabel(self.t("blocks_window.math_blocks_tab.tab_title"))
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.math_left_layout.addWidget(title)
        self.math_left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING blocks
        math_blocks = [
            (self.t("blocks_window.math_blocks_tab.Plus"), "Plus"),
            (self.t("blocks_window.math_blocks_tab.Minus"), "Minus"),
            (self.t("blocks_window.math_blocks_tab.Multiply"), "Multiply"),
            (self.t("blocks_window.math_blocks_tab.Divide"), "Divide"),
            (self.t("blocks_window.math_blocks_tab.Modulo"), "Modulo"),
            (self.t("blocks_window.math_blocks_tab.Power"), "Power"),
            (self.t("blocks_window.math_blocks_tab.Root"), "Root"),
            (self.t("blocks_window.math_blocks_tab.Random_number"), "Random_number"),
            (self.t("blocks_window.math_blocks_tab.Plus_one"), "Plus_one"),
            (self.t("blocks_window.math_blocks_tab.Minus_one"), "Minus_one")
        ]
        
        for label, element in math_blocks:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, e=element, t='math': self.show_block_details(e, t))
            self.math_left_layout.addWidget(btn)
        
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

        self.math_left_layout.addStretch()
        layout.addWidget(main_scroll)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, self.t("blocks_window.math_blocks_tab.tab_title"))
        self.show_block_details("Plus", 'math')  # Show default details
    #MARK: Functions Tab
    def create_functions_tab(self):
        """Create functions tab"""
        #logging.info("Creating Functions tab in blocksWindow")
        #logging.debug(f" Self f_tab: {self.f_tab if hasattr(self, 'f_tab') else 'Not defined'}")
        
        if self.f_tab is not None and self.function_layout.count() > 0:
            while self.function_layout.count():
                child = self.function_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for i in range(self.function_layout.count() - 1, -1, -1):
                item = self.function_layout.itemAt(i)
                if item and item.spacerItem():
                    self.function_layout.takeAt(i)

        if self.f_tab is None:
            self.f_tab = QWidget()
            layout = QVBoxLayout(self.f_tab)
            widget = QWidget()
            main_scroll = QScrollArea()
            main_scroll.setWidget(widget)
            main_scroll.setWidgetResizable(True)
            self.function_layout = QVBoxLayout(widget)
            self.function_layout.setSpacing(5)
            self.now_created = True
            # Title
            title = QLabel(self.t("blocks_window.function_blocks_tab.tab_title"))
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.function_layout.addWidget(title)
            self.function_layout.addSpacing(10)
            layout.addWidget(main_scroll)
            
        

        function_blocks = []
            # Buttons - MAPPED TO SPAWNING blocks
        for f, f_info in Utils.functions.items():
            #logging.debug(f"Function available: {f} with info {f_info}")
            function_blocks.append(f_info['name'])
        #logging.info(f"Function blocks collected: {function_blocks}")
        for element in function_blocks:
            btn = QPushButton(element)
            element_type = "Function"
            btn.clicked.connect(lambda checked, e=element_type, n=element if element else None: self.spawn_element(e, n))
            self.function_layout.addWidget(btn)
        self.function_layout.addStretch()

        if self.now_created:
            #logging.info("Adding Functions tab to blocksWindow")
            self.tab_widget.addTab(self.f_tab, self.t("blocks_window.function_blocks_tab.tab_title"))
    #MARK: Block Details
    def on_block_selected(self, element_type, tab_name, is_dropdown=False, id=None, m_id=None):
        """Handle selection of basic block from list"""
        if is_dropdown:
            self.open_dropdown_menu(element_type, tab_name, id, m_id)
        else:
            self.show_block_details(element_type, tab_name)

    def open_dropdown_menu(self, element_type, tab_name, id=None, m_id=None):
        #logging.info(f"Opening dropdown menu for {element_type} in {tab_name} tab")
        if element_type == "LED":
            blocks = (
                (self.t("blocks_window.io_blocks_tab.Blink_LED"), 'Blink_LED'),
                (self.t("blocks_window.io_blocks_tab.Toggle_LED"), 'Toggle_LED'),
                (self.t("blocks_window.io_blocks_tab.PWM_LED"), 'PWM_LED'),
                (self.t("blocks_window.io_blocks_tab.RGB_LED"), 'RGB_LED'),
                (self.t("blocks_window.io_blocks_tab.LED_ON"), 'LED_ON'),
                (self.t("blocks_window.io_blocks_tab.LED_OFF"), 'LED_OFF')
            )
        elif element_type == "Cycles":
            blocks = (
                (self.t("blocks_window.logic_blocks_tab.If"), "If"),
                (self.t("blocks_window.logic_blocks_tab.While"), "While"),
                (self.t("blocks_window.logic_blocks_tab.While_true"), "While_true"),
                (self.t("blocks_window.logic_blocks_tab.Switch"), "Switch"),
                (self.t("blocks_window.logic_blocks_tab.For_Loop"), "For_Loop"),
            )
        elif element_type == "Comparison":
            blocks = (
                (self.t("blocks_window.logic_blocks_tab.Lower"), "Lower"),
                (self.t("blocks_window.logic_blocks_tab.Greater"), "Greater"),
                (self.t("blocks_window.logic_blocks_tab.Equal"), "Equal"),
                (self.t("blocks_window.logic_blocks_tab.Not_equal"), "Not_equal"),
                (self.t("blocks_window.logic_blocks_tab.Greater_equal"), "Greater_equal"),
                (self.t("blocks_window.logic_blocks_tab.Lower_equal"), "Lower_equal")
            )
        elif element_type == "Bool logic":
            blocks = (
                (self.t("blocks_window.logic_blocks_tab.Not"), "Not"),
                (self.t("blocks_window.logic_blocks_tab.And"), "And"),
                (self.t("blocks_window.logic_blocks_tab.Nand"), "Nand"),
                (self.t("blocks_window.logic_blocks_tab.Or"), "Or"),
                (self.t("blocks_window.logic_blocks_tab.Nor"), "Nor"),
                (self.t("blocks_window.logic_blocks_tab.Xor"), "Xor"),
                (self.t("blocks_window.logic_blocks_tab.Xnor"), "Xnor")
            )
        if tab_name == 'IO':
            tab = self.IO_left_layout
        elif tab_name == 'logic':
            tab = self.logic_left_layout
        elif tab_name == 'basic':
            tab = self.basic_left_layout
        elif tab_name == 'math':
            tab = self.math_left_layout
        if element_type not in self.dropdown_menus.keys():
            #logging.info(f"Adding dropdown options for {element_type} in {tab_name} tab")
            info = {"name": element_type, "is_dropdown": True, "id": id}
            self.dropdown_menus.setdefault(element_type, info)
            #logging.debug(f"Dropdown menus now: {self.dropdown_menus}")
            #logging.debug(f"Block displayed {self.dropdown_blocks}")
            length = 0
            for key, val in self.dropdown_menus.items():
                #logging.debug(f"Dropdown menu - {key}: {val}")
                if val['id'] > id:
                    #logging.debug(f"Menu {key} with id {val['id']} is after current id {id}")
                    length += len(self.dropdown_blocks.get(key, []))
            insert = abs(length + m_id - id) if m_id is not None and id is not None else 1
            for blocks in blocks:
                #logging.info(f"Adding button for {blocks[0]} with element type {blocks[1]}")
                label, block_name = blocks
                line_widget = QWidget()
                line_layout = QHBoxLayout(line_widget)
                line_layout.setContentsMargins(0, 0, 0, 0)
                separator = QWidget()
                separator.setFixedWidth(2)
                separator.setStyleSheet("background-color: palette(base);")
                btn = QPushButton(label)
                btn.clicked.connect(lambda checked, e=block_name, t=tab_name: self.on_block_selected(e, t))
                self.dropdown_blocks.setdefault(element_type, []).append(label)
                #logging.debug(f"Inserting {label} at position {tab.count() - insert}, tab.count() = {tab.count()}, insert = {insert}, length = {length}, m_id = {m_id}, id = {id} in {tab_name} tab")
                line_layout.addWidget(separator)
                line_layout.addWidget(btn)

                tab.insertWidget(tab.count() - insert, line_widget)
        elif element_type in self.dropdown_menus.keys():
            # Remove dropdown options
            self.dropdown_menus.pop(element_type, None)
            length = 0
            for key, val in self.dropdown_menus.items():
                #logging.info(f"Remaining menu - {key}: {val}")
                if val['id'] > id:
                    #logging.debug(f"Menu {key} with id {val['id']} is after current id {id}")
                    length += len(self.dropdown_blocks.get(key, []))
            insert = m_id - id - length if m_id is not None and id is not None else 1
            for i in range(tab.count() - insert, -1, -1):
                item = tab.itemAt(i)
                if item and item.widget() and item.widget().findChild(QPushButton) and item.widget().findChild(QPushButton).text() in self.dropdown_blocks.get(element_type, []):
                    widget = item.widget()
                    tab.removeWidget(widget)
                    widget.deleteLater()
                    self.dropdown_blocks[element_type].remove(widget.findChild(QPushButton).text())
            if not self.dropdown_blocks[element_type]:
                del self.dropdown_blocks[element_type]
            

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
            #logging.info(f"blocksWindow spawn_element called: {element_type}")
            
            # Get CURRENT canvas
            #logging.info(f" Parent canvas in blocksWindow: {self.parent_canvas}, main_window: {getattr(self.parent_canvas, 'main_window', None)}")
            if self.parent and hasattr(self.parent_canvas, 'main_window'):
                #logging.info(" Getting current canvas from main window")
                current_canvas = self.parent_canvas.GUI.current_canvas
            else:
                current_canvas = self.parent_canvas
            #logging.info(f"Current canvas determined for spawning: {current_canvas}")
            if current_canvas is None:
                return
            #logging.debug(f"Spawner {getattr(current_canvas, 'spawner', None)} on canvas {id(current_canvas)} will spawn element: {element_type} with name: {name}")
            # ✓ Use CURRENT canvas's spawner, not stored self.element_spawner!
            if hasattr(current_canvas, 'spawner'):
                #logging.info("Current state of canvas before spawning:", self.state_manager.canvas_state.current_state())
                if self.state_manager.canvas_state.on_adding_block():
                    #logging.info("Current state of canvas before spawning:", self.state_manager.canvas_state.current_state())
                    current_canvas.spawner.start(current_canvas, element_type, name=name)
                    #logging.info(f"Element spawn initiated on canvas {id(current_canvas)}")
                else:
                    logging.warninig("Canvas cannot add block right now.")
            else:
                logging.error("Canvas has no spawner!")
            
        except Exception as e:
            logging.error(f"Error spawning {element_type}: {e}")
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
        #logging.info("Opening blocksWindow")
        if self.is_hidden:
            #logging.info("Initially hidden, showing window")
            self.is_hidden = False
            for canvas_info in Utils.canvas_instances.values():
                #logging.debug(f"Checking canvas {id(canvas_info['canvas'])} with ref {canvas_info['ref']} against parent_canvas {self.parent_canvas}")
                if canvas_info['canvas'] == self.parent_canvas:
                    #loggin.info("Found matching canvas for blocksWindow open")
                    if canvas_info['ref'] == 'canvas' and len(Utils.canvas_instances) > 1:
                        #logging.info("Ensuring Functions tab is created for main canvas")
                        self.create_functions_tab()
                        break
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            #logging.info("blocksWindow already open, raising to front")
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
        #logging.info("blocksWindow closeEvent called")
        self.is_hidden = True
        self.state_manager.app_state.on_blocks_dialog_close()
        event.accept()
