from Imports import (QDialog, Qt, QVBoxLayout, QLabel, QTabWidget, QWidget, QFont, QTextEdit,
                     QScrollArea, QPushButton,Path, os, get_Utils, QScroller, QTextBrowser, QIcon,
                     QPropertyAnimation, QEasingCurve, QTimer, QRect)

Utils = get_Utils()

class HelpWindow(QDialog):
    """Singleton Help Window"""
    _instance = None

    def __init__(self, parent=None, which=0):
        super().__init__()
        self.parent_canvas = parent
        self.which = which
        self.is_hidden = True
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.base_path = Utils.get_base_path()
        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent=None, which=0):
        if cls._instance is None:
            try:
                _ = cls._instance.isVisible()  # Check if the instance is still valid
                if cls._instance.is_hidden:
                    return cls._instance
            except RuntimeError:
                cls._instance = None  # Reset instance if it was deleted
            except Exception as e:
                cls._instance = None  # Reset instance on any unexpected error
        if cls._instance is None:
            cls._instance = cls(parent=parent, which=which)

        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(self.t("help_window.window_title"))
        self.setWindowIcon(QIcon('resources/images/APPicon.ico'))
        self.resize(600, 400)
        
        self.setWindowFlags(Qt.WindowType.Window)
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: palette(window);
            }
            QTabWidget::pane {
                border: 1px solid palette(base);
                background-color: palette(window);
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: palette(window);
                color: palette(text);
                padding: 8px 20px;
                border: 1px solid palette(base);
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: palette(highlight);
            }
            QTabBar::tab:hover {
                background-color: palette(highlight).lighter(120);
            }
            QLabel {
                color: palette(text);
            }
            QPushButton {
                background-color: palette(highlight);
                color: palette(text);
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: palette(highlight).lighter(120);
            }
            QPushButton:pressed {
                background-color: palette(highlight).darker(120);
            }

        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.create_getting_started_tab()
        self.create_tutorial_tab()
        self.create_faq_tab()
        
        self.tab_widget.setCurrentIndex(self.which)
        
    def create_getting_started_tab(self):
        """Create the Getting Started tab"""
        #print("Creating Getting Started tab")
        window = self.palette().color(self.palette().ColorRole.Window).name()
        text = self.palette().color(self.palette().ColorRole.Text).name()
        text_hightlight = self.palette().color(self.palette().ColorRole.HighlightedText).name()
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)
        
        css = self.get_content_stylesheet().format(window=window, text=text, text_hightlight=text_hightlight)

        html_file_path = self.t("help_window.getting_started_tab.content")

        base_dir = self.base_path
        full_path = base_dir / html_file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                html_template = f.read()

                html_content = html_template.format(css=css)
            
            # Now use html_content in your QTextEdit or wherever you need it
            # For tutorial:
            # self.help_text_widget.setHtml(html_content)
            
        except FileNotFoundError:
            print(f"Help file not found: {full_path}")
            html_content = self.t("help_window.getting_started_tab.file_not_found")
        except Exception as e:
            print(f"Error loading help content: {e}")
            html_content = self.t("help_window.getting_started_tab.error_loading_file")

        text_edit = QTextBrowser()
        text_edit.setReadOnly(True)
        text_edit.setHtml(html_content)
        text_edit.setOpenExternalLinks(True)
        layout.addWidget(text_edit)
        #print("Added label to Getting Started tab")
        self.tab_widget.addTab(tab, self.t("help_window.getting_started_tab.title"))

    def create_tutorial_tab(self):
        """Create the tutorial tab with scrollable vertical tutorial"""
        #print("Creating tutorial tab")
        self.tutorial_tab = QWidget()
        self.tutorial_layout = QVBoxLayout(self.tutorial_tab)
        self.tutorial_layout.setContentsMargins(0, 0, 0, 0)
        
        self.show_tutorial_list()
        
        self.tab_widget.addTab(self.tutorial_tab, self.t("help_window.tutorials_tab.title"))
        #print("Added scrollable tutorial to tutorial tab")

    def show_tutorial_list(self):
        """Show the tutorial list view"""
        # Clear layout
        while self.tutorial_layout.count():
            self.tutorial_layout.takeAt(0).widget().deleteLater()
        
        # Create scroll area
        scroll = QScrollArea()
        QScroller.grabGesture(
            scroll.viewport(), 
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: palette(window); }
            QScrollBar:vertical { background-color: palette(window); width: 12px; border: none; }
            QScrollBar::handle:vertical { background-color: palette(mid); border-radius: 6px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background-color: palette(highlight); }
        """)
        
        # Create container widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add tutorial
        tutorial = [
            (self.t("help_window.tutorials_tab.tutorials.tutorial_0_linux_based_RPI.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_0_linux_based_RPI.description"), "0"),
            (self.t("help_window.tutorials_tab.tutorials.tutorial_0_RPI_PICO.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_0_RPI_PICO.description"), "0_RPI_PICO"),
            (self.t("help_window.tutorials_tab.tutorials.tutorial_1.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_1.description"), "1"),
            (self.t("help_window.tutorials_tab.tutorials.tutorial_2.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_2.description"), "2"),
            (self.t("help_window.tutorials_tab.tutorials.tutorial_3.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_3.description"), "3"),
            (self.t("help_window.tutorials_tab.tutorials.tutorial_4.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_4.description"), "4"),
            (self.t("help_window.tutorials_tab.tutorials.tutorial_5.title"), self.t("help_window.tutorials_tab.tutorials.tutorial_5.description"), "5"),
        ]
        
        for title, description, tutorial_id in tutorial:
            item_widget = self._create_tutorial_item(title, description, tutorial_id)
            scroll_layout.addWidget(item_widget)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.tutorial_layout.addWidget(scroll)
    
    def _create_tutorial_item(self, title, description, tutorial_id):
        """Helper method to create a styled tutorial item"""
        item = QWidget()
        item_layout = QVBoxLayout(item)
        item_layout.setContentsMargins(10, 10, 10, 10)
        item_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: palette(highlighted-text);")
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: palette(text);")
        
        view_btn = QPushButton(self.t("help_window.tutorials_tab.show_tutorial_button"))
        view_btn.setMaximumWidth(120)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        view_btn.clicked.connect(lambda: self.show_tutorial_detail(title, description, tutorial_id))
        
        item_layout.addWidget(title_label)
        item_layout.addWidget(desc_label)
        item_layout.addWidget(view_btn)
        
        item.setStyleSheet("QWidget { border-bottom: 1px solid palette(mid); }")
        return item

    def show_tutorial_detail(self, title, description, tutorial_id):
        """Show detailed view of an tutorial"""
        self.current_tutorial = (title, description)
        
        # Clear layout
        while self.tutorial_layout.count():
            self.tutorial_layout.takeAt(0).widget().deleteLater()
        
        # Create detail view
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        detail_layout.setSpacing(10)
        
        # Back button
        back_btn = QPushButton(self.t("help_window.tutorials_tab.back_to_tutorials_button"))
        back_btn.setMaximumWidth(150)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.show_tutorial_list)
        detail_layout.addWidget(back_btn)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: palette(highlighted-text);")
        detail_layout.addWidget(title_label)
        
        content = QTextBrowser()
        content.setReadOnly(True)
        content.setOpenExternalLinks(True)
        self.fill_content_area(content, tutorial_id)
        detail_layout.addWidget(content)
        
        # Add to tab
        self.tutorial_layout.addWidget(detail_widget)

    def fill_content_area(self, content, tutorial_id):
        window = self.palette().color(self.palette().ColorRole.Window).name()
        text = self.palette().color(self.palette().ColorRole.Text).name()
        text_hightlight = self.palette().color(self.palette().ColorRole.HighlightedText).name()
        print(f"Window {window}, text {text}, text_hightlight {text_hightlight}")
        css = self.get_content_stylesheet().format(window=window, text=text, text_hightlight=text_hightlight)
        #print(f"Filling content area for tutorial ID: {tutorial_id}")
        match tutorial_id:
            case "0":
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_0_linux_based_RPI.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)

                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")

                #print("Filling content for tutorial 0")
                content.setHtml(html_content)
            case "0_RPI_PICO":
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_0_RPI_PICO.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")
                
                content.setHtml(html_content)
            case "1":
                #print("Filling content for tutorial 1")
                current_dir = self.base_path
                Power_Supply_Symbol_DC = current_dir / "resources/images/Tutorials/Tutorial_1/Power_Supply_Symbol_DC.png"
                Power_Supply_Symbol_AC = current_dir / "resources/images/Tutorials/Tutorial_1/Power_Supply_Symbol_DC.png"
                Pin_Connection_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Pin_Connection_Symbol.png"
                Resistor_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Resistor_Symbol.png"
                Capacitor_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Capacitor_Symbol.png"
                Inductor_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Inductor_Symbol.png"
                Diode_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Diode_Symbol.png"
                LED_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/LED_Symbol.png"
                Transistor_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Transistor_Symbol.png"
                Ground_Symbol = current_dir / "resources/images/Tutorials/Tutorial_1/Ground_Symbol.png"
                for path in [
                    Power_Supply_Symbol_DC,
                    Power_Supply_Symbol_AC,
                    Pin_Connection_Symbol,
                    Resistor_Symbol,
                    Capacitor_Symbol,
                    Inductor_Symbol,
                    Diode_Symbol,
                    LED_Symbol,
                    Transistor_Symbol,
                    Ground_Symbol
                ]:
                    path = path.resolve()  # Ensure we have an absolute path
                    path = path.as_posix()
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_1.content")
 
                full_path = current_dir / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()
                        html_content = html_template.format(
                            css=css,
                            Power_Supply_Symbol_DC=Power_Supply_Symbol_DC,
                            Power_Supply_Symbol_AC=Power_Supply_Symbol_AC,
                            Pin_Connection_Symbol=Pin_Connection_Symbol,
                            Resistor_Symbol=Resistor_Symbol,
                            Capacitor_Symbol=Capacitor_Symbol,
                            Inductor_Symbol=Inductor_Symbol,
                            Diode_Symbol=Diode_Symbol,
                            LED_Symbol=LED_Symbol,
                            Transistor_Symbol=Transistor_Symbol,
                            Ground_Symbol=Ground_Symbol
                        )
                    # Now use html_content in your QTextEdit or wherever you need it
                    # For tutorial:
                    # self.help_text_widget.setHtml(html_content)
                    
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")
                #print(f"Image path for help content: {Blinking_LED_Diagram}")

                content.setHtml(html_content)
            case "2":
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_2.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)

                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")

                    #print("Filling content for tutorial 2")
                content.setHtml(html_content)
            case "3":
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_3.content")
                
                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")
                #print("Filling content for tutorial 3")
                content.setHtml(html_content)
            case "4":
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_4.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")
    
                #print("Filling content for tutorial 4")
                content.setHtml(html_content)
            case "5":
                html_file_path = self.t("help_window.tutorials_tab.tutorials.tutorial_5.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.tutorials_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.tutorials_tab.error_loading_file")

                #print("Filling content for tutorial 5")
                content.setHtml(html_content)
        
    def create_faq_tab(self):
        """Create the FAQ tab"""
        #print("Creating FAQ tab")

        window = self.palette().color(self.palette().ColorRole.Window).name()
        text = self.palette().color(self.palette().ColorRole.Text).name()
        text_hightlight = self.palette().color(self.palette().ColorRole.HighlightedText).name()
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text_edit = QTextBrowser()
        text_edit.setReadOnly(True)
        text_edit.setOpenExternalLinks(True)
        css = self.get_content_stylesheet().format(window=window, text=text, text_hightlight=text_hightlight)

        html_file_path = self.t("help_window.faq_tab.content")
        full_path = self.base_path / html_file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                html_template = f.read()

                html_content = html_template.format(css=css)
        except FileNotFoundError:
            print(f"Help file not found: {full_path}")
            html_content = self.t("help_window.faq_tab.file_not_found")
        except Exception as e:
            print(f"Error loading FAQ content: {e}")
            html_content = self.t("help_window.faq_tab.error_loading_file")
        
        text_edit.setHtml(html_content)
        layout.addWidget(text_edit)
        #print("Added label to FAQ tab")
        self.tab_widget.addTab(tab, self.t("help_window.faq_tab.title"))
    
    def get_content_stylesheet(self):
        """Return CSS stylesheet for QTextEdit content"""
        return """
        <style>
            body {{
                background-color: {window};
                color: {text};
                font-family: Arial, sans-serif;
            }}
            p {{
                color: {text};
                margin: 10px 0;
            }}
            .highlight {{
                color: {text_hightlight};
                font-weight: bold;
            }}
            .code {{
                background-color: {window};
                color: #61ab16;
                padding: 5px 8px;
                border-radius: 4px;
                font-family: monospace;
            }}
            ul {{
                color: {text};
            }}
            li {{
                margin: 5px 0;
            }}
        </style>
        """
    
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
        print("Opening HelpWindow")
        if self.is_hidden:
            print("Initially hidden, showing window")
            self.is_hidden = False
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            print("HelpWindow already open, raising to front")
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            self.raise_()           # Brings the widget to the top of the stack
            self.activateWindow()    # Gives the window keyboard focus   
            self.flash_window()
        return self
    def reject(self):
        self.close()

    def closeEvent(self, event):
        self.state_manager.app_state.on_help_dialog_close()
        self.is_hidden = True
        event.accept()