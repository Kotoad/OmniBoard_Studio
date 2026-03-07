from Imports import (QDialog, pyqtSignal, QObject, QsciLexerPython, QFont,
                      QsciScintilla, QsciAPIs, Qt, QColor, QVBoxLayout, QWidget,
                      QPropertyAnimation, QEasingCurve, QTimer, QRect, QIcon) 
import keyword, builtins

from Imports import get_Utils
Utils = get_Utils()

class CodeEditorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_canvas = parent
        self.is_hidden = True

        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.setup_ui()
    
    def setup_ui(self):
        
        self.editor = QsciScintilla(self)
        
        # 1. FIX: Make Lexer an instance variable and give it a parent
        self.lexer = QsciLexerPython(self.editor) 
        
        self.set_theme(self.lexer, self.editor)

        self.editor.setLexer(self.lexer)

        self.editor.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)

        self.editor.setIndentationGuides(True)
        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)

        # 2. FIX: Make API an instance variable and attach it to self.lexer
        self.api = QsciAPIs(self.lexer)

        for kw in keyword.kwlist:
            self.api.add(kw)
        for builtin in dir(builtins):
            if not builtin.startswith("__"):
                self.api.add(builtin + "()")  # Add parentheses to indicate callable
        
        self.api.prepare()

        self.editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.editor.setAutoCompletionThreshold(2)
        self.editor.setAutoCompletionCaseSensitivity(False)
        self.editor.setAutoCompletionReplaceWord(False)
        self.editor.setAutoCompletionShowSingle(True)
        self.editor.setAutoCompletionFillupsEnabled(True)

        with open("File.py", "r", encoding="utf-8") as f:
            sample_code = f.read()
            self.editor.setText(sample_code)

        self.editor.SendScintilla(QsciScintilla.SCI_COLOURISE, 0, -1)

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def set_theme(self, lexer, editor):
        material_font = QFont("Monospace", 11)
        lexer.setDefaultFont(material_font)
        lexer.setFont(material_font)

        # --- 2. Base Editor Colors ---
        bg_color = QColor("#3A3A3A")          # Material Darker Background
        fg_color = QColor("#EEFFFF")          # Material Default Text
        selection_bg = QColor("#2C3941")      # Highlighted text background
        caret_color = QColor("#FFCC00")       # Yellow cursor
        current_line_bg = QColor("#2F2F2F")   # Active line highlight
        margin_fg = QColor("#4A4A4A")         # Line numbers color

        # Apply base colors to the Lexer
        lexer.setDefaultPaper(bg_color)
        lexer.setDefaultColor(fg_color)
        lexer.setPaper(bg_color)
        lexer.setColor(fg_color)

        # Apply base colors to the Editor
        editor.setPaper(bg_color)
        editor.setCaretForegroundColor(caret_color)
        editor.setCaretWidth(2)
        editor.setSelectionBackgroundColor(selection_bg)

        editor.setMarginLineNumbers(0, True)  # Turns on line numbers for margin 0
        editor.setMarginWidth(0, "00000")  # Adjust margin width based on expected line count

        editor.setFoldMarginColors(bg_color, bg_color)

        # Highlight the line the cursor is currently on
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(current_line_bg)
        # Line Numbers (Margins)
        editor.setMarginsBackgroundColor(bg_color)
        editor.setMarginsForegroundColor(margin_fg)

        editor.setMatchedBraceBackgroundColor(QColor("#1F1F1F"))  # Yellow for matched braces

        editor.setUnmatchedBraceBackgroundColor(bg_color)  # Red for unmatched braces
        editor.setUnmatchedBraceForegroundColor(QColor("#FF0000"))

        # --- 3. Material Darker Syntax Highlighting ---
        
        # Keywords (def, class, if, return...) -> Purple
        lexer.setColor(QColor("#C792EA"), QsciLexerPython.Keyword)
        
        # Classes -> Yellow/Orange
        lexer.setColor(QColor("#FFCB6B"), QsciLexerPython.ClassName)
        
        # Function & Method Names (when defining them) -> Blue
        lexer.setColor(QColor("#82AAFF"), QsciLexerPython.FunctionMethodName)
        
        # Strings -> Light Green
        string_color = QColor("#C3E88D")
        lexer.setColor(string_color, QsciLexerPython.SingleQuotedString)
        lexer.setColor(string_color, QsciLexerPython.DoubleQuotedString)
        lexer.setColor(string_color, QsciLexerPython.TripleSingleQuotedString)
        lexer.setColor(string_color, QsciLexerPython.TripleDoubleQuotedString)
        
        # Numbers -> Orange
        lexer.setColor(QColor("#F78C6C"), QsciLexerPython.Number)
        
        # Comments -> Faded Blue/Grey (You can also make them italic!)
        comment_color = QColor("#546E7A")
        lexer.setColor(comment_color, QsciLexerPython.Comment)
        lexer.setColor(comment_color, QsciLexerPython.CommentBlock)
        # Make comments italic
        italic_font = QFont("Monospace", 11)
        italic_font.setItalic(True)
        lexer.setFont(italic_font, QsciLexerPython.Comment)
        lexer.setFont(italic_font, QsciLexerPython.CommentBlock)

        # Decorators (@property, etc) -> Cyan
        lexer.setColor(QColor("#89DDFF"), QsciLexerPython.Decorator)
        
        # Operators (+, -, =, (, ), etc.) -> Cyan
        lexer.setColor(QColor("#89DDFF"), QsciLexerPython.Operator)

        # Standard identifiers and default text -> Off-White
        lexer.setColor(fg_color, QsciLexerPython.Identifier)
        lexer.setColor(fg_color, QsciLexerPython.Default)
    
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
        #print("Opening DeviceSettingsWindow")
        if self.is_hidden:
            #print("Initially hidden, showing window")
            self.is_hidden = False
            with open("File.py", "r", encoding="utf-8") as f:
                sample_code = f.read()
            if self.editor:
                self.editor.setText(sample_code)

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
        self.close()

    def closeEvent(self, event):
        self.is_hidden = True
        self.state_manager.app_state.on_code_editor_dialog_close()
        event.accept()