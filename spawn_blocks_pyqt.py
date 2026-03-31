from Imports import (QWidget, QLabel, QLineEdit, math,
QComboBox, QApplication, QStyleOptionComboBox,
pyqtProperty, QEasingCurve, QRectF,
Qt, QPoint, QPropertyAnimation, QRect,
pyqtSignal, QObject, QRegularExpression,
QPainter, QPen, QBrush, QColor, QGraphicsObject,
QPixmap, QImage, QMouseEvent, QStandardItem,
QIntValidator, QRegularExpressionValidator,
QPainterPath, QFont, QStyledItemDelegate, QSortFilterProxyModel,
QStandardItemModel, QListWidget, QEvent, ctypes, sys, time,
QGraphicsPixmapItem, QGraphicsItem, QPointF, QCursor)
import random
from Imports import get_Utils, get_Commands
Utils = get_Utils()
AddBlockCommand = get_Commands()[0]
MoveBlockCommand = get_Commands()[4]

class BlockSignals(QObject):
    """Signal container for block interactions"""
    input_clicked = pyqtSignal(object, QPointF, str)  # block, center, type
    output_clicked = pyqtSignal(object, QPointF, str)  # block, center, type
    Add_condition = pyqtSignal(object)  # block
    Remove_condition = pyqtSignal(object)  # block
    Add_network = pyqtSignal(object)  # block
    Remove_network = pyqtSignal(object)  # block

#MARK: - BlockGraphicsItem
class BlockGraphicsItem(QGraphicsObject):
    """Graphics item representing a block - renders with QPainter for perfect zoom quality"""

    def __init__(self, x, y, block_id, block_type, parent_canvas, GUI=None, name=None, conditions=1, networks=2):
        super().__init__()
        print(f'Initializing BlockGraphicsItem: {block_id} of type {block_type} at ({x}, {y}) on canvas {parent_canvas}, name: {name if name else "N/A"}')
        self.signals = BlockSignals()
        self.state_manager = Utils.state_manager
        self.canvas = parent_canvas
        if GUI is not None:
            self.GUI = GUI
        elif hasattr(parent_canvas, 'GUI'):
            self.GUI = parent_canvas.GUI
        else:
            self.GUI = QApplication.instance().activeWindow()
        #print(f"GUI window in BlockGraphicsItem: {self.GUI}")
        self._drag_start_pos = None  # For tracking drag start position
        self.border_color = QColor("black")
        self.block_id = block_id
        self.block_type = block_type
        self.canvas_id = None
        self.name = name
        self.grid_size = 25
        self.radius = 6
        self.border_width = 2
        self.outputs = 0
        self.condition_count = conditions
        self.network_count = networks
        self.width_changed = False
        self.font = "Consolas"
        #print(f"self.canvas: {self.canvas}, self.block_id: {self.block_id}, self.block_type: {self.block_type}, self.x: {x}, self.y: {y}, self.name: {self.name}")
        self.value_1_name = "N"
        if self.block_type in ("If", "While", "Switch"):
            self.operator = "=="
        self.value_2_name = "N"
        self.result_var_name = "N"
        self.switch_state = False
        self.sleep_time = "1000"
        self.PWM_value = "50"
        # Block dimensions based on type
        self._setup_dimensions()
        
        # Set position
        x, y = self.snap_to_grid(x, y)
        self.setPos(x, y)
        
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        print(f"✓ BlockGraphicsItem created: {block_id} ({block_type}) at ({x}, {y})")

    def boundingRect(self):
        """Define the bounding rectangle for the item"""
        return QRectF(-5, -5, self.width + 15 + self.radius, self.height+10)

    def paint(self, painter, option, widget):
        """Paint the block using QPainter"""

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        #print("Calculating dimensions for block:", self.block_id)
        self._calculate_dimensions(painter)

        # Draw main block body
        #print("Drawing block body for:", self.block_id)
        self._draw_block_body(painter)
        
        # Draw text
        #print("Drawing text for:", self.block_id)
        self._draw_text(painter)
        
        # Draw connection circles
        #print("Drawing connection circles for:", self.block_id)
        self._draw_connection_circles(painter)

    def recalculate_size(self):
        """
        Force calculation of dimensions immediately.
        Call this whenever text/properties change that affect size.
        """
        # We need a painter to calculate text width, but paint() is async.
        # We create a temporary dummy painter to do the math synchronously.
        pixmap = QPixmap(1, 1)
        painter = QPainter(pixmap)
        
        # Notify Qt that geometry is about to change (Critical for update logic)
        self.prepareGeometryChange()
        
        # Run your existing calculation logic
        self._calculate_dimensions(painter)
        
        painter.end()

    def _calculate_dimensions(self, painter):
        """Recalculate block dimensions based on current properties"""
        self._setup_dimensions()
        self._calculate_width_from_text(painter)
        #self.prepareGeometryChange()

    def _setup_dimensions(self):
        
        """Set block dimensions based on type"""
        if self.block_type in ["While", "Button", "Lower", "Equal", "Not_equal", "Greater", "Greater_equal", "Lower_equal"]:
            self.width = 100
            self.height = 75
        elif self.block_type in ["Timer", "Plus", "Minus", "Multiply", "Divide", "Modulo", "Power", "Root", "Blink_LED", "PWM_LED", "Return"]:
            self.width = 150
            self.height = 50
        elif self.block_type in [ "Start", "End", "While_true", "Toggle_LED", "Switch", "LED_ON", "LED_OFF", "Plus_one", "Minus_one"]:
            self.width = 100
            self.height = 50
        elif self.block_type == "Function":
            v_count = 0
            d_count = 0
            #print(f"Utils.variables['function_canvases']: {Utils.variables['function_canvases']}")
            for canvas, canvas_info in Utils.canvas_instances.items():
                if canvas_info.get('ref') == 'function' and canvas_info.get('name') == self.name:
                    self.canvas_id = canvas_info.get('id')
                    break
            #print(f"Calculating dimensions for function block: {self.name} in canvas {self.canvas_id}")
            for f_id, f_info in Utils.variables['function_canvases'][self.canvas_id].items():
                v_count += 1
            for f_id, f_info in Utils.devices['function_canvases'][self.canvas_id].items():
                d_count += 1
            
            if v_count >= d_count:
                count = v_count
            else:
                count = d_count
            self.width = 150
            self.height = 50 + (count * 25)
        elif self.block_type == "If":
            self.width = 100
            self.height = 50 + (self.condition_count * 25)
        elif self.block_type == "Networks":
            self.width = 100
            self.height = 25 + (self.network_count * 25)
        elif self.block_type == "RGB_LED":
            self.width = 100
            self.height = 100
        else:  #Fallback for other blocks
            print(f"[Warning] Unknown block type '{self.block_type}', using default dimensions.")
            self.width = 100
            self.height = 50
        #print(f"Set dimensions for block '{self.block_id}' ({self.block_type}): width={self.width}, height={self.height}")

    def _calculate_width_from_text(self, painter):
        """Calculate required width based on text content"""
        font = QFont(self.font, 8, QFont.Weight.Normal)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        
        text_to_measure = ""
        
        # --- Determine the text string exactly as you do in _draw_text ---
        if self.block_type in ["While"]:
            text_to_measure = f"{self.value_1_name} {self.operator} {self.value_2_name}"
        elif self.block_type == "If":
            longest_condition = ""
            for i in range(1, self.condition_count + 1):
                val_a = getattr(self, f"value_{i}_1_name", "N")
                op    = getattr(self, f"operator_{i}", "==")
                val_b = getattr(self, f"value_{i}_2_name", "N")
                if i == 1:
                    condition_text = f"If {val_a} {op} {val_b}"
                else:
                    condition_text = f"Elif {val_a} {op} {val_b}"
                if len(condition_text) > len(longest_condition):
                    longest_condition = condition_text
            text_to_measure = longest_condition
        elif self.block_type == "Timer":
            text_to_measure = f"Wait {self.sleep_time} ms"
        elif self.block_type == "Switch":
            text_to_measure = f"{self.value_1_name}"
        elif self.block_type == "Button":
            text_to_measure = f"{self.value_1_name}"
        elif self.block_type in ["Plus", "Minus", "Multiply", "Divide", "Modulo", "Power", "Root", "Random_number", "Lower", "Equal", "Not_equal", "Greater", "Greater_equal", "Lower_equal"]:
            operators = {
                "Plus": "+",
                "Minus": "-",
                "Multiply": "*",
                "Divide": "/",
                "Modulo": "%",
                "Power": "^2",
                "Root": "√",
                "Random_number": "rand",
                "Lower": "<",
                "Equal": "==",
                "Not_equal": "!=",
                "Greater": ">",
                "Greater_equal": ">=",
                "Lower_equal": "<="
            }
            text_to_measure = f"{self.result_var_name} = {self.value_1_name} {operators.get(self.block_type, "E")} {self.value_2_name}"
        elif self.block_type == "Blink_LED":
            text_to_measure = f"{self.value_1_name} - {self.sleep_time} ms"
        elif self.block_type == "PWM_LED":
            text_to_measure = f"{self.value_1_name} - {self.PWM_value}"
        elif self.block_type in ["Toggle_LED", "LED_ON", "LED_OFF"]:
            text_to_measure = f"{self.value_1_name}"
        elif self.block_type == "Plus_one":
            text_to_measure = f"{self.value_1_name} + 1"
        elif self.block_type == "Minus_one":
            text_to_measure = f"{self.value_1_name} - 1"
        elif self.block_type == "RGB_LED":
            for i in range(1, 4):
                val_name = getattr(self, f"value_{i}_1_name", "N")
                PWM_value = getattr(self, f"value_{i}_2_PWM", "N")
                text = f"{val_name} - {PWM_value}"
                if len(text) > len(text_to_measure):
                    text_to_measure = text
        elif self.block_type == "Return":
            text_to_measure = f"Return {self.value_1_name}"
        elif self.block_type == "Function":
            longest_line = ""
            i = 1
            for v_id, v_info in Utils.variables['function_canvases'][self.canvas_id].items():
                var_text = ""
                
                ref_var_a = v_info.get('name', "N")
                main_var_a = getattr(self, f"main_var_{i}_name", "N")

                if ref_var_a != "N":
                    var_text = f"{ref_var_a}     {main_var_a}"
                if len(var_text) > len(longest_line):
                    longest_line = var_text
                i += 1

            i = 1
            for d_id, d_info in Utils.devices['function_canvases'][self.canvas_id].items():
                dev_text = ""

                ref_dev_a = d_info.get('name', "N")
                main_dev_a = getattr(self, f"main_dev_{i}_name", "N")

                if ref_dev_a != "N":
                    dev_text = f"{ref_dev_a}     {main_dev_a}"
                if len(dev_text) > len(longest_line):
                    longest_line = dev_text 
                i += 1

        # --- Update Width ---
        if text_to_measure:
            text_width = metrics.horizontalAdvance(text_to_measure)

            text_width = (math.ceil(text_width/self.grid_size)*self.grid_size)+25
            width = self.width
            self.width = max(self.width, text_width)
            if self.width != width:
                self.width_changed = True
            #print(f"Calculated text width for block '{self.block_id}' ({self.block_type}): {text_width}, setting block width to: {self.width}")

    def _get_block_color(self):
        """Get color for block type"""
        colors = {
            "Start": QColor("#90EE90"),      # Light green
            "End": QColor("#FF6B6B"),        # Red
            "Timer": QColor("#02B488"),     # Sky blue
            "If": QColor("#87CEEB"),        # Sky blue
            "While": QColor("#87CEEB"),     # Sky blue
            "Switch": QColor("#87CEEB"),    # Sky blue
            "Button": QColor("#D3D3D3"),    # Light gray
            "While_true": QColor("#87CEEB"),     # Sky blue
            "Function": QColor("#FFA500"),  # Orange
            "Plus": QColor("#9900FF"),  # Purple
            "Minus": QColor("#9900FF"),  # Purple
            "Multiply": QColor("#9900FF"),  # Purple
            "Divide": QColor("#9900FF"),  # Purple
            "Modulo": QColor("#9900FF"),  # Purple
            "Power": QColor("#9900FF"),  # Purple
            "Root": QColor("#9900FF"),  # Purple
            "Random_number": QColor("#9900FF"),  # Purple
            "Lower": QColor("#9900FF"),  # Purple
            "Equal": QColor("#9900FF"),  # Purple
            "Not_equal": QColor("#9900FF"),  # Purple
            "Greater": QColor("#9900FF"),  # Purple
            "Greater_equal": QColor("#9900FF"),  # Purple
            "Lower_equal": QColor("#9900FF"),  # Purple
            "Blink_LED": QColor("#57A139"),      # Green
            "Toggle_LED": QColor("#57A139"),     # Green
            "PWM_LED": QColor("#57A139"),        # Green
            "RGB_LED": QColor("#57A139"),        # Green
            "LED_ON": QColor("#57A139"),   # Green
            "LED_OFF": QColor("#57A139"),    # Green
            "Networks": QColor("#00CED1"),       # Dark turquoise
            "Return": QColor("#90EE90")       # Light green
    
        }
        return colors.get(self.block_type, QColor("#FFD700"))  # Default yellow

    def _draw_block_body(self, painter):
        """Draw the main rounded rectangle body"""
        color = self._get_block_color()
        
        # Draw filled rounded rectangle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(self.border_color, self.border_width))
        
        # Main body rectangle
        body_rect = QRectF(self.radius, 0, self.width, self.height)
        painter.drawRoundedRect(body_rect, 3, 3)

    def _draw_text(self, painter):
        """Draw block label text"""
        #print("Drawing text for block:", self.block_type)
        painter.setPen(QPen(QColor("black")))
        font = QFont(self.font, 8, QFont.Weight.Normal)
        painter.setFont(font)
        
        # Determine text
        name = self.block_type.replace("_", " ")
        # Draw text centered
        if self.block_type in ["While"]:
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter, name)
            text_rect2 = QRectF(self.radius, 0, self.width, self.height)
            condition_text = f"{self.value_1_name} {self.operator} {self.value_2_name}"
            painter.drawText(text_rect2, Qt.AlignmentFlag.AlignCenter, condition_text)
        elif self.block_type == "Timer":
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            timer_text = f"Wait {self.sleep_time} ms"
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, timer_text)
        elif self.block_type == "Button":
            ON_rect = QRectF(self.radius, 5, self.width-10, self.height)
            OFF_rect = QRectF(self.radius, 0, self.width-10, self.height-5)
            device_text = f"{self.value_1_name}"
            painter.drawText(QRectF(self.radius+5, 5, self.width, self.height), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading, name)
            painter.drawText(QRectF(self.radius, 0, self.width, self.height), Qt.AlignmentFlag.AlignCenter, device_text)
            painter.drawText(ON_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, "ON")
            painter.drawText(OFF_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, "OFF")
        elif self.block_type == "Function":
            #print(f"Drawing function block text for: {self.block_type}")
            name_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignHCenter, self.name)

            # Draw variable/device list
            small_font = QFont(self.font, 8)
            painter.setFont(small_font)
            y_offset = 25

            # Draw internal variables and devices on left
            for v_id, v_info in Utils.variables['function_canvases'][self.canvas_id].items():
                #print(f"   Drawing variable: {v_info['name']}")
                var_text = f"{v_info['name']}"
                var_rect = QRectF(self.radius + 10, y_offset, self.width - 20, 15)
                painter.drawText(var_rect, Qt.AlignmentFlag.AlignLeft, var_text)
                y_offset += 25
            y_offset = 25
            for d_id, d_info in Utils.devices['function_canvases'][self.canvas_id].items():
                #print(f"   Drawing device: {d_info['name']}")
                dev_text = f"{d_info['name']}"
                dev_rect = QRectF(self.radius + 10, y_offset, self.width - 20, 15)
                painter.drawText(dev_rect, Qt.AlignmentFlag.AlignRight, dev_text)
                y_offset += 25
            
            y_offset = 25


            if self.canvas.reference == 'canvas':
                if Utils.main_canvas['blocks'].get(self.block_id, {}).get('internal_vars', {}).get('main_vars') is None:
                    #print(f"Warning: No main_vars found in block_data for block '{self.name}'")
                    if self.canvas.reference == 'canvas':
                        data = Utils.project_data.main_canvas['blocks'].get(self.block_id, {})
                else:
                    data = Utils.main_canvas['blocks'].get(self.block_id, {})
            elif self.canvas.reference == 'function':
                for f_id, f_info in Utils.functions.items():
                    if self.canvas == f_info.get('canvas'):
                        if f_info['blocks'].get(self.block_id, {}).get('internal_vars', {}).get('main_vars') is None:
                            #print(f"Warning: No main_vars found in block_data for block '{self.name}' in function canvas")
                            data = f_info['blocks'].get(self.block_id, {})
                        else:
                            data = f_info['blocks'].get(self.block_id, {})
                        break
            
            #print(f"Data for function block '{self.name}': {data}")
            # Draw main variables and devices on right
            for i in range(1, len(Utils.variables['function_canvases'][self.canvas_id]) + 1):
                main_var_text = f"{getattr(self, f'main_var_{i}_name', 'N')}"
                main_var_rect = QRectF(self.radius + self.width - 20 - painter.fontMetrics().boundingRect(main_var_text).width(), y_offset, painter.fontMetrics().boundingRect(main_var_text).width(), 15)
                painter.drawText(main_var_rect, Qt.AlignmentFlag.AlignLeft, main_var_text)
                y_offset += 25

            for i in range(1, len(Utils.devices['function_canvases'][self.canvas_id]) + 1):
                main_dev_text = f"{getattr(self, f'main_dev_{i}_name', 'N')}"
                main_dev_rect = QRectF(self.radius + self.width - 20 - painter.fontMetrics().boundingRect(main_dev_text).width(), y_offset, painter.fontMetrics().boundingRect(main_dev_text).width(), 15)
                painter.drawText(main_dev_rect, Qt.AlignmentFlag.AlignLeft, main_dev_text)
                y_offset += 25

        elif self.block_type == "If":
            #print(f"Drawing text for If block with {self.condition_count} conditions")
            large_font = QFont(self.font, 15, QFont.Weight.Bold)
            painter.setFont(large_font)
            painter.drawText(QRectF(self.radius + 10, 0, self.width, 25), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "+")
            painter.drawText(QRectF(self.radius, 0, self.width-10, 25), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "-")
            small_font = QFont(self.font, 8)
            painter.setFont(small_font)
            y_offset = 17.5
            for i in range(1, self.condition_count + 1):
                #print(f"Drawing main condition for If block")
                val_a = getattr(self, f"value_{i}_1_name", "N")
                op    = getattr(self, f"operator_{i}", "==")
                val_b = getattr(self, f"value_{i}_2_name", "N")
                if i == 1:
                    condition_text = f"If {val_a} {op} {val_b}"
                else:
                    condition_text = f"Elif {val_a} {op} {val_b}"
                painter.drawText(QRectF(self.radius, y_offset, self.width, 15), Qt.AlignmentFlag.AlignCenter, condition_text)
                y_offset += 25
            else_text = "Else"
            painter.drawText(QRectF(self.radius, y_offset, self.width, 15), Qt.AlignmentFlag.AlignCenter, else_text)
        elif self.block_type == "Networks":
            large_font = QFont(self.font, 15, QFont.Weight.Bold)
            painter.setFont(large_font)
            painter.drawText(QRectF(self.radius + 10, 0, self.width, 25), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "+")
            painter.drawText(QRectF(self.radius, 0, self.width-10, 25), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "-")
            small_font = QFont(self.font, 8)
            painter.setFont(small_font)
            y_offset = 17.5
            for i in range(1, self.network_count + 1):
                network_text = f"Network {i}"
                painter.drawText(QRectF(self.radius, y_offset, self.width, 15), Qt.AlignmentFlag.AlignCenter, network_text)
                y_offset += 25
        elif self.block_type == "Switch":
            small_font = QFont(self.font, 8)
            painter.setFont(small_font)
            #print(f"Drawing Switch labels, state: {self.switch_state}")
            #print(f"Current block data: {Utils.main_canvas['blocks'].get(self.block_id, {})}")
            
            dev_text = f"{self.value_1_name}"
            dev_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(dev_rect, Qt.AlignmentFlag.AlignCenter, dev_text)

            on_rect = QRectF(self.radius, 0, self.width-5-2*self.radius, self.height)
            on_color = QColor("Green") if self.switch_state else QColor("Gray")
            painter.setPen(QPen(on_color))
            painter.drawText(on_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "ON")
            
            off_rect = QRectF(self.radius*2 +5, 0, self.width, self.height)
            off_color = QColor("Red") if not self.switch_state else QColor("Gray")
            painter.setPen(QPen(off_color))
            painter.drawText(off_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "OFF")
        
        elif self.block_type in ["Plus", "Minus", "Multiply", "Divide", "Modulo", "Power", "Root", "Random_number"]:
            operators = {
                "Plus": "+",
                "Minus": "-",
                "Multiply": "*",
                "Divide": "/",
                "Modulo": "%",
                "Power": "^",
                "Root": "√",
                "Random_number": "rand"
            }
            math_text = f"{self.result_var_name} = {self.value_1_name} {operators.get(self.block_type, "E")} {self.value_2_name}"
            math_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(math_rect, Qt.AlignmentFlag.AlignCenter, math_text)
        elif self.block_type in ["Lower", "Equal", "Not_equal", "Greater", "Greater_equal", "Lower_equal"]:
            operators = {
                "Lower": "<",
                "Equal": "==",
                "Not_equal": "!=",
                "Greater": ">",
                "Greater_equal": ">=",
                "Lower_equal": "<="
            }
            math_text = f"{self.value_1_name} {operators.get(self.block_type, "E")} {self.value_2_name}"
            math_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(math_rect, Qt.AlignmentFlag.AlignCenter, math_text)
        elif self.block_type in ["Plus_one", "Minus_one"]:
            if self.block_type == "Plus_one":
                math_text = f"{self.value_1_name} + 1"
            else:
                math_text = f"{self.value_1_name} - 1"
            math_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(math_rect, Qt.AlignmentFlag.AlignCenter, math_text)
        elif self.block_type in ["Toggle_LED", "LED_ON", "LED_OFF"]:
            device_text = f"{self.value_1_name}"
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, name)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignCenter, device_text)
        elif self.block_type in ["Blink_LED"]:
            device_text = f"{self.value_1_name} - {self.sleep_time} ms"
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignVCenter, name)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignCenter, device_text)
        elif self.block_type in ["PWM_LED"]:
            device_text = f"{self.value_1_name} - {self.PWM_value}"
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignVCenter, name)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignCenter, device_text)
        elif self.block_type in ["RGB_LED"]:
            y_offset = 17.5
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignVCenter, name)
            for i in range(1, 4):
                val_name = getattr(self, f"value_{i}_1_name", "N")
                PWM_value = getattr(self, f"value_{i}_2_PWM", "N")
                text = f"{val_name} - {PWM_value}"
                text_rect = QRectF(self.radius, y_offset, self.width, 15)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
                y_offset += 25
        elif self.block_type == "Return":
            return_text = f"Return {self.value_1_name}"
            return_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(return_rect, Qt.AlignmentFlag.AlignCenter, return_text)
        else:
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, name)

    def _draw_connection_circles(self, painter):
        """Draw input/output connection circles"""
        painter.setPen(QPen(QColor("black"), self.border_width))
        self.outputs = 0 
        # Input circle (white)
        if self.block_type != "Start":
            in_y = self.grid_size*((self.height/self.grid_size)-1)
            
            in_circle = QRectF(0, in_y - self.radius, 2*self.radius, 2*self.radius)
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(in_circle)
        
        # Output circle(s) (red)
        if self.block_type != "End":
            painter.setBrush(QBrush(QColor("red")))
            if self.block_type in ["While", "Button", "Lower", "Equal", "Not_equal", "Greater", "Greater_equal", "Lower_equal"]:
                for i in range(1, 3):
                    out_y = i * self.grid_size
                    out_circle = QRectF(self.width, out_y - self.radius, 2*self.radius, 2*self.radius)
                    painter.drawEllipse(out_circle)
                    self.outputs += 1

            elif self.block_type == "If":
                for i in range(1, self.condition_count + 2):
                    out_y = i * self.grid_size
                    out_circle = QRectF(self.width, out_y - self.radius, 2*self.radius, 2*self.radius)
                    painter.drawEllipse(out_circle)
                    self.outputs += 1
                    
            elif self.block_type == "Networks":
                for i in range(1, self.network_count + 1):
                    out_y = i * self.grid_size
                    out_circle = QRectF(self.width, out_y - self.radius, 2*self.radius, 2*self.radius)
                    painter.drawEllipse(out_circle)
                    self.outputs += 1
            else:
                out_y = self.grid_size
                out_circle = QRectF(self.width, out_y - self.radius, 2*self.radius, 2*self.radius)
                painter.drawEllipse(out_circle)
                self.outputs += 1

            # Update Utils data if changed
            if self.canvas.reference == 'canvas':
                if self.block_id in Utils.main_canvas['blocks']:
                    current_stored = Utils.main_canvas['blocks'][self.block_id].get('outputs')
                    if current_stored != self.outputs:
                        Utils.main_canvas['blocks'][self.block_id]['outputs'] = self.outputs
            elif self.canvas.reference == 'function':
                for f_id, f_info in Utils.functions.items():
                    if self.canvas == f_info.get('canvas'):
                        if self.block_id in f_info['blocks']:
                            f_info['blocks'][self.block_id]['outputs'] = self.outputs
                        break
    #MARK: - Event Handling
    def connect_graphics_signals(self):
        """Connect graphics item circle click signals to event handler"""
        if hasattr(self.canvas, 'blocks_events'):
            events = self.canvas.blocks_events
            try:
                # Directly connect THIS instance's signals, bypassing the Utils dictionary entirely!
                self.signals.input_clicked.connect(events.on_input_clicked)
                self.signals.output_clicked.connect(events.on_output_clicked)
                
                if self.block_type == "If":
                    self.signals.Add_condition.connect(events.on_add_condition)
                    self.signals.Remove_condition.connect(events.on_remove_condition)
                elif self.block_type == "Networks":
                    self.signals.Add_network.connect(events.on_add_network)
                    self.signals.Remove_network.connect(events.on_remove_network)
                    
                print(f"✓ Signals successfully connected for {self.block_id}")
            except Exception as e:
                print(f"Error connecting signals for {self.block_id}: {e}")

    def snap_to_grid(self, x, y):
        #Snap coordinates to the nearest grid intersection
        
        height = self.height     
        grid_height = (round(height/self.grid_size))*self.grid_size
        #print(f"Widget height: {height}, Calculated grid height: {grid_height}")
        if height > grid_height:
            #print("Increasing grid height by one grid size")
            grid_height += self.grid_size
        elif height < self.grid_size:
            #print("Height less than grid size, setting to grid size")
            grid_height += self.grid_size
        #print(f"Height: {height}, Grid height: {grid_height}")
        """round_x = round(x / self.grid_size)
        round_y = round(y / self.grid_size) 
        Grid_rounded_x = (round_x * self.grid_size)
        Grid_rounded_y = (round_y * self.grid_size)
        Grid_rounded_y_height_offset = Grid_rounded_y + height_offset
        snapped_x = int(Grid_rounded_x)
        snapped_y = int(Grid_rounded_y_height_offset)
        print(f"snapped before adjustment: {snapped_x}, {snapped_y}")
        print(f"Differences: {abs(x - snapped_x)}, {abs(y - snapped_y)}")"""
        
            
        snapped_x = int(round(x / self.grid_size) * self.grid_size - self.radius)
        #print(f"Snapped X before adjustment: {snapped_x}, Difference: {abs(x - snapped_x)}")
        snapped_y = int((round(y / self.grid_size) * self.grid_size))
        #print(f"Snapped Y before adjustment: {snapped_y}, Difference: {abs(y - snapped_y)}")
        if (abs(y - snapped_y)) > (self.grid_size/2):
            #print("Adjusting snapped_y upwards")
            snapped_y = int(snapped_y - self.grid_size)
        """print(f"Original {x}, {y}") 
        print(f"Rounded {round_x}, {round_y}")
        print(f"Grid {Grid_rounded_x, Grid_rounded_y}")
        print(f"Grid + height_offset {Grid_rounded_y_height_offset}")"""
        #print(f"Snapped {snapped_x}, {snapped_y}")
        return snapped_x, snapped_y

    def itemChange(self, change, value):
        """Handle position/selection changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # Snap to grid on move
            new_pos = value
            snapped_x, snapped_y = self.snap_to_grid(new_pos.x(), new_pos.y())
            return QPointF(snapped_x, snapped_y)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.state_manager.canvas_state.on_moving_item():
                #print(f"Block {self.block_id} moved to {value}")
                #print(f"Z value before move: {self.zValue()}")
                self.setZValue(1)  # Bring to front while moving
                #print(f"Z value {self.zValue()} set for moving block {self.block_id}")
                pos = self.pos()
                pos_x = pos.x()
                pos_y = pos.y()
                if self.canvas.reference == 'canvas':
                    if self.block_id in Utils.main_canvas['blocks']:
                        Utils.main_canvas['blocks'][self.block_id]['x'] = pos_x
                        Utils.main_canvas['blocks'][self.block_id]['y'] = pos_y
                else:
                    for f_id, f_info in Utils.functions.items():
                        if self.canvas == f_info.get('canvas'):
                            if self.block_id in f_info['blocks']:
                                f_info['blocks'][self.block_id]['x'] = pos_x
                                f_info['blocks'][self.block_id]['y'] = pos_y
                                break
                
                # Update connected paths
                if hasattr(self.canvas, 'path_manager'):
                    self.canvas.path_manager.update_paths_for_widget(self)
                

                if hasattr(self.canvas, 'inspector_frame_visible') and self.canvas.inspector_frame_visible:
                    if self.canvas.last_inspector_block and self.canvas.last_inspector_block.block_id == self.block_id:
                        self.GUI.update_pos(self.canvas.last_inspector_block)
        
        return super().itemChange(change, value)
    #MARK: - Mouse Events
    def mousePressEvent(self, event):
        """Handle block selection and circle clicks"""
        local_pos = event.pos()
        clicked = self.where_clicked(local_pos)
        
        self._drag_start_pos = self.pos()  # Store initial position for potential move

        print(f"Mouse press at {local_pos}, detected circle: {clicked}")
        
        if event.button() == Qt.MouseButton.LeftButton:
            if clicked and (clicked.startswith('out') or clicked.startswith('in')):
                circle_center = self._get_circle_center(clicked)  # Get base type for center calculation
                if isinstance(circle_center, tuple):
                    circle_center = QPointF(circle_center[0], circle_center[1])
                
                if clicked.startswith('in'):
                    print(f" → Input circle clicked: {clicked} at {circle_center}")
                    self.signals.input_clicked.emit(self, circle_center, clicked)
                elif clicked.startswith('out'):
                    print(f" → Output circle clicked: {clicked} at {circle_center}")
                    self.signals.output_clicked.emit(self, circle_center, clicked)
                self.ungrabMouse()
                event.accept()
                return  # Prevent further processing if circle clicked
            elif clicked in ('add_condition', 'remove_condition'):
                if clicked == 'add_condition':
                    #print(" → Add condition clicked")
                    self.signals.Add_condition.emit(self)
                else:
                    #print(" → Remove condition clicked")
                    self.signals.Remove_condition.emit(self)
                event.accept()
                return  # Prevent further processing if add/remove clicked
            elif clicked in ('add_network', 'remove_network'):
                if clicked == 'add_network':
                    #print(" → Add network clicked")
                    self.signals.Add_network.emit(self)
                else:
                    #print(" → Remove network clicked")
                    self.signals.Remove_network.emit(self)
                event.accept()
                return  # Prevent further processing if add/remove clicked
        self.setSelected(True)
        event.accept()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle block deselection"""
        self.setSelected(False)

        if hasattr(self, '_drag_start_pos') and self._drag_start_pos != self.pos():
            command = MoveBlockCommand(self, self._drag_start_pos, self.pos())
            self.GUI.main_window.undo_stack.push(command)

        print("Current state before release:", self.state_manager.canvas_state.current_state())
        if self.state_manager.canvas_state.current_state() == 'MOVING_ITEM':
            print("Setting state to IDLE after move")
            self.setZValue(0)  # Reset Z value after moving
            self.state_manager.canvas_state.on_idle()
        super().mouseReleaseEvent(event)
    
    #MARK: - Hover Events
    def hoverEnterEvent(self, event):
        # Change color or show handle when mouse touches block
        #print("Mouse entered block!")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.border_color = QColor("blue")
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # Reset color when mouse leaves
        #print("Mouse left block!")
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.border_color = QColor("black")
        self.update()
        super().hoverLeaveEvent(event)

    def where_clicked(self, pos):
        """Determine if click is on input/output circle"""
        circle_type = self._check_click_on_circle(pos)
        add_remove_condition = self._check_click_on_add_remove_condition(pos)
        add_remove_network = self._check_click_on_add_remove_network(pos)
        if circle_type:
            #print(f"Click detected on circle: {circle_type}")
            return circle_type
        if add_remove_condition:
            #print(f"Click detected on add/remove condition: {add_remove_condition}")
            return add_remove_condition
        if add_remove_network:
            #print(f"Click detected on add/remove network: {add_remove_network}")
            return add_remove_network

    def _check_click_on_add_remove_condition(self, click_pos):
        """Check if click is on add/remove condition areas for If blocks"""
        if self.block_type != "If":
            return None

        add_rect = QRectF(self.radius*2 + 2, 5, 15, 15)
        remove_rect = QRectF(self.width - self.radius*2 -2, 5, 15, 15)
        
        if add_rect.contains(click_pos):
            return 'add_condition'
        if remove_rect.contains(click_pos):
            return 'remove_condition'
        
        return None

    def _check_click_on_add_remove_network(self, click_pos):
        """Check if click is on add/remove network areas for Networks blocks"""
        if self.block_type != "Networks":
            return None
        add_rect = QRectF(self.radius*2 + 2, 5, 15, 15)
        remove_rect = QRectF(self.width - self.radius*2 -2, 5, 15, 15)
        
        if add_rect.contains(click_pos):
            return 'add_network'
        if remove_rect.contains(click_pos):
            return 'remove_network'
        
        return None

    #MARK: - Circle Detection
    def _get_circle_center(self, circle_type):
        """Get circle center in scene coordinates"""
        radius = self.radius
        
        if circle_type == 'in':
            local_x = radius
            local_y = self.grid_size * ((self.height / self.grid_size) - 1)
        if circle_type.startswith('out'):
            if self.canvas.reference == 'canvas':
                if self.block_id in Utils.main_canvas['blocks']:
                    outputs = Utils.main_canvas['blocks'][self.block_id].get('outputs', 1)
            elif self.canvas.reference == 'function':
                for f_id, f_info in Utils.functions.items():
                    if self.canvas == f_info.get('canvas'):
                        if self.block_id in f_info['blocks']:
                            outputs = Utils.functions[f_id]['blocks'][self.block_id].get('outputs', 1)
            number = int(circle_type.split('_')[1])
            print(f"Calculating circle center for output {number} of {outputs} outputs")
            local_x = self.width
            local_y = self.grid_size * (number)
        
        # Convert to scene coordinates
        print(f"Local coordinates for {circle_type} circle: ({local_x}, {local_y})")
        scene_pos = self.mapToScene(local_x, local_y)
        return (scene_pos.x(), scene_pos.y())

    def _check_click_on_circle(self, click_pos, radius_margin=5):
        """
        Determine which circle (if any) was clicked
        Returns: 'in', 'out', 'out1', 'out2', or None
        """
        effective_radius = self.radius + radius_margin
        
        in_x, in_y = self.radius, self.height - self.grid_size
        dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
        if dist_in <= effective_radius:
            return 'in'
        
        # Check output circles
        out_x = self.width + self.radius
        
        if self.block_type in ('While', 'Button', 'Lower', 'Equal', 'Not_equal', 'Greater', 'Greater_equal', 'Lower_equal'):
            # Two output circles
            out_y1 = self.grid_size * ((self.height / self.grid_size) - 2)
            out_y2 = self.grid_size * ((self.height / self.grid_size) - 1)
            
            dist_out1 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y1)**2)**0.5
            dist_out2 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y2)**2)**0.5
            
            if dist_out1 <= effective_radius:
                return 'out_1'
            if dist_out2 <= effective_radius:
                return 'out_2'
        elif self.block_type == 'If':
            # Multiple output circles based on condition count
            helper = 1
            for i in reversed(range(1, self.condition_count + 2)):
                print(i, helper)
                out_y = self.grid_size * ((self.height / self.grid_size) - (i))
                dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
                if dist_out <= effective_radius:
                    return f'out_{helper}'
                helper += 1
        elif self.block_type == 'Networks':
            # Multiple output circles based on network count
            helper = 1
            for i in reversed(range(1, self.network_count + 1)):
                out_y = self.grid_size * ((self.height / self.grid_size) - (i))
                dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
                if dist_out <= effective_radius:
                    return f'out_{helper}'
                helper += 1
        else:
            # Standard output at center height
            out_y = self.grid_size
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            if dist_out <= effective_radius:
                return 'out_1'
        
        return None
    
#MARK: - spawning_blocks
class spawning_blocks:
    """Handles spawning and placing blocks on the canvas"""
    def __init__(self, parent, blocks_window=None):
        self.placing_active = False
        self.perm_stop = False
        self.parent = parent
        self.blocks_window = blocks_window
        self.element_spawner = Element_spawn()
        self.path_manager = parent.path_manager if hasattr(parent, 'path_manager') else None
        self.state_manager = Utils.state_manager
        self.ghost_block = None

    def start(self, parent, element_type, name=None):
        """Start placing an element"""
        #print(f"Before: {parent.mousePressEvent}")
        if not hasattr(self, 'old_mousePressEvent'):
            self.old_mousePressEvent = parent.mousePressEvent
            parent.mousePressEvent = self.on_mouse_press
        elif self.placing_active == False:
            self.old_mousePressEvent = parent.mousePressEvent
            parent.mousePressEvent = self.on_mouse_press
        #print(f"After: {parent.mousePressEvent}")
        self.type = element_type
        self.name = name
        self.perm_stop = False
        self.parent = parent
        self.placing_active = True
        #print("Start placement")
        #print(f"parent: {parent}, element_type: {element_type}")
        if self.blocks_window and self.blocks_window.isVisible():
            self.blocks_window.is_hidden = True
            self.blocks_window.hide()

        global_pos = QCursor.pos()

        local_pos = parent.viewport().mapFromGlobal(global_pos)

        local_point = QPointF(local_pos.x(), local_pos.y())

        self.ghost_block = self.element_spawner.custom_shape_spawn(parent, element_type, QMouseEvent(QEvent.Type.MouseButtonPress, local_point, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier), name)

        self.ghost_block.setOpacity(0.7)
        self.ghost_block.setZValue(1000)

        parent.setFocus()
        #print(f"Canvas enabled: {parent.isEnabled()}")
        parent.raise_()
        #print("Canvas raised to top")

    def update_position(self, scene_pos):
        """Update position of the floating block (called by Canvas MouseMove)"""
        if self.ghost_block and self.placing_active:
            # Snap to grid using the block's internal logic
            snapped_x, snapped_y = self.ghost_block.snap_to_grid(scene_pos.x(), scene_pos.y())
            self.ghost_block.setPos(snapped_x, snapped_y)

    def on_mouse_press(self, event):
        #print("Mouse Pressed")
        if event.button() == Qt.MouseButton.LeftButton:
            self.place(event)

    def place(self, event):
        """Place the element at clicked position"""
        #print("Placement started")
        
        if self.perm_stop:
            return

        if self.placing_active and self.ghost_block:
            # 2. Update Data in Utils (Sync position)
            # The block was added to Utils in start(), but its position has changed.
            final_pos = self.ghost_block.pos()
            block_id = self.ghost_block.block_id

            self.parent.remove_block(block_id)
            self.ghost_block = None
            
            print(f"self.parent: {self.parent} type: {type(self.parent)}, self.type: {self.type} type {type(self.type)}, final_pos: ({final_pos.x()} type {type(final_pos.x())}, {final_pos.y()} type {type(final_pos.y())}), block_id: {block_id} type {type(block_id)}, name: {self.name} type {type(self.name)}")
        
            command = AddBlockCommand(
                canvas=self.parent,
                block_type=self.type,
                x=final_pos.x(),
                y=final_pos.y(),
                block_id=block_id,
                name=self.name
            )
            self.parent.GUI.main_window.undo_stack.push(command)

            if self.parent.reference == 'canvas':
                 if block_id in Utils.main_canvas['blocks']:
                     Utils.main_canvas['blocks'][block_id]['x'] = final_pos.x()
                     Utils.main_canvas['blocks'][block_id]['y'] = final_pos.y()
            elif self.parent.reference == 'function':
                 for f_id, f_info in Utils.functions.items():
                    if self.parent == f_info.get('canvas'):
                        if block_id in f_info['blocks']:
                            f_info['blocks'][block_id]['x'] = final_pos.x()
                            f_info['blocks'][block_id]['y'] = final_pos.y()
                        break

            self.start(self.parent, self.type, self.name)  # Start new placement for next block

    def stop_placing(self, parent):
        """Stop placement mode"""
        #print("Placement stopped")
        
        # 1. Remove the floating block if it exists
        if self.ghost_block:
            #print(f"Removing cancelled block: {self.ghost_block.block_id}")
            parent.remove_block(self.ghost_block.block_id)
            self.ghost_block = None

        self.perm_stop = True
        self.placing_active = False
        
        #print("Current state before idle:", self.state_manager.canvas_state.current_state())
        self.state_manager.canvas_state.on_idle()
        #print("Current state after idle:", self.state_manager.canvas_state.current_state())
        #print(f"Current mousePressEvent: {parent.mousePressEvent}, Restoring old mousePressEvent: {self.old_mousePressEvent}")
        parent.mousePressEvent = self.old_mousePressEvent
        #print(f"mousePressEvent restored: {parent.mousePressEvent}")
        if self.blocks_window:
            #print("Re-opening blocksWindow")
            self.blocks_window.is_hidden = True
            self.blocks_window.open()

#MARK: - blocks_events
class blocks_events(QObject):
    """Centralized event handler for block interactions"""
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        print(f"[BlocksEvents]Initializing blocksEvents for canvas: {canvas}")
        self.path_manager = canvas.path_manager if hasattr(canvas, 'path_manager') else None
        print(f"[BlocksEvents]path_manager: {self.path_manager}, canvas path_manager: {getattr(canvas, 'path_manager', 'No path manager')}")
        self.state_manager = Utils.state_manager
        #print(f"Instantiating blocksEvents for canvas: {canvas}")
        #print(f" → inspector_panel: {self.inspector_frame_visible}")
        #print("✓ blocksEvents initialized")
        print(f"[BlocksEvents]path_manager: {self.path_manager}")

    def on_input_clicked(self, block, circle_center, circle_type):
        """Handle input circle clicks"""
        #print(f"✓ on_input_clicked: {block.block_id} ({circle_type})")
        if self.path_manager:
            #print("Current state before finalizing connection:", self.state_manager.canvas_state.current_state())
            self.path_manager.finalize_connection(block, circle_center, circle_type)
            

    def on_output_clicked(self, block, circle_center, circle_type):
        """Handle output circle clicks"""
        print(f"✓ on_output_clicked: {block.block_id} ({circle_type})")
        if self.path_manager:
            print("Current state before adding path:", self.state_manager.canvas_state.current_state())
            if self.state_manager.canvas_state.on_adding_path():
                print("Adding path...")
                self.path_manager.start_connection(block, circle_center, circle_type)
        
    def on_add_condition(self, block):
        """Handle adding condition to If block"""
        #print(f"✓ on_add_condition for block: {block.block_id}")
        block.condition_count += 1
        block.recalculate_size()

        if self.canvas.reference == 'canvas':
            data = Utils.main_canvas['blocks'].get(block.block_id)
            if data:
                data['conditions'] = block.condition_count
                str_1 = 'value_{}_1_name'.format(block.condition_count)
                str_2 = 'operator_{}'.format(block.condition_count)
                str_3 = 'value_{}_2_name'.format(block.condition_count)
                data['first_vars'][str_1] = 'N'
                data['operators'][str_2] = '=='
                data['second_vars'][str_3] = 'N'
                for path_id, path_info in list(Utils.main_canvas['paths'].items()):
                    #print(f"Checking path {path_id} for update: {path_info}, looking for from {block.block_id} and from_circle out_{block.condition_count}")
                    if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.condition_count}':
                        #print(f"Updating path {path_id} from block {block.block_id} to new output circle out_{block.condition_count+1}")
                        Utils.main_canvas['paths'][path_id]['from_circle_type'] = f'out_{block.condition_count+1}'
                        data['out_connections'][path_id] = f'out_{block.condition_count+1}'
                        #print(f"Updated path {path_id} in main canvas to new output circle out_{block.condition_count+1}")
        elif self.canvas.reference == 'function':
            for f_id, f_info in list(Utils.functions.items()):
                if self.canvas == f_info.get('canvas'):
                    data = f_info['blocks'].get(block.block_id)
                    if data:
                        data['conditions'] = block.condition_count
                        for path_id, path_info in list(Utils.functions[f_id]['paths'].items()):
                            #print(f"Checking path {path_id} for update: {path_info}, looking for from {block.block_id} and from_circle out_{block.condition_count}")
                            if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.condition_count}':
                                #print(f"Updating path {path_id} from block {block.block_id} to new output circle out_{block.condition_count+1}")
                                Utils.functions[f_id]['paths'][path_id]['from_circle_type'] = f'out_{block.condition_count+1}'
                                data['out_connections'][path_id] = f'out_{block.condition_count+1}'
                    break
        
        self.path_manager.update_paths_for_widget(block)

        block.update()
        if hasattr(self.canvas, 'inspector_frame_visible') and self.canvas.inspector_frame_visible:
            #print(f"Updating inspector for block {block.block_id} after adding condition")
            self.canvas.GUI.update_inspector_content(block)
        
    def on_remove_condition(self, block):
        """Handle removing condition from If block"""
        #print(f"✓ on_remove_condition for block: {block.block_id}")
        if block.condition_count > 1:
            if self.canvas.reference == 'canvas':
                data = Utils.main_canvas['blocks'].get(block.block_id)
                if data:
                    data['conditions'] = block.condition_count
                    str_1 = 'value_{}_1_name'.format(block.condition_count)
                    str_2 = 'operator_{}'.format(block.condition_count)
                    str_3 = 'value_{}_2_name'.format(block.condition_count)
                    #print(f"data before deletion: {data}")
                    if str_1 in data['first_vars']:
                        del data['first_vars'][str_1]
                    if str_2 in data['operators']:
                        del data['operators'][str_2]
                    if str_3 in data['second_vars']:
                        del data['second_vars'][str_3]
                    block.str_1 = 'N'
                    block.str_2 = '=='
                    block.str_3 = 'N'
                    for path_id, path_info in list(Utils.main_canvas['paths'].items()):
                        #print(f"Checking path {path_id} for removal: {path_info}, looking for from {block.block_id} and from_circle out_{block.condition_count}")
                        if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.condition_count}':
                            self.path_manager.remove_path(path_id)
                            del Utils.main_canvas['paths'][path_id]
                            out_part, in_part = path_id.split('-')
                            if in_part in Utils.main_canvas['blocks']:
                                #print(f"Removing path from block {in_part} in main_canvas")
                                del Utils.main_canvas['blocks'][in_part]['in_connections'][path_id]
                            if out_part in Utils.main_canvas['blocks']:
                                #print(f"Removing path from block {out_part} in main_canvas")
                                del Utils.main_canvas['blocks'][out_part]['out_connections'][path_id]
                        if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.condition_count+1}':
                            #print(f"Updating path {path_id} from block {block.block_id} to new output circle out_{block.condition_count}")
                            Utils.main_canvas['paths'][path_id]['from_circle_type'] = f'out_{block.condition_count}'
                            Utils.main_canvas['blocks'][block.block_id]['out_connections'][path_id] = f'out_{block.condition_count}'
                    
            elif self.canvas.reference == 'function':
                for f_id, f_info in list(Utils.functions.items()):
                    if self.canvas == f_info.get('canvas'):
                        data = f_info['blocks'].get(block.block_id)
                        if data:
                            data['conditions'] = block.condition_count
                            str_1 = 'value_{}_1_name'.format(block.condition_count)
                            str_2 = 'operator_{}'.format(block.condition_count)
                            str_3 = 'value_{}_2_name'.format(block.condition_count)
                            if str_1 in data['first_vars']:
                                del data['first_vars'][str_1]
                            if str_2 in data['operators']:
                                del data['operators'][str_2]
                            if str_3 in data['second_vars']:
                                del data['second_vars'][str_3]
                            block.str_1 = 'N'
                            block.str_2 = '=='
                            block.str_3 = 'N'
                            for path_id, path_info in list(Utils.functions[f_id]['paths'].items()):
                                if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.condition_count}':
                                    self.path_manager.remove_path(path_id)
                                    del Utils.functions[f_id]['paths'][path_id]
                                    out_part, in_part = path_id.split('-')
                                    if in_part in Utils.functions[f_id]['blocks']:
                                        #print(f"Removing path from block {in_part} in function {f_id}")
                                        del Utils.functions[f_id]['blocks'][in_part]['in_connections'][path_id]
                                    if out_part in Utils.functions[f_id]['blocks']:
                                        #print(f"Removing path from block {out_part} in function {f_id}")
                                        del Utils.functions[f_id]['blocks'][out_part]['out_connections'][path_id]
                                if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.condition_count+1}':
                                    #print(f"Updating path {path_id} from block {block.block_id} to new output circle out_{block.condition_count}")
                                    Utils.functions[f_id]['paths'][path_id]['from_circle_type'] = f'out_{block.condition_count}'
                                    Utils.functions[f_id]['blocks'][block.block_id]['out_connections'][path_id] = f'out_{block.condition_count}'
                        break
            block.condition_count -= 1
            block.recalculate_size()
            self.path_manager.update_paths_for_widget(block)
            block.update()
            if hasattr(self.canvas, 'inspector_frame_visible') and self.canvas.inspector_frame_visible:
                #print(f"Updating inspector for block {block.block_id} after removing condition")
                self.canvas.GUI.update_inspector_content(block)
    
    def on_add_network(self, block):
        """Handle adding network to Networks block"""
        #print(f"✓ on_add_network for block: {block.block_id}")
        block.network_count += 1
        block.recalculate_size()
        if self.canvas.reference == 'canvas':
            data = Utils.main_canvas['blocks'].get(block.block_id)
            if data:
                data['networks'] = block.network_count
        elif self.canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    data = f_info['blocks'].get(block.block_id)
                    if data:
                        data['networks'] = block.network_count
                    break
        self.path_manager.update_paths_for_widget(block)
        block.update()
        if hasattr(self.canvas, 'inspector_frame_visible') and self.canvas.inspector_frame_visible:
            print(f"Updating inspector for block {block.block_id} after adding network")
            self.canvas.GUI.update_inspector_content(block)
        
    def on_remove_network(self, block):
        """Handle removing network from Networks block"""
        #print(f"✓ on_remove_network for block: {block.block_id}")
        if block.network_count > 1:
            if self.canvas.reference == 'canvas':
                data = Utils.main_canvas['blocks'].get(block.block_id)
                if data:
                    data['networks'] = block.network_count
                    for path_id, path_info in list(Utils.main_canvas['paths'].items()):
                        if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.network_count}':
                            self.path_manager.remove_path(path_id)
                            del Utils.main_canvas['paths'][path_id]
                            out_part, in_part = path_id.split('-')
                            if in_part in Utils.main_canvas['blocks']:
                                #print(f"Removing path from block {in_part} in function {f_id}")
                                del Utils.main_canvas['blocks'][in_part]['in_connections'][path_id]
                            if out_part in Utils.main_canvas['blocks']:
                                #print(f"Removing path from block {out_part} in function {f_id}")
                                del Utils.main_canvas['blocks'][out_part]['out_connections'][path_id]

            elif self.canvas.reference == 'function':
                for f_id, f_info in Utils.functions.items():
                    if self.canvas == f_info.get('canvas'):
                        data = f_info['blocks'].get(block.block_id)
                        if data:
                            data['networks'] = block.network_count
                            for path_id, path_info in list(Utils.functions[f_id]['paths'].items()):
                                if path_info['from'] == block.block_id and path_info['from_circle_type'] == f'out_{block.network_count}':
                                    self.path_manager.remove_path(path_id)
                                    del Utils.functions[f_id]['paths'][path_id]
                                    out_part, in_part = path_id.split('-')
                                    if in_part in Utils.functions[f_id]['blocks']:
                                        #print(f"Removing path from block {in_part} in function {f_id}")
                                        del Utils.functions[f_id]['blocks'][in_part]['in_connections'][path_id]
                                    if out_part in Utils.functions[f_id]['blocks']:
                                        #print(f"Removing path from block {out_part} in function {f_id}")
                                        del Utils.functions[f_id]['blocks'][out_part]['out_connections'][path_id]
    
                        break
            block.network_count -= 1
            block.recalculate_size()
            self.path_manager.update_paths_for_widget(block)
            block.update()
            if hasattr(self.canvas, 'inspector_frame_visible') and self.canvas.inspector_frame_visible:
                print(f"Updating inspector for block {block.block_id} after removing network")
                self.canvas.GUI.update_inspector_content(block)

#MARK: - Element_spawn
class Element_spawn:
    """Spawns visual blocks"""
    height = 36

    def custom_shape_spawn(self, parent, element_type, event, name=None):
        """Spawn a custom shape at the clicked position"""
        #print(f"Spawning element: {element_type}")
        block_id = f"{element_type}_{int(time.time() * 1000)}"
        scene_pos = parent.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()

        block = parent.add_block(element_type, x, y, block_id, name)
        block.prepareGeometryChange()

        return block