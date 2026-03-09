import ssl
import certifi
from random import random
import traceback as tb
import inspect
from pyboard import Pyboard, PyboardError
import urllib.request
import tempfile
from binascii import hexlify
import serial.tools.list_ports
from Imports import (
    sys, QApplication, QWidget, QVBoxLayout, QHBoxLayout, threading,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea, QListWidget, QMovie,
    QLineEdit, QComboBox, QDialog, QPainter, QPen, QColor, QBrush, pyqtProperty,
    QPropertyAnimation, QEasingCurve, QStyledItemDelegate, os, QThread, paramiko,
    QPalette, QMouseEvent, QRegularExpression, QRegularExpressionValidator, time,
    QTimer, QMessageBox, QInputDialog, QFileDialog, QFont, Qt, QPoint, ctypes,
    QRect, QSize, pyqtSignal, AppSettings, ProjectData, QCoreApplication, QSizePolicy,
    QAction, math, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem,
    QGraphicsItem, QPointF, QRectF, QPixmap, QImage, QGraphicsPixmapItem, QPainterPath, QEvent,
    QStackedWidget, QSplitter, QIcon, QKeySequence, QShortcut, json, QSplashScreen, QProgressBar,
    QScroller, QTest, QInputDevice, QEventPoint, QTouchEvent, QObject, warnings, QToolBar, QSlider,
    QIntValidator, QProgressDialog, QPixmap
)
from Imports import (
    get_Spawn_Blocks, get_Device_Settings_Mindow,
    get_Path_Manager, get_Blocks_Window, get_Utils,
    get_Help_Window, get_Code_Editor_Window, get_Commands
)
Utils = get_Utils()

BlockGraphicsItem = get_Spawn_Blocks()[0]
spawningblocks = get_Spawn_Blocks()[1]
elementevents = get_Spawn_Blocks()[2]
DeviceSettingsWindow = get_Device_Settings_Mindow()
PathManager = get_Path_Manager()[0]
PathGraphicsItem = get_Path_Manager()[1]
blocksWindow = get_Blocks_Window()
HelpWindow = get_Help_Window()
RemoveBlockCommand = get_Commands()[1]
RemovePathCommand = get_Commands()[3]

#MARK: - Threads for background tasks
class PromptPolicy(paramiko.MissingHostKeyPolicy):
    def __init__(self, execution_thread, filepath=None):
        self.execution_thread = execution_thread
        self.filepath = filepath

    def missing_host_key(self, ssh, hostname, key):

        fingerprint = hexlify(key.get_fingerprint()).decode('utf-8')
        key_name = key.get_name()

        self.execution_thread.host_key_verification.emit(hostname, key_name, fingerprint)

        self.execution_thread.key_prompt_event.wait()  # Wait for user response

        if self.execution_thread.key_prompt_accept:
            ssh._host_keys.add(hostname, key_name, key)
            ssh.save_host_keys(self.filepath)
        else:
            raise paramiko.ssh_exception.SSHException(f"Host key verification failed for {hostname} ({key_name} - {fingerprint})")

class RPiExecutionThread(QThread):
    """
    Background thread for executing code on Raspberry Pi via SSH.
    
    This thread can be stopped gracefully from the main GUI thread.
    """
    
    # Signals emitted to main GUI
    finished = pyqtSignal()  # Execution completed successfully
    error = pyqtSignal(str)  # Execution error
    output = pyqtSignal(str)  # Command output
    status = pyqtSignal(str)  # Status messages
    execution_completed = pyqtSignal(bool)  # Success/failure status
    host_key_verification = pyqtSignal(str, str, str)  # Emitted when host key verification is needed
    
    def __init__(self, ssh_config):
        """
        Initialize the execution thread.
        
        Args:
            ssh_config: dict with keys: filepath, rpi_host, rpi_user, rpi_password
        """
        super().__init__()
        self.ssh_config = ssh_config
        self.should_stop = False  # Flag to stop execution
        self.ssh = None  # SSH connection reference
        self.channel = None  # SSH channel reference
        self.stop_lock = threading.Lock()  # Thread-safe stop flag

        self.key_prompt_event = threading.Event()  # Event to wait for host key verification response
        self.key_prompt_accept = False  # Store user response for host key verification
    
    def stop(self):
        """
        Signal thread to stop gracefully.
        This is called from the main GUI thread.
        """
        print("[RPiExecutionThread]  Stop signal received")
        
        with self.stop_lock:
            self.should_stop = True
        
        # CRITICAL: Close SSH connection immediately to interrupt blocking operations
        if self.ssh is not None:
            try:
                print("[RPiExecutionThread] Closing SSH connection...")
                self.ssh.close()
            except Exception as e:
                print(f"[RPiExecutionThread] Error closing SSH: {e}")
        
        # Close channel if it exists
        if self.channel is not None:
            try:
                print("[RPiExecutionThread] Closing SSH channel...")
                self.channel.close()
            except Exception as e:
                print(f"[RPiExecutionThread] Error closing channel: {e}")
    
    def should_continue(self):
        """
        Thread-safe check if execution should continue.
        Use this instead of checking self.should_stop directly.
        """
        with self.stop_lock:
            return not self.should_stop
    
    def run(self):
        """
        Main execution method. This runs in background thread.
        """
        try:
            # ===== STEP 1: Check if stop was called before execution =====
            if not self.should_continue():
                self.status.emit("Execution cancelled before start")
                return
            
            # ===== STEP 2: Connect to RPi =====
            self.status.emit("Connecting to RPi...")
            
            try:
                ssh = paramiko.SSHClient()

                ssh_dir = Utils.get_base_path() / "Config"
                os.makedirs(ssh_dir, exist_ok=True)  # Ensure Config directory exists

                known_hosts_path = ssh_dir / "known_hosts"
                open(known_hosts_path, 'a').close()  # Ensure known_hosts file exists

                ssh.load_system_host_keys(str(known_hosts_path))  # Load existing known hosts

                custom_policy = PromptPolicy(self, str(known_hosts_path))
                ssh.set_missing_host_key_policy(custom_policy) # Reject unknown hosts for security; you can change to AutoAddPolicy if you want to allow new hosts

                self.ssh = ssh  # Store reference for cleanup
                
                # Set timeout for connection attempt
                ssh.connect(
                    self.ssh_config['rpi_host'],
                    username=self.ssh_config['rpi_user'],
                    password=self.ssh_config['rpi_password'],
                    timeout=10,  # Connection timeout
                    allow_agent=False,
                    look_for_keys=False
                )
            except paramiko.ssh_exception.SSHException as e:
                self.error.emit(f"SSH error: {str(e)}")
                self.execution_completed.emit(False)
                return
            except Exception as e:
                self.error.emit(f"Failed to connect to RPi: {str(e)}")
                self.execution_completed.emit(False)
                return
            
            # ===== STEP 3: Check if stop was called during connection =====
            if not self.should_continue():
                ssh.close()
                self.status.emit("Execution cancelled during connection")
                return

            self.status.emit("Connected to RPi")
            
            # ===== STEP 4: Upload file via SFTP =====
            try:
                self.status.emit("Uploading File.py...")
                sftp = ssh.open_sftp()
                
                # Get home directory
                stdin, stdout, stderr = ssh.exec_command("echo $HOME")
                home_dir = stdout.read().decode().strip()
                if not home_dir:
                    home_dir = f"/home/{self.ssh_config['rpi_user']}"
                
                remote_path = f"{home_dir}/File.py"
                
                # ===== STEP 5: Check if stop was called before upload =====
                if not self.should_continue():
                    sftp.close()
                    ssh.close()
                    self.status.emit("Execution cancelled before upload")
                    return
                
                # Upload file
                sftp.put(self.ssh_config['filepath'], remote_path)
                sftp.close()
                
                self.status.emit(f"Uploaded to {remote_path}")
            
            except Exception as e:
                self.error.emit(f"Failed to upload file: {str(e)}")
                self.execution_completed.emit(False)
                ssh.close()
                return
            
            # ===== STEP 6: Check if stop was called before execution =====
            if not self.should_continue():
                ssh.close()
                self.status.emit("Execution cancelled before code execution")
                return
            
            # ===== STEP 7: Execute code on RPi =====
            self.status.emit("Killing old processes...")

            self.kill_process()
            # Check if stop was called while killing
            if not self.should_continue():
                ssh.close()
                self.status.emit("Execution stopped by user")
                self.execution_completed.emit(False)
                return

            self.reset_gpio_remotely()
            
            # Give the old process time to die
            time.sleep(2.0)

            self.status.emit("Executing code...")
            
            
            try:
                # Execute Python file with timeout
                stdin, stdout, stderr = ssh.exec_command(
                    f"python3 -u {remote_path}",
                    timeout=None, get_pty=True
                )
                
                # Store channel for potential interruption
                self.channel = stdout.channel
                
                # ===== CRITICAL: Non-blocking read with stop checks =====
                # Wait for command completion while checking stop flag
                
                while not stdout.channel.exit_status_ready():
                    # Check if stop was called (every 100ms)
                    if not self.should_continue():
                        # Close channel to interrupt remote process
                        try:
                            stdout.channel.close()
                            ssh.close()
                        except:
                            pass
                        return
                    
                    # Check timeout
                    if self.channel.recv_ready():
                        # Read available data (byte by byte or chunks, but readline is easier if PTY)
                        # Since recv_ready is true, we can read.
                        # CAUTION: readline() might block if a line isn't complete. 
                        # Ideally, use a non-blocking read pattern:
                        try:
                            line = self.channel.recv(4096).decode('utf-8')
                            if line:
                                # Check if it contains your report tag
                                if '__REPORT__' in line:
                                    # Extract the JSON part and emit it specifically if needed
                                    # Or just emit raw output for now
                                    self.output.emit(line)
                                else:
                                    self.output.emit(line)
                        except Exception as e:
                            print(f"Read error: {e}")
                    # Sleep briefly to avoid busy-waiting
                    time.sleep(0.1)
                
                # Get exit code
                exit_code = stdout.channel.recv_exit_status()
                
                # ===== STEP 8: Check if stop was called during execution =====
                if not self.should_continue():
                    ssh.close()
                    self.status.emit("Execution cancelled after completion")
                    return
                
                # Read output with timeout
                output = ""
                error_output = ""
                
                try:
                    # Set a read timeout
                    stdout.channel.settimeout(5)
                    output = stdout.read().decode('utf-8', errors='ignore')
                except:
                    pass
                
                try:
                    stderr.channel.settimeout(5)
                    error_output = stderr.read().decode('utf-8', errors='ignore')
                except:
                    pass
                
                # Close SSH connection
                ssh.close()
                
                # ===== STEP 9: Handle results =====
                if exit_code == 0:
                    self.status.emit("Execution successful!")
                    if output:
                        self.output.emit(f"Output:\n{output}")
                    self.execution_completed.emit(True)
                    self.finished.emit()
                else:
                    self.status.emit(f" Execution failed (exit code: {exit_code})")
                    self.error.emit(f"Execution failed:\n{error_output}")
                    self.execution_completed.emit(False)
            
            except Exception as e:
                if self.should_continue():  # Only report error if not stopped by user
                    self.error.emit(f"Execution error: {str(e)}")
                    self.execution_completed.emit(False)
                try:
                    ssh.close()
                except:
                    pass
        
        except Exception as e:
            if self.should_continue():
                self.error.emit(f"Thread error: {str(e)}")
                self.execution_completed.emit(False)

        finally:
            if self.ssh is not None:
                try:
                    self.ssh.close()
                except:
                    pass

    def kill_process(self):
        """
        Gracefully terminate old Python processes with proper delays.
        """
        try:
            print("Terminating old processes...")
            
            # Step 1: Find the process ID (PID) first
            find_pid_cmd = "pgrep -f 'python3.*File.py'"
            stdin, stdout, stderr = self.ssh.exec_command(find_pid_cmd, timeout=3)
            pids = stdout.read().decode().strip().split('\n')
            pids = [p for p in pids if p]  # Filter empty strings
            
            if not pids:
                print("No processes to terminate")
                return
            
            print(f"Found {len(pids)} process(es): {pids}")
            
            # Step 2: Send SIGTERM to each process
            for pid in pids:
                kill_cmd = f"kill -INT {pid} 2>/dev/null || true"
                self.ssh.exec_command(kill_cmd, timeout=2)
            
            print("SIGTERM sent, waiting for graceful shutdown...")
            time.sleep(3.0)  # INCREASED: Give more time for cleanup
            
            # Step 3: Check if processes still running
            stdin, stdout, stderr = self.ssh.exec_command(find_pid_cmd, timeout=3)
            remaining = stdout.read().decode().strip().split('\n')
            remaining = [p for p in remaining if p]
            
            if remaining:
                print(f"Warning: {len(remaining)} process(es) still running")
                print("Escalating to SIGKILL...")
                
                for pid in remaining:
                    kill_cmd = f"kill -9 {pid} 2>/dev/null || true"
                    self.ssh.exec_command(kill_cmd, timeout=2)
                
                time.sleep(1.0)
                print(" GPIO cleanup may not have completed. Pin state may be dirty.")
            
            # Final check to ensure port/file descriptors are released
            time.sleep(0.5)
            print("Process termination logic complete")
        except Exception as e:
            print(f"Process termination error: {e}")



    def reset_gpio_remotely(self):
        """
        Reset GPIO pins at Linux kernel level using sysfs interface.
        This works regardless of which Python process configured the pins.
        """
        try:
            print("Executing kernel-level GPIO reset...")
            
            # Get list of all GPIO pins your application uses
            # You need to collect these from Utils.devices
            pins_to_reset = self.get_configured_pins()
            
            if not pins_to_reset:
                pins_to_reset = [17]  # Fallback to default if detection fails
            
            print(f"Resetting pins: {pins_to_reset}")
            
            # Build compound command to reset all pins
            reset_commands = []
            for pin in pins_to_reset:
                # Step 1: Unexport pin (releases from userspace control)
                reset_commands.append(f"echo {pin} > /sys/class/gpio/unexport 2>/dev/null || true")
            
            # Execute all commands in one SSH call
            full_command = " && ".join(reset_commands)
            full_command += " && echo 'GPIO reset complete'"
            
            stdin, stdout, stderr = self.ssh.exec_command(full_command, timeout=5)
            stdout.channel.recv_exit_status()  # Wait for completion
            
            output = stdout.read().decode().strip()
            errors = stderr.read().decode().strip()
            
            if output:
                print(f"Remote GPIO reset: {output}")
            if errors and "No such file" not in errors:  # Ignore "file not found" for unexported pins
                print(f"Remote GPIO errors: {errors}")
                
            time.sleep(0.5)  # Allow kernel to process changes
            
        except Exception as e:
            print(f"Remote GPIO reset failed: {e}")

    def get_configured_pins(self):
        """
        Extract list of GPIO pins used in current project.
        Returns list of pin numbers.
        """
        pins = []
        
        try:
            # Collect from main canvas devices
            for dev_id, dev_info in Utils.devices.get('main_canvas', {}).items():
                pin = dev_info.get('PIN')
                if pin is not None and pin not in pins:
                    pins.append(pin)
            
            # Collect from function canvas devices
            for func_id, func_devices in Utils.devices.get('function_canvases', {}).items():
                for dev_id, dev_info in func_devices.items():
                    pin = dev_info.get('PIN')
                    if pin is not None and pin not in pins:
                        pins.append(pin)
            
            print(f"Detected pins in project: {pins}")
        except Exception as e:
            print(f"Error detecting pins: {e}")
        
        return pins

class PicoListenerThread(QThread):
    """
    Background thread to listen to Pico W serial output after a hard reset.
    """
    output = pyqtSignal(str)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        self.ser = None

    def run(self):

        self.status.emit("Waiting for Pico to reboot...")
        time.sleep(2.0)  # Short initial wait
        
        # 2. Dynamic Port Hunting Loop
        # We will look for the Pico for up to 15 seconds
        start_time = time.time()
        new_port = None
        # 1. Wait for Pico to reboot and reappear
        while time.time() - start_time < 15:
            # Search all active ports for the Pico's USB ID (0x2E8A = RPi, 0x0005 = Pico)
            found = False
            for p in serial.tools.list_ports.comports():
                if (p.vid == 0x2E8A and p.pid == 0x0005):
                    new_port = p.device
                    found = True
                    break
            
            if found:
                break # We found it!
            
            time.sleep(0.25) # Check 4 times a second
            
        # 3. Handle specific failure (Timout or Success)
        if not new_port:
            self.status.emit(" Pico not found after reboot.")
            self.finished.emit()
            return
            
        # 4. Attempt Connection (with retries for "Access Denied" race conditions)
        for attempt in range(5):
            try:
                self.port = new_port # Update port in case it changed (e.g. COM3 -> COM4)
                self.ser = serial.Serial(self.port, 115200, timeout=1)
                self.status.emit(f"Reconnected to {self.port}")
                break
            except Exception as e:
                time.sleep(0.5)
                if attempt == 4:
                     self.status.emit(f"Connection failed: {str(e)}")
                     self.finished.emit()
                     return

        # 5. Listen loop (Same as your original code)
        self.running = True
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.output.emit(line)
                else:
                    time.sleep(0.01)
            except Exception:
                break
        
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.finished.emit()

    def stop(self):
        self.running = False

class GridScene(QGraphicsScene):
    def __init__(self, grid_size=25):
        super().__init__()
        self.grid_size = grid_size
        self.grid_color = QColor("#3A3A3A")
        self.bg_pixmap = QPixmap(self.grid_size, self.grid_size)
        self.bg_pixmap.fill(Qt.GlobalColor.transparent)

        pix_painter = QPainter(self.bg_pixmap)
        pix_painter.setPen(QPen(self.grid_color, 1))

        pix_painter.drawLine(0, 0, self.grid_size, 0)  # Horizontal line
        pix_painter.drawLine(0, 0, 0, self.grid_size)  # Vertical line
        pix_painter.end()
    
    def drawBackground(self, painter, rect):
        """
        Draw grid only for visible area
        Called automatically by Qt when rendering, and only for visible region
        """
        super().drawBackground(painter, rect)
        
        offset = QPointF(rect.x() % self.grid_size, rect.y() % self.grid_size)

        painter.drawTiledPixmap(rect, self.bg_pixmap, offset)
#MARK: - Custom widgets
class CustomSwitch(QWidget):
    """
    YOUR CustomSwitch - Has FULL control over circle size!
    """
    
    toggled = pyqtSignal(bool)
    clicked = pyqtSignal(bool)
    
    def __init__(self, parent=None, 
                 width=80, height=40,
                 bg_off_color="#e0e0e0",
                 bg_on_color="#4CAF50",
                 circle_color="#ffffff",
                 border_color="#999999",
                 animation_speed=300):
        super().__init__(parent)
        
        # State management
        self._is_checked = False
        self._circle_x = 0.0
        self._is_enabled = True
        
        self.base_width = width
        self.base_height = height
        self.circle_diameter = height - 8 
        self.padding = 4
        self.border_width = 2
        
        # Color configuration
        self.bg_off_color = bg_off_color
        self.bg_on_color = bg_on_color
        self.circle_color = circle_color
        self.border_color = border_color
        self.disabled_alpha = 0.5
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"circle_x")
        self.animation.setDuration(animation_speed)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._is_animating = False
        self.animation.stateChanged.connect(self.animation_state_changed)
        
        # Widget configuration
        self.setFixedSize(self.base_width, self.base_height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize circle position
        self._update_circle_position(animate=False)
    
    @pyqtProperty(float)
    def circle_x(self):
        return self._circle_x
    
    @circle_x.setter
    def circle_x(self, value):
        self._circle_x = value
        self.update()
    
    def animation_state_changed(self, state):
        from PyQt6.QtCore import QAbstractAnimation
    
        if state == QAbstractAnimation.State.Running:
            self._is_animating = True
        else:  # Stopped
            self._is_animating = False
    
    def set_checked(self, state, emit_signal=True):
        if self._is_checked != state:
            self._is_checked = state
            self._update_circle_position(animate=True)
            if emit_signal:
                self.toggled.emit(self._is_checked)
            self.clicked.emit(self._is_checked)
    
    def toggle(self):
        self.set_checked(not self._is_checked)
    
    def _update_circle_position(self, animate=True):
        if self._is_checked:
            end_pos = self.base_width - self.circle_diameter - self.padding
        else:
            end_pos = self.padding
        
        if animate:
            self.animation.setStartValue(self._circle_x)
            self.animation.setEndValue(end_pos)
            self.animation.start()
        else:
            self._circle_x = end_pos
    
    def mousePressEvent(self, event):
        if self._is_animating:
            event.ignore()
            return
        
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self.toggle()
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.update()
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._is_enabled:
            painter.setOpacity(self.disabled_alpha)
        
        radius = self.base_height / 2
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.base_width, self.base_height, radius, radius)
        painter.setClipPath(path)

        # 2) BACKGROUND: USE SAME OUTER RECT (NO INSET)
        bg_rect = QRectF(0, 0, self.base_width, self.base_height)
        bg_color = QColor(self.bg_on_color if self._is_checked else self.bg_off_color)
        painter.fillRect(bg_rect, bg_color)

        # 3) BORDER: DRAW ON SAME RECT & RADIUS
        border_pen = QPen(QColor(self.border_color), self.border_width)
        painter.setPen(border_pen)
        painter.drawRoundedRect(bg_rect, radius, radius)

        # 4) FOCUS RECT: SLIGHTLY INSET, SAME SHAPE
        if self.hasFocus():
            focus_pen = QPen(QColor("#2196f3"), 2, Qt.PenStyle.SolidLine)
            painter.setPen(focus_pen)
            focus_margin = 2
            focus_rect = QRectF(
                focus_margin,
                focus_margin,
                self.base_width - 2 * focus_margin,
                self.base_height - 2 * focus_margin,
            )
            painter.drawRoundedRect(focus_rect, radius - focus_margin, radius - focus_margin)

        # 5) CIRCLE
        circle_rect = QRectF(
            self._circle_x,
            self.padding,
            self.circle_diameter,
            self.circle_diameter,
        )
        painter.setBrush(QBrush(QColor(self.circle_color)))
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawEllipse(circle_rect)

        shadow_pen = QPen(QColor("#000000"), 1)
        shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(shadow_pen)
        painter.setOpacity(0.15)
        painter.drawEllipse(circle_rect.adjusted(1, 1, 1, 1))

class PassiveListPopup(QListWidget):
    """
    A list widget designed to float as a tool window without stealing focus.
    """
    selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. Window Flags: Tool (no taskbar) + Frameless + Always on Top
        self.setWindowFlags(
            Qt.WindowType.ToolTip | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.BypassWindowManagerHint
        )
        
        # 2. Attribute: Tell Qt NOT to activate this window when showing it
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 3. Focus Policy: logical focus should never be here
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Styling
        self.setStyleSheet("""
            QListWidget { 
                border: 1px solid palette(mid); 
                background: palette(base); 
                font-size: 10px;
                color: palette(text);
            }
            QListWidget::item:selected { 
                background: #0078d7; 
                color: #ffffff; 
            }
            QScrollBar:horizontal {
                height: 0px;
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 0px;
                border: none;
                background: transparent;
            }
        """)
        
        # Handle item clicks
        self.itemClicked.connect(self._on_item_clicked)
        
        # Install global filter to handle clicking outside
        QApplication.instance().installEventFilter(self)

    def showEvent(self, event):
        # Windows-specific fix to prevent activation on click
        if sys.platform == "win32":
            self._apply_windows_no_activate()
        super().showEvent(event)

    def _apply_windows_no_activate(self):
        # Set WS_EX_NOACTIVATE (0x08000000)
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            # Handle 64-bit vs 32-bit API naming
            set_window_long = user32.SetWindowLongPtrW if hasattr(user32, "SetWindowLongPtrW") else user32.SetWindowLongW
            get_window_long = user32.GetWindowLongPtrW if hasattr(user32, "GetWindowLongPtrW") else user32.GetWindowLongW
            
            ex_style = get_window_long(hwnd, GWL_EXSTYLE)
            set_window_long(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception:
            pass

    def eventFilter(self, source, event):
        # Close popup if user clicks anywhere else
        if self.isVisible() and event.type() == QEvent.Type.MouseButtonPress:
            global_pos = event.globalPosition().toPoint()
            # If click is NOT inside the popup, close it.
            # Note: We don't check the LineEdit here because the LineEdit will 
            # likely have its own logic or just keep focus naturally.
            if not self.geometry().contains(global_pos):
                self.hide()
        return super().eventFilter(source, event)

    def _on_item_clicked(self, item):
        self.selected.emit(item.text())
        self.hide()


class SearchableLineEdit(QLineEdit):
    """
    A QLineEdit that mimics a ComboBox. 
    It manages a passive popup list that filters based on input.
    """
    
    selected = pyqtSignal(str)
    MAX_WIDTH = 245  # Max width for popup
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.popup = PassiveListPopup(parent=self)
        self.popup.selected.connect(self.set_text_and_hide)
        
        self.setStyleSheet("""
        QLineEdit {
            background-color: palette(base);
            border: 1px solid palette(mid);
            border-radius: 3px;
            font-size: 10px;
            color: #333;
        }
        """)
        self.all_items = []
        
        # Connect typing events
        self.textEdited.connect(self.update_popup)
        
        self.setFixedWidth(self.MAX_WIDTH)  # Optional: set a fixed width for the line edit

    def addItem(self, text):
        self.all_items.append(str(text))

    def addItems(self, texts):
        self.all_items.clear()
        self.all_items.extend([str(t) for t in texts])
        #print(f"All items added: {self.all_items}")

    def set_text_and_hide(self, text):
        self.setText(text)
        self.popup.hide()

    def update_popup(self, text):
        """Filter items and show popup."""
        self.popup.clear()
        
        if not text:
            self.popup.hide()
            return

        # Simple case-insensitive filter
        filtered = [item for item in self.all_items if text.lower() in item.lower()]
        
        if not filtered:
            self.popup.hide()
            return

        self.popup.addItems(filtered)
        
        # Select the first item by default for easy navigation
        self.popup.setCurrentRow(0)
        
        # Position the popup
        self._move_popup()
        self.popup.show()
        #self.setFocus()  # Keep focus on the line edit

    def _move_popup(self):
        """Align popup geometry to the bottom of the line edit."""
        rect = self.rect()
        bottomleft = self.mapToGlobal(rect.bottomLeft())
        
        # Calculate popup width based on content (max 150px)
        fm = self.fontMetrics()
        max_text_width = 0
        for item_text in range(self.popup.count()):
            item = self.popup.item(item_text)
            if item:
                w = fm.horizontalAdvance(item.text())
                max_text_width = max(max_text_width, w)
        
        # Add padding and cap at max width
        popup_width = min(max_text_width + 20, self.MAX_WIDTH)
        popup_width = max(popup_width, 30)  # Minimum 30px
        
        self.popup.setFixedWidth(popup_width)  # ← Now dynamic!
        
        itemheight = self.popup.sizeHintForRow(0)
        #print(f"Item height: {itemheight}")
        count = self.popup.count()
        #print(f"Item count: {count}")
        h = min(count * itemheight, itemheight * 5)  # Max 5 items visible
        #print(f"Popup height: {h}")
        self.popup.setFixedHeight(h)
        self.popup.updateGeometry()
        self.popup.move(bottomleft)
        
    def keyPressEvent(self, event):
        """Forward navigation keys to the popup."""
        if not self.popup.isVisible():
            super().keyPressEvent(event)
            return

        if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            # Forward arrow keys to list
            current_row = self.popup.currentRow()
            count = self.popup.count()
            
            if event.key() == Qt.Key.Key_Down:
                new_row = (current_row + 1) % count
            else:
                new_row = (current_row - 1 + count) % count
                
            self.popup.setCurrentRow(new_row)
            return
        
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            # Select current item on Enter
            if self.popup.currentItem():
                self.set_text_and_hide(self.popup.currentItem().text())
            return
        
        elif event.key() == Qt.Key.Key_Escape:
            self.popup.hide()
            return
        else:
            super().keyPressEvent(event)

#MARK: - GridCanvas
class GridCanvas(QGraphicsView):
    """Canvas widget using QGraphicsView for proper zoom/pan handling"""
    
    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        #print(f"Self in GridCanvas init: {self}")
        self.grid_size = grid_size
        blocks_window = blocksWindow.get_instance(parent=self)
        self.spawner = spawningblocks(self, blocks_window)  
        print(f"[GridCanvas] spawner {self.spawner}")
        self.path_manager = PathManager(self)
        self.blocks_events = elementevents(self)
        # Create graphics scene
        self.scene = GridScene(grid_size=grid_size)
        self.scene.setSceneRect(-5000, -5000, 5000, 5000)
        self.setScene(self.scene)
        
        # Zoom setup
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        
        # Rendering
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        # Pan mode - middle mouse button
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.middle_mouse_pressed = False
        self.pan_mode = False
        self.middle_mouse_start = QPoint()
        
        # Tracking
        self.GUI = None
        self.main_window = None
        
        # Style
        self.setStyleSheet("""
            GridCanvas {
                background-color: palette(window);
            }
        """)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def draw_grid(self):
        """Draw grid background"""
        grid_size = self.grid_size
        scene_rect = self.scene.sceneRect()
        
        pen = QPen(QColor("palette(mid)"), 1)
        
        # Vertical lines
        x = int(scene_rect.left())
        while x < scene_rect.right():
            self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen)
            x += grid_size
        
        # Horizontal lines
        y = int(scene_rect.top())
        while y < scene_rect.bottom():
            self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen)
            y += grid_size
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        factor = 1.15
        if event.angleDelta().y() > 0:
            new_zoom = self.zoom_level * factor
        else:
            new_zoom = self.zoom_level / factor
        
        # Clamp to min/max
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        # Zoom toward mouse position
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.scale(new_zoom / self.zoom_level, new_zoom / self.zoom_level)
        self.zoom_level = new_zoom
        print(f"[GridCanvas.wheelEvent] GUI {self.GUI}, zoom level: {self.zoom_level}, slider value: {self.zoom_level*100}")
        self.GUI.zoom_slider.setValue(int(self.zoom_level * 100))
        event.accept()
    
    def zoom_calc(self, zoom):
        new_zoom = zoom/100
        #print(f"Calculated new zoom: {new_zoom} from input: {zoom}")
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        #print(f"Clamped new zoom: {new_zoom}")
        return new_zoom

    def zoom_change(self, zoom):
        new_zoom = self.zoom_calc(zoom)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.scale(new_zoom / self.zoom_level, new_zoom / self.zoom_level)
        self.zoom_level = new_zoom

    def reset_zoom(self):
        self.resetTransform()
        self.zoom_level = 1.0
        print(f"Resetting view to default. Zoom level: {self.zoom_level}, zoom for slider {self.zoom_level*100}")
        self.GUI.zoom_slider.setValue(int(self.zoom_level*100))

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        print(f"[GridCanvas.keyPressEvent] Key: {event.key()}")
        if event.key() == Qt.Key.Key_Home:
            # Reset zoom and pan
            self.reset_zoom()
            event.accept()
        #print(f"Spawner state: {self.spawner}, element_placed: {getattr(self.spawner, 'element_placed', None)}")
        if self.spawner and self.spawner.placing_active:
            #print(f"Key pressed: {event.key()}")
            #print(f"Element placed before: {self.spawner.element_placed}")
            if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.spawner.stop_placing(self)
                event.accept()
            else:
                event.ignore()
        elif self.path_manager.start_node:
            print(f"Key pressed during path creation: {event.key()}")
            if event.key() == Qt.Key.Key_Escape:
                self.path_manager.cancel_connection()
                event.accept()
            else:
                event.ignore()
        elif self.pan_mode:
            if event.key() == Qt.Key.Key_Escape:
                self.pan_mode = False
                self.main_window.pan_button.setChecked(False)
                print(f"pan mode {self.pan_mode}, middle mouse pressed {self.middle_mouse_pressed}")
                self.setCursor(Qt.CursorShape.ArrowCursor)
                event.accept()
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press - check for middle-click panning"""
        print(f"[GridCanvas.mousePressEvent] Button: {event.button()}")
        
        # Handle middle-click panning
        if event.button() == Qt.MouseButton.MiddleButton:
            print("[GridCanvas] Middle mouse pressed - starting pan")
            self.middle_mouse_pressed = True
            self.middle_mouse_start = event.pos()
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        
        # Handle right-click context menu
        if event.button() == Qt.MouseButton.RightButton:
            #print("[GridCanvas] Right mouse pressed - checking for context menu")
            scene_pos = self.mapToScene(event.position().toPoint())
            items = self.scene.items(scene_pos)
            #print(f"[GridCanvas] Items under cursor: {items}")
            
            for item in items:
                #print(f"[GridCanvas] Checking item: {item}")
                if isinstance(item, BlockGraphicsItem):
                    #print(f"[GridCanvas] Showing block context menu")
                    self.show_block_context_menu(item, scene_pos)
                    event.accept()
                    return  # ← Return ONLY if we showed context menu
                elif isinstance(item, PathGraphicsItem):
                    print(f"[GridCanvas] Showing path context menu")
                    self.show_path_context_menu(item, scene_pos)
                    event.accept()
                    return  # ← Return ONLY if we showed context menu
            # ← If NO menu shown, fall through to super()
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"[GridCanvas] Left mouse pressed")
            if self.path_manager.start_node:
                items = self.scene.items(self.mapToScene(event.position().toPoint()))

                click_on_block = False
                for item in items:
                    if isinstance(item, BlockGraphicsItem):
                        print(f"[GridCanvas] Completing path to block on mouse press")
                        click_on_block = True
                
                if click_on_block:
                    pass
                else:
                    print(f"[GridCanvas] Adding point to path at mouse press")
                    scene_pos = self.mapToScene(event.position().toPoint())
                    self.path_manager.add_point(scene_pos)
                    event.accept()
                    return
            if self.pan_mode:
                print(f"[GridCanvas] Starting pan mode with left click")
                self.middle_mouse_pressed = True
                self.middle_mouse_start = event.pos()
                self.setCursor(Qt.CursorShape.OpenHandCursor)
                event.accept()
                return
        # ✅ CRITICAL: Pass all other events to parent so blocks can receive them
        #print(f"[GridCanvas] Passing event to super() for block handling")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move - pan if middle-mouse pressed"""
        if self.middle_mouse_pressed:
            print(f"[GridCanvas.mouseMoveEvent] Middle mouse move - panning")
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            # Middle-mouse is held down: pan using scroll bars instead of translate
            delta = event.pos() - self.middle_mouse_start
            
            # Use scrollbars to pan - this keeps everything in sync
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y())
            )
            
            self.middle_mouse_start = event.pos()
            event.accept()
        if self.path_manager.start_node:
            # Update preview path as mouse moves
            scene_pos = self.mapToScene(event.position().toPoint())
            self.path_manager.update_preview_path(scene_pos)
        if self.spawner and self.spawner.placing_active:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.spawner.update_position(scene_pos)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release - end panning"""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Release middle-click
            self.middle_mouse_pressed = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton and self.pan_mode:
            print(f"[GridCanvas.mouseReleaseEvent] Ending pan mode with left click")
            self.middle_mouse_pressed = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            super().mouseReleaseEvent(event)
        else:
            # Other buttons
            super().mouseReleaseEvent(event)
    
    def add_block(self, block_type, x, y, block_id, name=None):
        """Add a new block to the canvas"""
        print(f"Adding block of type {block_type} at ({x}, {y}) with ID {block_id} to canvas {self}, name: {name if name else 'N/A'}")
        block = BlockGraphicsItem(
            x=x, y=y,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=self,
            GUI=self.GUI,
            name=name
        )
        
        self.scene.addItem(block)

        # Store in Utils

        info = Utils.data_control.inicilize_date(block, block_type, block_id, x, y, name)

        if self.reference == 'canvas':
            Utils.main_canvas['blocks'].setdefault(block_id, info)
            if block_type == 'If':
                for i in range(1, block.condition_count + 1):
                    str_1 = f'value_{i}_1_name'
                    str_2 = f'value_{i}_2_name'
                    str_op = f'operator_{i}'
                    Utils.main_canvas['blocks'][block_id]['first_vars'].setdefault(str_1, 'N')
                    Utils.main_canvas['blocks'][block_id]['second_vars'].setdefault(str_2, 'N')
                    Utils.main_canvas['blocks'][block_id]['operators'].setdefault(str_op, 'N')
        elif self.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                #print(f"Utils.functions key: {f_id}, value: {f_info}")
                if self == f_info.get('canvas'):
                    #print(f"Matched function canvas for block addition: {f_id}")
                    Utils.functions[f_id]['blocks'].setdefault(block_id, info)
                    break
        print(f"Added block: {info}")
        if self.reference == 'canvas':
            #print(f"Current Utils.main_canvas blocks: {Utils.main_canvas['blocks']}")
            pass
        elif self.reference == 'function':
            #print(f"Current Utils.functions[{f_id}] blocks: {Utils.functions[f_id]['blocks']}")
            pass
        block.connect_graphics_signals()
        return block

    def viewportEvent(self, event):
        """
        Intercept events sent to the viewport.
        Required because QGraphicsView receives touch events on the viewport, not the widget itself.
        """
        #print(f"[GridCanvas.viewportEvent] Event type: {event.type()}")
        if event.type() in (QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate, QEvent.Type.TouchEnd):
            # Pass the event to your custom handler
            #print(f"[GridCanvas.viewportEvent] Handling touch event: {event.type()}") 
            self.touch_event(event)
            return True # Tell Qt we handled it
        
        return super().viewportEvent(event)

    def touch_event(self, event):
        """Handle touch events for panning and zooming"""
        if event.type() == QEvent.Type.TouchBegin:
            if len(event.points()) == 1:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.middle_mouse_pressed = True
                self.middle_mouse_start = event.points()[0].position()
                event.accept()
            elif len(event.points()) == 2:
                print(f"Pinch start with points: {event.points()[0].position()}, {event.points()[1].position()}")
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self._initial_pinch_distance = (event.points()[0].position() - event.points()[1].position()).manhattanLength()
                self._initial_zoom = self.zoom_level
                event.accept()
        elif event.type() == QEvent.Type.TouchUpdate:
            if len(event.points()) == 1 and self.middle_mouse_pressed:
                delta = event.points()[0].position() - self.middle_mouse_start
                self.horizontalScrollBar().setValue(
                    int(self.horizontalScrollBar().value() - delta.x())
                )
                self.verticalScrollBar().setValue(
                    int(self.verticalScrollBar().value() - delta.y())
                )
                self.middle_mouse_start = event.points()[0].position()
                event.accept()
            elif len(event.points()) == 2:
                current_distance = (event.points()[0].position() - event.points()[1].position()).manhattanLength()
                print(f"Pinch update with current distance: {current_distance}")
                if self._initial_pinch_distance > 0:
                    print(f"Calculating zoom from pinch gesture")
                    scale_factor = current_distance / self._initial_pinch_distance
                    new_zoom = self._initial_zoom * scale_factor
                    new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
                    print(f"New zoom level from pinch: {new_zoom}")
                    self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
                    self.scale(new_zoom / self.zoom_level, new_zoom / self.zoom_level)
                    self.zoom_level = new_zoom
                    self.GUI.zoom_slider.setValue(int(self.zoom_level * 100))
                    event.accept()
        elif event.type() == QEvent.Type.TouchEnd:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.middle_mouse_pressed = False
            event.accept()
    
    def remove_block(self, block_id):
        """Remove a block from canvas"""
        try:
            current_canvas = self.GUI.current_canvas
            if not current_canvas:
                return
            
            reference = current_canvas.reference
            
            if reference == "canvas":
                block_data = Utils.main_canvas['blocks'].get(block_id)
                if block_data:
                    widget = block_data.get('widget')
                    if widget:
                        out_connections = block_data.get('out_connections', {})
                        for path_id in list(out_connections.keys()):
                            self.remove_path(path_id)
                        in_connections = block_data.get('in_connections', {})
                        for path_id in list(in_connections.keys()):
                            self.remove_path(path_id)
                        # ✅ Properly remove from scene
                        widget.setParent(None)
                        self.scene.removeItem(widget)
                        # ✅ Explicitly delete
                        widget.deleteLater()
                    
                    del Utils.main_canvas['blocks'][block_id]
            
            elif reference == "function":
                for fid, finfo in Utils.functions.items():
                    if current_canvas == finfo.get('canvas'):
                        block_data = Utils.functions[fid]['blocks'].get(block_id)
                        if block_data:
                            widget = block_data.get('widget')
                            if widget:
                                out_connections = block_data.get('out_connections', {})
                                for path_id in list(out_connections.keys()):
                                    self.remove_path(path_id)
                                in_connections = block_data.get('in_connections', {})
                                for path_id in list(in_connections.keys()):
                                    self.remove_path(path_id)
                                widget.setParent(None)
                                self.scene.removeItem(widget)
                                widget.deleteLater()
                            
                            del Utils.functions[fid]['blocks'][block_id]
                        break
        
        except Exception as e:
            print(f"Error removing block {block_id}: {e}")
            
    def remove_path(self, path_id):
        """Remove a path from canvas"""
        if self.GUI.current_canvas.reference == "canvas":
            paths = Utils.main_canvas.get('paths', {})
        elif self.GUI.current_canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.GUI.current_canvas == f_info.get('canvas'):
                    paths = Utils.functions[f_id].get('paths', {})
                    break
        print(f"paths {paths}")

        if path_id in paths:
            print(f"Removing path: {path_id}")
            path_item = paths[path_id].get('item')
            print(f"Path item to remove: {path_item}")
            if path_item:
                self.scene.removeItem(path_item)
                print(f"Path item {path_id} removed from scene.")
                out_part, in_part = path_id.split("-")
                print(f"Path connects {in_part} to {out_part}")
                if self.GUI.current_canvas.reference == "canvas":
                    if in_part in Utils.main_canvas['blocks']:
                        print(f"Removing path from block {in_part} in main_canvas")
                        del Utils.main_canvas['blocks'][in_part]['in_connections'][path_id]
                    if out_part in Utils.main_canvas['blocks']:
                        print(f"Removing path from block {out_part} in main_canvas")
                        del Utils.main_canvas['blocks'][out_part]['out_connections'][path_id]
                    
                elif self.GUI.current_canvas.reference == "function":
                    for f_id, f_info in Utils.functions.items():
                        if self.GUI.current_canvas == f_info.get('canvas'):
                            print(f"Found matching function canvas for path removal: {f_id}")
                            if in_part in Utils.functions[f_id]['blocks']:
                                print(f"Removing path from block {in_part} in function {f_id}")
                                del Utils.functions[f_id]['blocks'][in_part]['in_connections'][path_id]
                            if out_part in Utils.functions[f_id]['blocks']:
                                print(f"Removing path from block {out_part} in function {f_id}")
                                del Utils.functions[f_id]['blocks'][out_part]['out_connections'][path_id]
                            break
                    
                del paths[path_id]
    
    def show_block_context_menu(self, block, scene_pos):
        """Show context menu for blocks"""
        menu = QMenu(self)
        
        block_id = block.block_id
        
        edit_action = QAction("Edit Block", self)
        edit_action.triggered.connect(lambda: self.edit_block(block, block_id))
        #menu.addAction(edit_action)
        
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_block(block, block_id))
        #menu.addAction(duplicate_action)
        
        inspector_action = QAction("Show Inspector", self)
        inspector_action.triggered.connect(lambda: self.GUI.toggle_inspector_frame(block))
        menu.addAction(inspector_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Block", self)
        delete_action.triggered.connect(lambda: self.delete_block(block, block_id))
        menu.addAction(delete_action)
        
        # Convert scene coords to screen coords
        screen_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        menu.exec(screen_pos)
    
    def show_path_context_menu(self, path, scene_pos):
        """Show context menu for paths"""
        menu = QMenu(self)
        
        delete_action = QAction("Delete Connection", self)
        delete_action.triggered.connect(lambda: self.delete_path(path))
        menu.addAction(delete_action)
        
        screen_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        menu.exec(screen_pos)
    
    def edit_block(self, block, block_id):
        """Edit block properties"""
        #print(f"Editing block: {block_id}")
    
    def duplicate_block(self, block, block_id):
        """Create a copy of a block"""
        #TODO : Implement duplication logic
        if block_id not in Utils.top_infos:
            return
        
        block_data = Utils.top_infos[block_id]
        x = block_data['x'] + 50
        y = block_data['y'] + 50
        #print(f"Duplicating block {block_id} at ({x}, {y})")
    
    def delete_block(self, block, block_id):
        """Delete a block and its connections"""
        command = RemoveBlockCommand(self, block_id)
        self.main_window.undo_stack.push(command)

    def delete_path(self, path):
        """Delete a connection path"""
        print(f"Deleting path: {path.path_id}")
        command = RemovePathCommand(
            canvas=self,
            path_id=path.path_id
        )
        self.main_window.undo_stack.push(command)

#MARK: - Main GUI
class GUI(QWidget):
    """Main application window"""
    
    tab_changed = pyqtSignal(int)
    
    @property
    def current_canvas(self):
        """Get the currently active canvas from the sidebar"""


        caller = inspect.currentframe().f_back
        print(f"Getting current canvas. Called from: {caller.f_code.co_name} in {caller.f_code.co_filename}:{caller.f_lineno}")
        try:
            #print(f"Getting current canvas from sidebar. Current tab index: {self.get_current_tab_index()}")
            index = self.get_current_tab_index()
            for canvas, info in Utils.canvas_instances.items():
                #print(f"Canvas in Utils.canvas_instances: {canvas}, info: {info}")
                if info['index'] == index:
                    #print(f"Found current canvas in Utils.canvas_instances: {canvas}")
                    widget = info['canvas']
            #print(f"Current sidebar tab index: {index}, widget: {widget}")
            
            # Check if it's a GridCanvas instance
            if isinstance(widget, GridCanvas):
                print("Current canvas found.")
                return widget
        except Exception as e:
            print(f"Error getting current canvas: {e}")
        
        # Fallback to main canvas if property fails
        if hasattr(self, 'canvas') and self.canvas is not None:
            print("Using main canvas as fallback.")
            return self.canvas
        
        print(" No canvas available.")
        return None
        
    def __init__(self, parent=None):
        super().__init__()
        
        self.main_window = parent 
        self.t = Utils.translation_manager.translate
        self.path_manager = PathManager(self)  
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: palette(window);
                color: palette(text);
            }
            QLineEdit {
                background-color: palette(window);
                color: palette(text);
                border: 1px solid palette(base);
                border-radius: 3px;
                padding: 4px;
            }
            QComboBox {
                background-color: palette(window);
                color: palette(text);
                border: 1px solid palette(base);
                border-radius: 3px;
                padding: 4px;
            }
        """)
        self.zoom_slider = None
        self.last_canvas = None
        self.blockIDs = {}
        self.execution_thread = None
        self.pico_thread = None
        self.canvas_added = None
        self.pages = {}
        self.page_count = 0
        self.count_w_separator = 0
        self.canvas_count = 0
        self.tab_buttons = []  # Track tab buttons
        self.opend_inspectors = {}
        self.create_canvas_frame()
    
    def mousePressEvent(self, event):
        """Debug: Track if main window gets mouse press"""
        print("GUI.mousePressEvent fired!")
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Home:
            if self.current_canvas:
                self.current_canvas.reset_zoom()
            event.accept()
        else:
            super().keyPressEvent(event)

    def stop_execution(self):
        if Utils.app_settings.rpi_model_index == 0:
            print("[GUI] Stopping Pico W")
            self.stop_pico_execution()
        else:
            if self.execution_thread and self.execution_thread.isRunning():
                print("[GUI] Stopping execution thread...")
                self.execution_thread.should_stop = True
                self.execution_thread.kill_process()
                self.execution_thread.stop()

                if not self.execution_thread.wait(5000):
                    print(f"[GUI] Execution thread did not stop in time, terminating...")
                    self.execution_thread.terminate()
                    self.execution_thread.wait()
            else:
                print("[GUI] No execution thread is running.")

    def create_canvas_frame(self):
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        print(f"[GUI] Main layout created: {self.main_layout}")
        self.sidebar = self.create_sidebar()
        
        # Create a splitter for canvas + inspector
        
        self.canvas = GridCanvas()

        print(f"[GUI]Created GridCanvas instance: {self.canvas}")
        try:
            self.canvas.GUI = self
            self.canvas.main_window = self.main_window
            print(f"[GUI] Set GUI reference {self} in canvas as {self.canvas.GUI}")
        except Exception as e:
            print(f"Error setting GUI on canvas: {e}")
        
        Utils.canvas_instances[self.canvas] = {
            'name': self.t("main_GUI.sidebar.canvas"),
            'canvas': self.canvas,
            'index': 0,
            'ref': 'canvas'
        }
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.sidebar)
        
        # Rest of your code...
        self.add_tab(tab_name=self.t("main_GUI.sidebar.canvas"), content_widget=self.canvas, reference="canvas")
        self.last_canvas = self.canvas
        self.tab_changed.connect(self.on_tab_changed)
        self.set_current_tab(0, 'canvas')
    
    def simulate_pinch(self):
        viewport = self.canvas.viewport()
        center_local = QPointF(viewport.width() / 2, viewport.height() / 2)
        center_global = viewport.mapToGlobal(center_local.toPoint())
        cx, cy = center_global.x(), center_global.y()

        # Define points (Start close, Move apart)
        p1_start_pos = QPointF(cx + 10, cy)
        p2_start_pos = QPointF(cx + 10, cy)
        
        p1_end_pos = QPointF(cx + 50, cy)
        p2_end_pos = QPointF(cx + 50, cy)

        # ---------------------------------------------------------
        # 2. DEFINE MOCK CLASSES (The Fix)
        # These mimic QTouchEvent/QEventPoint behavior but guarantee data persistence
        # ---------------------------------------------------------
        class MockPoint:
            def __init__(self, pos):
                self._pos = pos
            def position(self): 
                return self._pos
            def id(self): 
                return 0 # Dummy ID

        class MockEvent:
            def __init__(self, event_type, points):
                self._type = event_type
                self._points = points
            def type(self): 
                return self._type
            def points(self): 
                return self._points
            def accept(self): 
                pass # Do nothing
            def ignore(self): 
                pass # Do nothing

        # 3. Create Mock Points wrapping your REAL QPointF objects
        # We use real QPointF so math operations (like subtraction) inside touch_event work
        mp1_start = MockPoint(p1_start_pos)
        #mp2_start = MockPoint(p2_start_pos)
        
        mp1_end = MockPoint(p1_end_pos)
        #mp2_end = MockPoint(p2_end_pos)

        # 4. Send Mock Events Directly to Handler
        print(f"Simulating Pinch Center: {cx}, {cy}")

        # A. Touch Begin
        event_begin = MockEvent(QEvent.Type.TouchBegin, [mp1_start])
        self.canvas.touch_event(event_begin)

        # B. Touch Update (The Zoom)
        event_update = MockEvent(QEvent.Type.TouchUpdate, [mp1_end])
        self.canvas.touch_event(event_update)

        # C. Touch End
        event_end = MockEvent(QEvent.Type.TouchEnd, [mp1_end])
        self.canvas.touch_event(event_end)
        
        print("Simulated Pinch Complete.")

    def on_tab_changed(self, index):
        if index not in [info['index'] for info in Utils.canvas_instances.values()]:
            #print(f"Tab index {index} not in Utils.canvas_instances indices.")
            return
        if self.current_canvas != self.last_canvas:
            #print(f"Sidebar tab changed to index: {index}, widget: {self.current_canvas}")
            try:
                if hasattr(self, 'zoom_slider') and self.current_canvas:
                    # Block signals temporarily so it doesn't trigger a zoom event just by switching tabs
                    self.zoom_slider.blockSignals(True)
                    self.zoom_slider.setValue(int(self.current_canvas.zoom_level * 100))
                    self.zoom_slider.blockSignals(False)
            except Exception as e:
                print(f"Error showing/hiding buttons on tab change: {e}")
            self.last_canvas = self.current_canvas
            
    def create_variables_panel(self, canvas_reference=None):
        """Create Variables panel"""
        canvas_reference.widget = QWidget()
        canvas_reference.layout = QVBoxLayout(canvas_reference.widget)
        canvas_reference.layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel(self.t("main_GUI.variables_tab.variables"))
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: palette(text);")
        canvas_reference.layout.addWidget(header)
        
        add_btn = QPushButton(self.t("main_GUI.variables_tab.add_variable"))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(base);
                color: palette(text);
                padding: 8px;
                border-radius: 4px;
            }
        """)
        canvas_reference.layout.addWidget(add_btn)
        
        # Scroll area
        scroll = QScrollArea()
        QScroller.grabGesture(
            scroll.viewport(), 
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll.setWidgetResizable(True)
        canvas_reference.var_content = QWidget()
        canvas_reference.var_layout = QVBoxLayout(canvas_reference.var_content)
        canvas_reference.var_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        canvas_reference.var_layout.addStretch()
        scroll.setWidget(canvas_reference.var_content)
        canvas_reference.layout.addWidget(scroll)
        add_btn.clicked.connect(lambda: self.add_variable_row(None, None, canvas_reference))
        canvas_reference.widget.setStyleSheet("""
            QWidget { background-color: palette(window); }
        """)
        return canvas_reference.widget

    def create_devices_panel(self, canvas_reference=None):
        """Create Devices panel"""
        canvas_reference.widget = QWidget()
        canvas_reference.layout = QVBoxLayout(canvas_reference.widget)
        canvas_reference.layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel(self.t("main_GUI.devices_tab.devices"))
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: palette(text);")
        canvas_reference.layout.addWidget(header)
        
        add_btn = QPushButton(self.t("main_GUI.devices_tab.add_device"))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(base);
                color: palette(text);
                padding: 8px;
                border-radius: 4px;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_device_row(None, None, canvas_reference))
        canvas_reference.layout.addWidget(add_btn)
        
        # Scroll area
        scroll = QScrollArea()
        QScroller.grabGesture(
            scroll.viewport(), 
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll.setWidgetResizable(True)
        canvas_reference.dev_content = QWidget()
        canvas_reference.dev_layout = QVBoxLayout(canvas_reference.dev_content)
        canvas_reference.dev_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        canvas_reference.dev_layout.addStretch()
        scroll.setWidget(canvas_reference.dev_content)
        canvas_reference.layout.addWidget(scroll)
        
        canvas_reference.widget.setStyleSheet("""
            QWidget { background-color: palette(window); }
        """)
        return canvas_reference.widget
    
    def create_internal_vars_panel(self, canvas_reference=None):
        """Create Internal Variables panel"""
        canvas_reference.internal_devs_rows_count = 0
        canvas_reference.widget = QWidget()
        canvas_reference.layout = QVBoxLayout(canvas_reference.widget)
        canvas_reference.layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel(self.t("main_GUI.internal_tab.header"))
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: palette(text);")
        canvas_reference.layout.addWidget(header)

        scroll = QScrollArea()
        QScroller.grabGesture(
            scroll.viewport(), 
            QScroller.ScrollerGestureType.LeftMouseButtonGesture
        )
        scroll.setWidgetResizable(True)
        canvas_reference.internal_content = QWidget()
        canvas_reference.internal_layout = QVBoxLayout(canvas_reference.internal_content)
        canvas_reference.internal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        canvas_reference.internal_layout.addStretch()
        add_internal_var_btn = QPushButton(self.t("main_GUI.internal_tab.add_internal_variable"))
        add_internal_var_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(base);
                color: palette(text);
                padding: 8px;
                border-radius: 4px;
            }
        """)
        add_internal_var_btn.clicked.connect(lambda: self.add_internal_variable_row(None, None, canvas_reference))
        canvas_reference.internal_layout.insertWidget(canvas_reference.internal_layout.count() - 1, add_internal_var_btn)
        
        add_internal_dev_btn = QPushButton(self.t("main_GUI.internal_tab.add_internal_device"))
        add_internal_dev_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(base);
                color: palette(text);
                padding: 8px;
                border-radius: 4px;
            }
        """)
    
        add_internal_dev_btn.clicked.connect(lambda: self.add_internal_device_row(None, None, canvas_reference))
        canvas_reference.internal_layout.insertWidget(canvas_reference.internal_layout.count() - 1, add_internal_dev_btn)
        scroll.setWidget(canvas_reference.internal_content)
        canvas_reference.layout.addWidget(scroll)

        canvas_reference.widget.setStyleSheet("""
            QWidget { background-color: palette(window); }
        """)

        return canvas_reference.widget

    def create_sidebar(self):
        """Initialize sidebar and content areas"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== LEFT SIDEBAR =====
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setMinimumWidth(120)
        self.sidebar_frame.setMaximumWidth(150)
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: palette(window);
                border-right: 1px solid palette(base);
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Tab buttons container (using QVBoxLayout instead of QListWidget)
        self.tab_container = QWidget()
        self.tab_layout = QVBoxLayout(self.tab_container)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSpacing(0)
        
        sidebar_layout.addWidget(self.tab_container)
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar_frame)
        
        # ===== RIGHT CONTENT AREA =====
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: palette(window);
            }
        """)
        
        main_layout.addWidget(self.content_area, stretch=1)
        # Storage
        
        
        return widget

    def add_tab(self, tab_name, content_widget=None, icon=None, reference=None, function_id=None):
        """
        Add a tab to the sidebar
        
        Args:
            tab_name: Name of the tab
            content_widget: Widget to show when tab is active
            icon: Optional QIcon for the tab
            
        Returns:
            Index of the new tab
        """
        if content_widget is None:
            content_widget = QWidget()
            layout = QVBoxLayout(content_widget)
            layout.addWidget(QLabel(f"Content for {tab_name}"))
            layout.addStretch()
        
        if reference in ["canvas", "function"]:
            #print(f"Adding canvas tab: {tab_name}")
            canvas_splitter = QSplitter(Qt.Orientation.Vertical)
            canvas_splitter.addWidget(content_widget)
            canvas_splitter.setSizes([600, 400])  # Initial sizes (canvas, inspector)
            canvas_splitter.setCollapsible(0, False)  # Canvas cannot collapse
            content_widget.canvas_splitter = canvas_splitter
            content_widget.inspector_frame = None
            content_widget.inspector_layout = None
            content_widget.inspector_frame_visible = False
            content_widget.last_inspector_block = None
            content_widget.reference = reference
            if reference == "function":
                if not function_id:
                    #print("Generating new function ID")
                    self.function_id = 'Function_'+str(int(random()*100000))
                    #print(f"Generated function ID: {self.function_id}")
                else:
                    self.function_id = function_id
                #print(f"Function ID for tab '{tab_name}': {self.function_id}")
                Utils.functions[self.function_id] = {
                    'name': tab_name,
                    'id': self.function_id,
                    'canvas': content_widget,
                    'blocks': {},
                    'paths': {}
                }
                Utils.variables['function_canvases'][self.function_id] = {}
                Utils.devices['function_canvases'][self.function_id] = {}
            elif reference == "canvas":
                Utils.main_canvas = {
                    'name': tab_name,
                    'id': 'main_canvas',
                    'canvas': content_widget,
                    'blocks': {},
                    'paths': {}
                }
            self.content_area.addWidget(canvas_splitter)
            
        else: 
            self.content_area.addWidget(content_widget)
        self.pages[tab_name] = content_widget
        
        # Create tab button
        if reference == 'variable':
            #print("Adding Variable tab button")
            #print(f"Content widget in variable tab: {content_widget}")
            self.canvas_added.var_button = QPushButton(tab_name)
            tab_button = self.canvas_added.var_button
        elif reference == 'device':
            #print("Adding Device tab button")
            #print(f"Content widget in device tab: {content_widget}")
            self.canvas_added.dev_button = QPushButton(tab_name)
            tab_button = self.canvas_added.dev_button
        elif reference == 'internal_variable':
            #print("Adding Internal Variable tab button")
            #print(f"Content widget in internal variable tab: {content_widget}")
            self.canvas_added.internal_var_button = QPushButton(tab_name)
            tab_button = self.canvas_added.internal_var_button
        elif reference in ('canvas', 'function'):
            self.canvas_added = content_widget
            self.canvas_added.canvas_tab_button = QPushButton(tab_name)
            tab_button = self.canvas_added.canvas_tab_button
            self.canvas_added = None
        else:
            tab_button = QPushButton(tab_name)
        try:
            tab_button.setStyleSheet("""
                QPushButton {
                    background-color: palette(window);
                    color: palette(text);
                    border: none;
                    padding: 12px;
                    text-align: left;
                }
                
                QPushButton:hover {
                    background-color: palette(highlight);
                }
            """)
        except Exception as e:
            print(f"Error setting stylesheet for tab button '{tab_name}': {e}")
        tab_index = self.page_count
        self.tab_buttons.append({
            'button': tab_button,
            'index': tab_index,
            'name': tab_name
        })
        #print(f"Adding tab '{tab_name}' at index {tab_index} with reference '{reference}'")
        tab_button.clicked.connect(lambda: self._on_tab_clicked(tab_index, reference))
        if reference == 'canvas':
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            self.canvas_count+=1
            self.canvas_added = content_widget
            self.add_separator(ref='reference', content_widget=content_widget)
            self.add_new_canvas_tab_button(content_widget=content_widget)
            self.add_separator(content_widget=content_widget)
            self.add_variable_tab(content_widget, self.t("main_GUI.sidebar.main"))
            self.add_device_tab(content_widget, self.t("main_GUI.sidebar.main"))
            self.add_separator(ref='reference', content_widget=content_widget)
            self.canvas_added = None
            return tab_index
        elif reference == 'function':
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            self.canvas_count+=1
            self.canvas_added = content_widget
            self.add_internal_variable_tab(content_widget, tab_name)
            self.add_separator(ref='reference', content_widget=content_widget)
            self.canvas_added = None
            return tab_index
        elif reference in ('variable', 'device', 'internal_variable'):
            self.tab_layout.insertWidget(self.count_w_separator, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            return tab_index
        else:
            self.tab_layout.addWidget(tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            return tab_index
    
    def add_variable_tab(self, canvas_reference, name):
        """Add a Variables tab to the sidebar"""
        #print("Adding Variables tab")
        variables_panel = self.create_variables_panel(canvas_reference)
        self.add_tab(name+' '+self.t("main_GUI.sidebar.variables"), variables_panel, reference="variable")
    
    def add_device_tab(self, canvas_reference, name):
        """Add a Devices tab to the sidebar"""
        #print("Adding Devices tab")
        devices_panel = self.create_devices_panel(canvas_reference)
        self.add_tab(name+' '+self.t("main_GUI.sidebar.devices"), devices_panel, reference="device")
    
    def add_internal_variable_tab(self, canvas_reference, name):
        """Add an Internal Variables tab to the sidebar"""
        #print("Adding Internal Variables tab")
        internal_vars_panel = self.create_internal_vars_panel(canvas_reference)
        self.add_tab(name+' '+self.t("main_GUI.sidebar.internal_variables"), internal_vars_panel, reference="internal_variable")

    def add_new_canvas_tab_button(self, content_widget=None):
        """Add a special button to create a new canvas tab"""
        content_widget.new_canvas_button = QPushButton(self.t("main_GUI.sidebar.new_canvas"))
        content_widget.new_canvas_button.setStyleSheet("""
            QPushButton {
                background-color: palette(window);
                color: palette(text);
                border: none;
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: palette(highlight);
            }       
        """)
        content_widget.new_canvas_button.clicked.connect(self._on_new_canvas_clicked)
        self.tab_layout.insertWidget(self.canvas_count, content_widget.new_canvas_button)
    
    def _on_new_canvas_clicked(self):
        """Handler for new canvas tab button click"""
        if not Utils.state_manager.app_state.on_tab_created():
            return

        name, ok = QInputDialog.getText(
            self,
            self.t("main_GUI.dialogs.new_canvas"),
            self.t("main_GUI.dialogs.enter_canvas_name")
        )
        if not ok or not name.strip():
            return
        new_canvas = GridCanvas()
        new_canvas.GUI = self
        new_canvas.main_window = self.main_window
        new_tab_index = self.add_tab(
            name,
            new_canvas,
            reference="function",
        )
        Utils.canvas_instances[new_canvas] = {
            'canvas': new_canvas,
            'index': new_tab_index,
            'id': self.function_id,
            'ref': 'function',
            'name': name
        }
        self.tab_changed.emit(new_tab_index)
        #print(f"Utils.canvas_instances count: {len(Utils.canvas_instances)}")
        #print(f"Utils.canvas_instances: {Utils.canvas_instances}")
        self.set_current_tab(new_tab_index, 'function')
    
    def add_separator(self, ref=None, content_widget=None):
        """Add a visual separator line with exactly 5px height"""
        if not hasattr(content_widget, 'separators'):
            content_widget.separators = []
        # Create a container for the separator
        content_widget.separator_container = QFrame()
        content_widget.separator_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        content_widget.separator_container.setFixedHeight(5)
        
        # Create the actual line
        content_widget.separator = QFrame()
        content_widget.separator.setFrameShape(QFrame.Shape.HLine)
        content_widget.separator.setFrameShadow(QFrame.Shadow.Plain)
        content_widget.separator.setLineWidth(1)
        content_widget.separator.setStyleSheet("background-color: palette(mid);")
        
        # Layout for container
        content_widget.layout = QVBoxLayout(content_widget.separator_container)
        content_widget.layout.setContentsMargins(0, 2, 0, 2)  # Vertical padding: 2px top + 2px bottom + 1px line = 5px total
        content_widget.layout.setSpacing(0)
        content_widget.layout.addWidget(content_widget.separator)
        content_widget.separators.append(content_widget.separator_container)
        if ref is None:
            self.tab_layout.insertWidget(self.canvas_count, content_widget.separator_container)
        else:
            self.tab_layout.insertWidget(self.count_w_separator, content_widget.separator_container)
            self.count_w_separator+=1
            
    def set_current_tab(self, tab_index, reference=None):
        """Switch to a specific tab by index"""
        if 0 <= tab_index < len(self.tab_buttons):
            self._on_tab_clicked(tab_index, reference)
    
    def get_current_tab_index(self):
        """Get currently active tab index"""
        return self.content_area.currentIndex()
    
    def _on_tab_clicked(self, tab_index, reference=None):
        """Internal handler for tab clicks"""
        if Utils.state_manager.app_state.on_tab_changed():
            if 0 <= tab_index < len(self.tab_buttons):
                self.content_area.setCurrentIndex(tab_index)
                
                # Update button styles
                for tb in self.tab_buttons:
                    if tb['index'] == tab_index:
                        print(f"Setting active style for tab '{tb['name']}' at index {tab_index}")
                        try:
                            tb['button'].setStyleSheet("""
                                QPushButton {
                                    background-color: palette(highlight);
                                    color: palette(highlighted-text);
                                    border: none;
                                    border-left: 3px solid palette(highlight);
                                    padding: 12px;
                                    text-align: left;
                                }
                            """)
                        except Exception as e:
                            print(f"Error setting active stylesheet for tab button '{tb['name']}': {e}")
                    else:
                        tb['button'].setStyleSheet("""
                            QPushButton {
                                background-color: palette(window);
                                color: palette(text);
                                border: none;
                                padding: 12px;
                                text-align: left;
                            }
                            QPushButton:hover {
                                background-color: palette(highlight);
                            }
                        """)
                if reference == "canvas":
                    pass
                    #print(f"Setting Utils.courent_canvas to canvas tab index {tab_index}")
                    #print(f"Utils.canvas_instances: {Utils.canvas_instances}")
                    #if tab_index - self.canvas_count < 0:
                        #tab_index = 0
                        #print(f"Courent canvas index: {tab_index}")
                        #Utils.courent_canvas = Utils.canvas_instances[tab_index]
                        #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
                    #else:
                        #print(f"Setting Utils.courent_canvas to index {tab_index - self.canvas_count+1}")
                        #Utils.courent_canvas = Utils.canvas_instances[tab_index-self.canvas_count+1]
                        #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
                Utils.state_manager.app_state.current_tab_reference = reference
                self.tab_changed.emit(tab_index)

    def open_project(self):
        if Utils.file_manager.load_project(Utils.config['opend_project'], is_autosave=True) and Utils.config['opend_project'] is not None:
            self.rebuild_from_data()

    #MARK: - Inspector Panel Methods
    def toggle_inspector_frame(self, block):
        """Toggle inspector panel based on block selection"""
        #print(f"Self in toggle_inspector_frame: {self}")
        #print(f"Current canvas in toggle_inspector_frame: {self.current_canvas}")
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        if not current_canvas.inspector_frame_visible:
            current_canvas.last_inspector_block = block
            self.show_inspector_frame(block)
        elif current_canvas.inspector_frame_visible and current_canvas.last_inspector_block != block:
            current_canvas.last_inspector_block = block
            self.update_inspector_content(block)
        else:
            # Toggle off if clicking same block
            self.hide_inspector_frame()
        
    def show_inspector_frame(self, block):
        """Show the inspector panel"""
        #print(f"Self in show_inspector_frame: {self}")
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        if not current_canvas.inspector_frame_visible:
            current_canvas.last_inspector_block = block
            
            # Get current canvas
            
            
            # Create inspector frame if it doesn't exist
            if current_canvas.inspector_frame is None:
                current_canvas.inspector_frame = QFrame()
                current_canvas.inspector_frame.setStyleSheet("""
                    QFrame {
                        background-color: palette(window);
                        border-left: 1px solid palette(base);
                    }
                """)
                current_canvas.inspector_layout = QVBoxLayout(current_canvas.inspector_frame)
                
                # Scroll area
                current_canvas.scroll_area = QScrollArea()
                QScroller.grabGesture(
                    current_canvas.scroll_area.viewport(), 
                    QScroller.ScrollerGestureType.LeftMouseButtonGesture
                )
                current_canvas.scroll_area.setWidgetResizable(True)
                current_canvas.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                current_canvas.inspector_content = QWidget()
                current_canvas.inspector_content_layout = QVBoxLayout(current_canvas.inspector_content)
                current_canvas.inspector_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                current_canvas.inspector_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                current_canvas.scroll_area.setWidget(current_canvas.inspector_content)
                
                current_canvas.inspector_layout.addWidget(current_canvas.scroll_area)
            
            # Add inspector to splitter
            current_canvas.canvas_splitter.addWidget(current_canvas.inspector_frame)
            current_canvas.canvas_splitter.setSizes([700, 300])  # Adjust initial ratio
            
            if block:
                self.update_inspector_content(block, canvas=current_canvas)
            if current_canvas not in self.opend_inspectors or self.opend_inspectors[current_canvas]!= block:
                self.opend_inspectors[current_canvas] = block

            current_canvas.inspector_frame.show()
            current_canvas.inspector_frame_visible = True


    def hide_inspector_frame(self):
        """Hide the inspector panel"""
        current_canvas = self.current_canvas
        if current_canvas:
            canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
                    
        if canvas_splitter and current_canvas.inspector_frame:
            if current_canvas in self.opend_inspectors:
                del self.opend_inspectors[current_canvas]
            current_canvas.inspector_frame.hide()
            
            # Get current canvas and its splitter
            if canvas_splitter:
                canvas_splitter.setSizes([1000, 0])  # Hide inspector
            
            current_canvas.inspector_frame_visible = False

    def update_inspector_content(self, block, canvas=None):
        """Update the content of the inspector panel based on the selected block"""
        print(f"Getting inspector content for block: {block}")
        current_canvas = self.current_canvas if canvas is None else canvas
        print(f"Current canvas in update_inspector_content: {current_canvas}")
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        # Clear ONLY the content layout, NOT the main inspector layout
        while current_canvas.inspector_content_layout.count():
            item = current_canvas.inspector_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Remove spacer items
        for i in range(current_canvas.inspector_content_layout.count() - 1, -1, -1):
            item = current_canvas.inspector_content_layout.itemAt(i)
            if item and item.spacerItem():
                current_canvas.inspector_content_layout.takeAt(i)
        
        # Add new content
        title = QLabel(f"{self.t('main_GUI.inspector.title')} - {block.block_type.replace('_', ' ')}")
        title.setStyleSheet("font-weight: bold; font-size: 16px; padding: 5px;")
        current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), title)
        
        self.position_label = QLabel(f"{self.t('main_GUI.inspector.position')}: ({int(block.x())}, {int(block.y())})")
        current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.position_label)
        
        size_label = QLabel(f"{self.t('main_GUI.inspector.size')}: ({int(block.boundingRect().width())} x {int(block.boundingRect().height())})")
        current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), size_label)
        
        self.add_inputs(block, canvas=current_canvas)
        current_canvas.inspector_content_layout.addStretch()

    def update_pos(self, block):
        """Update position labels in inspector"""
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        if self.position_label:
            position_label = self.position_label
        else:
            position_label = None
        
        if position_label:
            position_label.setText(f"{self.t('main_GUI.inspector.position')}: ({int(block.x())}, {int(block.y())})")

    def add_inputs(self, block, dev_id=None, var_id=None, canvas=None):
        """Add input fields for block properties"""
        current_canvas = self.current_canvas if canvas is None else canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            block_data = Utils.main_canvas['blocks'].get(block.block_id)
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    block_data = Utils.functions[f_id]['blocks'].get(block.block_id)
                    break
        
        #print(f"Adding inputs for block data: {block_data}")
        if block_data['type'] in ('Start', 'End'):
            return
        
        if block_data['type'] == 'Timer':
            # Timer block inputs
            label = QLabel(f"{self.t('main_GUI.inspector.interval_ms')}:")
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), label)
            
            interval_input = QLineEdit()
            regex = QRegularExpression(r"^\d*$")
            validator = QRegularExpressionValidator(regex, self)
            interval_input.setValidator(validator)
            interval_input.setText(block_data.get('sleep_time', '1000'))
            interval_input.setPlaceholderText(self.t("main_GUI.inspector.interval_ms_placeholder"))
            interval_input.textChanged.connect(lambda text, bd=block_data: self.Block_sleep_interval_changed(text, bd))
            
            current_canvas.inspector_content_layout.insertWidget(
                current_canvas.inspector_content_layout.count(), 
                interval_input
            )
        #Loops and If blocks inputs
        if block_data['type'] in ('While', 'For Loop'):
            name_label = QLabel(f"{self.t('main_GUI.inspector.value_1_name')}:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            
            name_1_input = SearchableLineEdit()
            name_1_input.setText(block_data.get('value_1_name', ''))
            name_1_input.setPlaceholderText(self.t("main_GUI.inspector.value_1_name_placeholder"))
            name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, name_1_input, canvas=current_canvas)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_1_input)
            
            type_label = QLabel(f"{self.t('main_GUI.inspector.operator')}:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), type_label)
            
            type_input = QComboBox()
            type_input.addItems(["==", "!=", "<", ">", "<=", ">="])
            type_input.setCurrentText(block_data.get('operator', '=='))
            type_input.currentTextChanged.connect(lambda text, bd=block_data: self.Block_operator_changed(text, bd))
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), type_input)
            
            value_label = QLabel(f"{self.t('main_GUI.inspector.value_2_name')}:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), value_label)
            
            self.name_2_input = SearchableLineEdit()
            self.name_2_input.setText(block_data.get('value_2_name', ''))
            self.name_2_input.setPlaceholderText(self.t("main_GUI.inspector.value_2_name_placeholder"))
            self.name_2_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_2_name_changed(text, bd))
            
            self.insert_items(block, self.name_2_input, canvas=current_canvas)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_2_input)
        if block_data['type'] == 'If':
            for i in range(1, block_data.get('conditions', 1) + 1):
                print(f"Adding condition {i} for If block")
                cond_widget = QWidget()
                cond_layout = QHBoxLayout(cond_widget)
                cond_layout.setContentsMargins(0, 0, 0, 0)

                value_1_label = QLabel(f"{self.t('main_GUI.inspector.value_1_name')}:")
                cond_layout.addWidget(value_1_label)
                value_1_input = SearchableLineEdit()
                value_1_input.setText(block_data.get('first_vars', {}).get(f'value_{i}_1_name', ''))
                value_1_input.setPlaceholderText(self.t("main_GUI.inspector.value_1_name_placeholder"))
                value_1_input.textChanged.connect(lambda text, bd=block_data, idx=i: self.Block_value_1_name_changed(text, bd, idx))
                self.insert_items(block, value_1_input, canvas=current_canvas)
                cond_layout.addWidget(value_1_input)

                operator_label = QLabel(f"{self.t('main_GUI.inspector.operator')}:")
                cond_layout.addWidget(operator_label)
                operator_input = QComboBox()
                operator_input.addItems(["==", "!=", "<", ">", "<=", ">="])
                operator_input.setCurrentText(block_data.get('operators', {}).get(f'operator_{i}', '=='))
                operator_input.currentTextChanged.connect(lambda text, bd=block_data, idx=i: self.Block_operator_changed(text, bd, idx))
                cond_layout.addWidget(operator_input)

                value_2_label = QLabel(f"{self.t('main_GUI.inspector.value_2_name')}:")
                cond_layout.addWidget(value_2_label)
                value_2_input = SearchableLineEdit()
                value_2_input.setText(block_data.get('second_vars', {}).get(f'value_{i}_2_name', ''))
                value_2_input.setPlaceholderText(self.t("main_GUI.inspector.value_2_name_placeholder"))
                value_2_input.textChanged.connect(lambda text, bd=block_data, idx=i: self.Block_value_2_name_changed(text, bd, idx))
                self.insert_items(block, value_2_input, canvas=current_canvas)
                cond_layout.addWidget(value_2_input)
                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), cond_widget)

        if block_data['type'] == 'Switch':
            name_label = QLabel(f"{self.t('main_GUI.inspector.device/variable_name')}:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            
            name_1_input = SearchableLineEdit()
            name_1_input.setText(block_data.get('value_1_name', ''))
            name_1_input.setPlaceholderText(self.t("main_GUI.inspector.device/variable_name_placeholder"))
            name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, name_1_input, canvas=current_canvas)
            
            Label_ON = QLabel("On")
            Label_OFF = QLabel("Off")
            
            switch = CustomSwitch()
            switch.set_checked(block_data.get('switch_state', False))
            switch.toggled.connect(lambda state, bd=block_data: self.Block_switch_changed(state, bd))
            
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 5, 5, 5)
            
            row_layout.addWidget(Label_OFF)
            row_layout.addWidget(switch)
            row_layout.addWidget(Label_ON)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_1_input)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), row_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        if block_data['type'] == 'Button':
            name_label = QLabel(self.t("main_GUI.inspector.device_name"))
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            
            name_1_input = SearchableLineEdit()
            name_1_input.setText(block_data.get('value_1_name', ''))
            name_1_input.setPlaceholderText(self.t("main_GUI.inspector.device_name_placeholder"))
            name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, name_1_input, canvas=current_canvas)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_1_input)
       
        #LEDS

        if block_data['type'] == 'Blink_LED':
            name_label = QLabel(self.t("main_GUI.inspector.led_device_name"))
            
            name_1_input = SearchableLineEdit()
            name_1_input.setText(block_data.get('value_1_name', ''))
            name_1_input.setPlaceholderText(self.t("main_GUI.inspector.led_device_name_placeholder"))
            name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, name_1_input, canvas=current_canvas)
            
            time_label = QLabel(self.t("main_GUI.inspector.blink_interval_ms"))

            blink_time_input = QLineEdit()
            regex = QRegularExpression(r"^\d*$")
            validator = QRegularExpressionValidator(regex, self)
            blink_time_input.setValidator(validator)
            blink_time_input.setText(block_data.get('sleep_time', '1000'))
            blink_time_input.setPlaceholderText(self.t("main_GUI.inspector.blink_interval_ms_placeholder"))
            blink_time_input.textChanged.connect(lambda text, bd=block_data: self.Block_sleep_interval_changed(text, bd))

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_1_input)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), time_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), blink_time_input)
        if block_data['type'] in ["Toggle_LED", "LED_ON", "LED_OFF"]:
            name_label = QLabel(self.t("main_GUI.inspector.led_device_name"))
            
            name_1_input = SearchableLineEdit()
            name_1_input.setText(block_data.get('value_1_name', ''))
            name_1_input.setPlaceholderText(self.t("main_GUI.inspector.led_device_name_placeholder"))
            name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, name_1_input, canvas=current_canvas)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_1_input)
        if block_data['type'] == 'PWM_LED':
            name_label = QLabel(self.t("main_GUI.inspector.led_device_name"))
            
            name_1_input = SearchableLineEdit()
            name_1_input.setText(block_data.get('value_1_name', ''))
            name_1_input.setPlaceholderText(self.t("main_GUI.inspector.led_device_name_placeholder"))
            name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, name_1_input, canvas=current_canvas)

            PWM_label = QLabel(self.t("main_GUI.inspector.pwm_value"))

            PWM_value_input = SearchableLineEdit()
            PWM_value_input.setText(block_data.get('PWM_value', ''))
            PWM_value_input.setPlaceholderText(self.t("main_GUI.inspector.pwm_value_placeholder"))
            PWM_value_input.textChanged.connect(lambda text, bd=block_data, w=PWM_value_input: self.Block_PWM_value_changed(text, bd, w=w))

            self.insert_items(block, PWM_value_input, canvas=current_canvas)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_1_input)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), PWM_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), PWM_value_input)
        if block_data['type'] == 'RGB_LED':
            for i in range(1, 4):
                line_widget = QWidget()
                line_layout = QHBoxLayout(line_widget)
                line_layout.setContentsMargins(0, 0, 0, 0)

                name_label = QLabel(self.t("main_GUI.inspector.led_device_name"))
                
                name_1_input = SearchableLineEdit()
                name_1_input.setText(block_data['first_vars'].get(f'value_{i}_1_name', ''))
                name_1_input.setPlaceholderText(self.t("main_GUI.inspector.led_device_name_placeholder"))
                name_1_input.textChanged.connect(lambda text, bd=block_data, inx=i: self.Block_value_1_name_changed(text, bd, inx))
                
                self.insert_items(block, name_1_input, canvas=current_canvas)

                PWM_label = QLabel(self.t("main_GUI.inspector.pwm_value"))

                PWM_value_input = SearchableLineEdit()
                PWM_value_input.setText(block_data['second_vars'].get(f'value_{i}_2_PWM', ''))
                PWM_value_input.setPlaceholderText(self.t("main_GUI.inspector.pwm_value_placeholder"))
                PWM_value_input.textChanged.connect(lambda text, bd=block_data, inx=i, w=PWM_value_input: self.Block_PWM_value_changed(text, bd, inx, w))

                line_layout.addWidget(name_label)
                line_layout.addWidget(name_1_input)
                line_layout.addWidget(PWM_label)
                line_layout.addWidget(PWM_value_input)

                current_canvas.inspector_content_layout.addWidget(line_widget)

        #Math blocks

        if block_data['type'] in ("Basic_operations", "Exponential_operations", "Random_number"):
            name_label = QLabel(self.t("main_GUI.inspector.first_variable"))
            
            value_1_name_input = SearchableLineEdit()
            value_1_name_input.setText(block_data.get('value_1_name', ''))
            value_1_name_input.setPlaceholderText(self.t("main_GUI.inspector.first_variable_placeholder"))
            value_1_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))

            if block_data['type'] == "Basic_operations":
                box_label = QLabel(self.t("main_GUI.inspector.operator"))

                operator_box = QComboBox()
                operator_box.addItems(["+", "-", "*", "/", "%"])
                operator_box.setCurrentText(block_data.get('operator', '+'))
                operator_box.currentTextChanged.connect(lambda text, bd=block_data: self.Block_operator_changed(text, bd))
            elif block_data['type'] == "Exponential_operations":
                box_label = QLabel(self.t("main_GUI.inspector.operator"))

                operator_box = QComboBox()
                operator_box.addItems(["^", "√"])
                operator_box.setCurrentText(block_data.get('operator', '^'))
                operator_box.currentTextChanged.connect(lambda text, bd=block_data: self.Block_operator_changed(text, bd))
            else:
                operator_box = None

            name_label_2 = QLabel(self.t("main_GUI.inspector.second_variable"))
            value_2_name_input = SearchableLineEdit()
            value_2_name_input.setText(block_data.get('value_2_name', ''))
            value_2_name_input.setPlaceholderText(self.t("main_GUI.inspector.second_variable_placeholder"))
            value_2_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_2_name_changed(text, bd))

            name_label_3 = QLabel(self.t("main_GUI.inspector.result_variable"))
            result_var_name_input = SearchableLineEdit()
            result_var_name_input.setText(block_data.get('result_var_name', ''))
            result_var_name_input.setPlaceholderText(self.t("main_GUI.inspector.result_variable_placeholder"))
            result_var_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_result_var_name_changed(text, bd))

            self.insert_items(block, value_1_name_input, canvas=current_canvas)
            self.insert_items(block, value_2_name_input, canvas=current_canvas)
            self.insert_items(block, result_var_name_input, canvas=current_canvas)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label_3)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), result_var_name_input)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), value_1_name_input) 
            if operator_box:
                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), box_label)
                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), operator_box) 
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label_2)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), value_2_name_input)

        if block_data['type'] in ("Plus_one", "Minus_one"):

            line_widget = QWidget()
            line_layout = QHBoxLayout(line_widget)
            line_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(self.t("main_GUI.inspector.variable"))
            
            value_1_name_input = SearchableLineEdit()
            value_1_name_input.setText(block_data.get('value_1_name', ''))
            value_1_name_input.setPlaceholderText(self.t("main_GUI.inspector.variable_placeholder"))
            value_1_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))

            if block_data['type'] == "Plus_one":
                operator_label = QLabel("+ 1")
            else:
                operator_label = QLabel("- 1")

            self.insert_items(block, value_1_name_input, canvas=current_canvas)
            line_layout.addWidget(name_label)
            line_layout.addWidget(value_1_name_input)
            line_layout.addWidget(operator_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), line_widget)

        #Function block inputs
        
        if block_data['type'] == 'Function':
            
            var_label = QLabel(self.t("main_GUI.inspector.input_variables"))
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), var_label)

            for canv, canv_info in Utils.canvas_instances.items():
                if canv_info.get('ref') == 'function' and canv_info.get('name') == block_data.get('name'):
                    break
            #print(f"Function canvas info: {canv_info}")
            
            for var_id, var_info in Utils.variables['function_canvases'][canv_info['id']].items():
                line_widget = QWidget()
                line_layout = QHBoxLayout(line_widget)
                line_layout.setContentsMargins(0, 0, 0, 0)
                
                ref_var_label = QLabel(self.t("main_GUI.inspector.ref_variable"))

                ref_var_name = QLabel(var_info['name'])

                main_var_label = QLabel(self.t("main_GUI.inspector.main_variable"))
                main_var_combo = SearchableLineEdit()
                main_var_combo.setPlaceholderText(self.t("main_GUI.inspector.main_variables_placeholder"))

                self.insert_items(block, main_var_combo, type='variable_m', canvas=current_canvas)
                line_layout.addWidget(ref_var_label)
                line_layout.addWidget(ref_var_name)
                line_layout.addWidget(main_var_label)
                line_layout.addWidget(main_var_combo) 

                if var_id is None:
                    id_var_generated = False
                    while not id_var_generated:
                        var_id = 'var_'+str(int(random()*100000))
                        if var_id not in block_data['internal_vars']['ref_vars'].keys():
                            id_var_generated = True
                            break
                        else:
                            id_var_generated = False
                if var_id not in block_data['internal_vars'].get('ref_vars', {}):
                    block_data['internal_vars']['ref_vars'][var_id] = {
                        'name': '',
                        'type': '',
                    }
                block_data['internal_vars']['ref_vars'][var_id]['name'] = var_info['name']
                block_data['internal_vars']['ref_vars'][var_id]['type'] = 'Variable'

                main_var_combo.textChanged.connect(lambda text, bd=block_data, v=var_id: self.function_variable_changed(text, bd, v))

                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), line_widget)
            
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Plain)
            separator.setLineWidth(1)
            separator.setStyleSheet("background-color: #555555;")
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), separator)

            dev_label = QLabel(self.t("main_GUI.inspector.input_devices"))

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), dev_label)

            for dev_id, dev_info in Utils.devices['function_canvases'][canv_info['id']].items():
                line_widget = QWidget()
                line_layout = QHBoxLayout(line_widget)
                line_layout.setContentsMargins(0, 0, 0, 0)
                
                ref_dev_label = QLabel(self.t("main_GUI.inspector.ref_device"))
                ref_dev_name = QLabel(dev_info['name'])

                main_dev_label = QLabel(self.t("main_GUI.inspector.main_device"))

                main_dev_combo = SearchableLineEdit()
                main_dev_combo.setPlaceholderText(self.t("main_GUI.inspector.main_devices_placeholder"))

                self.insert_items(block, main_dev_combo, type='device_m', canvas=current_canvas)
                line_layout.addWidget(ref_dev_label)
                line_layout.addWidget(ref_dev_name)
                line_layout.addWidget(main_dev_label)
                line_layout.addWidget(main_dev_combo)
                
                if dev_id is None:
                    id_dev_generated = False
                    while not id_dev_generated:
                        dev_id = 'dev_'+str(int(random()*100000))
                        if dev_id not in block_data['internal_devs']['ref_devs'].keys():
                            id_dev_generated = True
                            break
                        else:
                            id_dev_generated = False

                if dev_id not in block_data['internal_devs'].get('ref_devs', {}):
                    block_data['internal_devs']['ref_devs'][dev_id] = {
                        'name': '',
                        'type': '',
                    }
                block_data['internal_devs']['ref_devs'][dev_id]['name'] = dev_info['name']
                block_data['internal_devs']['ref_devs'][dev_id]['type'] = 'Device'

                main_dev_combo.textChanged.connect(lambda text, bd=block_data, d=dev_id: self.function_device_changed(text, bd, d))


                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), line_widget)
#MARK: - Block Property Change Handlers
    def function_variable_changed(self, text, block_data, var_id=None):
        #print(f"Function variable changed to: {text}, type: {type}")
        # Implement the logic to update function variable mapping in block_data
        # This is a placeholder implementation
        if var_id in block_data['internal_vars'].get('main_vars', {}):
            old_name = block_data['internal_vars']['main_vars'][var_id]['name']
            del block_data['internal_vars']['main_vars'][var_id]
        if var_id not in block_data['internal_vars'].get('main_vars', {}):
            block_data['internal_vars']['main_vars'][var_id] = {
                'name': '',
                'type': '',
            }
        block_data['internal_vars']['main_vars'][var_id]['name'] = text
        block_data['internal_vars']['main_vars'][var_id]['type'] = 'Variable'
        print(f"Updated block_data: {block_data}")

    def function_device_changed(self, text, block_data, dev_id=None):
        #print(f"Function device changed to: {text}, type: {type}")
        # Implement the logic to update function device mapping in block_data
        # This is a placeholder implementation
        if dev_id in block_data['internal_devs'].get('main_devs', {}):
            old_name = block_data['internal_devs']['main_devs'][dev_id]['name']
            del block_data['internal_devs']['main_devs'][dev_id]
        if dev_id not in block_data['internal_devs'].get('main_devs', {}):
            block_data['internal_devs']['main_devs'][dev_id] = {
                'name': '',
                'type': '',
            }
        block_data['internal_devs']['main_devs'][dev_id]['name'] = text
        block_data['internal_devs']['main_devs'][dev_id]['type'] = 'Device'
        print(f"Updated block_data: {block_data}")

    def Block_value_1_name_changed(self, text, block_data, idx=None):
        current_canvas = self.current_canvas
        #print("Updating vlaue 1 name")
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            variables = Utils.variables['main_canvas']
            devices = Utils.devices['main_canvas']
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    variables = Utils.variables['function_canvases'][f_id]
                    devices = Utils.devices['function_canvases'][f_id]
                    break
        for var_id, var_info in variables.items():
            #print(f"Checking variable: {var_info}")
            if var_info['name'] == text:
                if block_data['type'] in ('If', 'RGB_LED'):
                    block_data['first_vars'][f'value_{idx if idx is not None else 1}_1_type'] = 'Variable'
                else:
                    block_data['value_1_type'] = 'Variable'
                break
        for dev_id, dev_info in devices.items():
            if dev_info['name'] == text:
                if block_data['type'] in ('If', 'RGB_LED'):
                    block_data['first_vars'][f'value_{idx if idx is not None else 1}_1_type'] = 'Device'
                else:
                    block_data['value_1_type'] = 'Device'
                break
        if len(text) > 20:
            text = text[:20]
        if block_data['type'] in ('If', 'RGB_LED'):
            block_data['first_vars'][f'value_{idx if idx is not None else 1}_1_name'] = text
            setattr(block_data['widget'], f'value_{idx if idx is not None else 1}_1_name', text)
        else: 
            block_data['value_1_name'] = text
            block_data['widget'].value_1_name = text

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])
        
        block_data['widget'].update()
    
    def Block_operator_changed(self, text, block_data, idx=None):
        #print("Updating operator")
        if block_data['type'] == 'If':
            block_data['operators'][f"operator_{idx if idx is not None else 1}"] = text
            print(f"Updated block_data operators: {block_data['operators']}")
            setattr(block_data['widget'], f'operator_{idx if idx is not None else 1}', text)
            print(f"Updated widget operator_{idx if idx is not None else 1}: {getattr(block_data['widget'], f'operator_{idx if idx is not None else 1}')}")
        else:
            block_data['operator'] = text
            block_data['widget'].operator = text   

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])

        block_data['widget'].update()
    
    def Block_value_2_name_changed(self, text, block_data, idx=None):
        #print("Updating vlaue 2 name") 
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return

        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            variables = Utils.variables['main_canvas']
            devices = Utils.devices['main_canvas']
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    variables = Utils.variables['function_canvases'][f_id]
                    devices = Utils.devices['function_canvases'][f_id]
                    break

        for var_id, var_info in variables.items():
            if var_info['name'] == text:
                if block_data['type'] in ('If', 'RGB_LED'):
                    block_data['second_vars'][f'value_{idx if idx is not None else 2}_2_type'] = 'Variable'
                else:
                    block_data['value_2_type'] = 'Variable'
                break
        for dev_id, dev_info in devices.items():
            if dev_info['name'] == text:
                if block_data['type'] in ('If', 'RGB_LED'):
                    block_data['second_vars'][f'value_{idx if idx is not None else 2}_2_type'] = 'Device'
                else:
                    block_data['value_2_type'] = 'Device'
                break
        if len(text) > 20:
            text = text[:20]
        if block_data['type'] in ('If', 'RGB_LED'):
            block_data['second_vars'][f'value_{idx if idx is not None else 2}_2_name'] = text
            setattr(block_data['widget'], f'value_{idx if idx is not None else 2}_2_name', text)
        else:
            block_data['value_2_name'] = text
            block_data['widget'].value_2_name = text

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])

        block_data['widget'].update()
    
    def Block_result_var_name_changed(self, text, block_data):
        #print("Updating result variable name") 
        block_data['result_var_name'] = text
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return

        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            variables = Utils.variables['main_canvas']
            devices = Utils.devices['main_canvas']
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    variables = Utils.variables['function_canvases'][f_id]
                    devices = Utils.devices['function_canvases'][f_id]
                    break

        for var_id, var_info in variables.items():
            if var_info['name'] == text:
                block_data['result_var_type'] = 'Variable'
                break
        for dev_id, dev_info in devices.items():
            if dev_info['name'] == text:
                block_data['result_var_type'] = 'Device'
                break
        if len(text) > 20:
            text = text[:20]
        block_data['result_var_name'] = text
        block_data['widget'].result_var_name = text

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])

        block_data['widget'].update()
    
    def Block_switch_changed(self, state, block_data):
        block_data['switch_state'] = state
        block_data['widget'].switch_state = state

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])

        block_data['widget'].update()
    
    def Block_sleep_interval_changed(self, text, block_data):
        #print("Updating sleep interval")
        block_data['sleep_time'] = text
        block_data['widget'].sleep_time = text

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])

        block_data['widget'].update()

    def Block_PWM_value_changed(self, text, block_data, inx=None, w=None):
        #print("Updating PWM value")
        if text != '' and text.isdigit():
            pwm_val = int(text)
            if pwm_val < 0:
                pwm_val = 0
            elif pwm_val > 100:
                pwm_val = 100
            text = str(pwm_val)
            if w is not None:
                w.blockSignals(True)
                w.setText(text)
                w.blockSignals(False)
        if len(text) > 20:
                text = text[:20]
        if block_data['type'] == 'RGB_LED':
            print(f"Updating RGB LED PWM value for index {inx}: {text}")
            block_data['second_vars'][f'value_{inx if inx is not None else 2}_2_PWM'] = text
            setattr(block_data['widget'], f'value_{inx if inx is not None else 2}_2_PWM', text)
        else:
            block_data['PWM_value'] = text
            block_data['widget'].PWM_value = text

        block_data['widget'].recalculate_size()

        if hasattr(self.current_canvas, 'path_manager'):
            self.current_canvas.path_manager.update_paths_for_widget(block_data['widget'])

        block_data['widget'].update()

    def insert_items(self, block, line_edit, type=None, canvas=None):
        #print("Inserting items into line edit")
        current_canvas = self.current_canvas if canvas is None else canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            if not block.block_id in Utils.main_canvas['blocks']:
                return
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    if not block.block_id in Utils.functions[f_id]['blocks']:
                        return
                    break
        #print("Inserting items into combo box")
        if hasattr(line_edit, 'addItems'):
            #print("Line edit supports addItems")
            # Collect all items
            all_items = []
            #print(f"All items before insertion: {all_items}")
            if block.block_type in ('Switch', 'Button'):
                if current_canvas.reference == 'canvas':
                    for id, text in Utils.devices['main_canvas'].items():
                        #print(f"Added device item into Switch/Button: {text}")
                        all_items.append(text['name'])
                elif current_canvas.reference == 'function':
                    for f_id, f_info in Utils.functions.items():
                        if current_canvas == f_info.get('canvas'):
                            for id, text in Utils.devices['function_canvases'][f_id].items():
                                #print(f"Added function device item into Switch/Button: {text}")
                                all_items.append(text['name'])
                            break
            elif block.block_type.startswith('Function_'):
                for canvas, info in Utils.canvas_instances.items():
                    if info['ref'] == 'function' and info['name'] == block.block_type.split('_')[1]:
                        function_id = info['id']
                        break
                if type == 'variable_f':
                    for v_id, v_info in Utils.variables['function_canvases'][function_id].items():
                        all_items.append(v_info['name'])
                        #print(f"Added function variable item: {v_info['name']}")
                elif type == 'variable_m':
                    for v_id, v_info in Utils.variables['main_canvas'].items():
                        all_items.append(v_info['name'])
                        #print(f"Added main variable item: {v_info['name']}")
                elif type == 'device_f':
                    for d_id, d_info in Utils.devices['function_canvases'][function_id].items():
                        all_items.append(d_info['name'])
                        #print(f"Added function device item: {d_info['name']}")
                elif type == 'device_m':
                    for d_id, d_info in Utils.devices['main_canvas'].items():
                        all_items.append(d_info['name'])
                        #print(f"Added main device item: {d_info['name']}")
            else:
                if current_canvas.reference == 'canvas':
                    for id, text in Utils.variables['main_canvas'].items():
                        all_items.append(text['name'])
                        #print(f"Added variable item: {text['name']}")
                    for id, text in Utils.devices['main_canvas'].items():
                        #print(f"Added device item: {text['name']}")
                        all_items.append(text['name'])
                elif current_canvas.reference == 'function':
                    for f_id, f_info in Utils.functions.items():
                        if current_canvas == f_info.get('canvas'):
                            for id, text in Utils.variables['function_canvases'][f_id].items():
                                all_items.append(text['name'])
                                #print(f"Added function variable item: {text['name']}")
                            for id, text in Utils.devices['function_canvases'][f_id].items():
                                all_items.append(text['name'])
                                #print(f"Added function device item: {text['name']}")
                            break

            # Add all items at once
            #print(f"Inserting items into combo box: {all_items}")
            line_edit.addItems(all_items)
            #print(f"Added {len(all_items)} items to combo box")

    #MARK: - Internal Variable Panel Methods
    def add_internal_variable_row(self, var_id=None, var_data=None, canvas_reference=None):
        """Add a new internal variable row"""
        #print(f"Adding variable row to canvas_reference: {canvas_reference}")
        id_var_generated = False
        if var_id is None:
            while not id_var_generated:
                var_id = f"variable_{str(int(random()*100000))}"
                #print(f"Generated variable_id attempt: {var_id}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas_reference == canvas and info['ref'] == 'canvas':
                        #print(f"Checking main_canvas for var_id: {var_id}")
                        pass
                    elif canvas_reference == canvas and info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                if var_id not in Utils.variables['function_canvases'][function_id].keys():
                                    Utils.variables['function_canvases'][function_id][var_id] = {
                                        'name': '',
                                        'type': 'Int',
                                        'widget': None,
                                        'name_input': None,
                                        'type_input': None,
                                    }
                                    id_var_generated = True
                                    break
                                else:
                                    var_id = None
                    else:
                        print("Error: Canvas reference not found in Utils.canvas_instances")
        else:
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas and info['ref'] == 'canvas':
                    #print(f"Adding predefined var_id to main_canvas: {var_id}")
                    pass
                elif canvas_reference == canvas and info['ref'] == 'function':
                    for function_id, function_info in Utils.functions.items():
                        if function_info['canvas'] == canvas_reference:
                            Utils.variables['function_canvases'][function_id][var_id] = {
                                'name': '',
                                'type': 'Int',
                                'widget': None,
                                'name_input': None,
                                'type_input': None,
                            }
                else:
                    print("Error: Canvas reference not found in Utils.canvas_instances")
        #print(f"Utils.variables after adding new variable: {Utils.variables}")
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)

        name_input = QLineEdit()
        name_input.setPlaceholderText(self.t("main_GUI.internal_tab.variable_name_placeholder"))
        if var_data and 'name' in var_data:
            name_input.setText(var_data['name'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.variables['function_canvases'][function_id][var_id]['name'] = var_data['name']
        
        name_input.textChanged.connect(lambda text, v_id=var_id, t="Variable", r=canvas_reference: self.name_changed(text, v_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Bool"])
        if var_data and 'type' in var_data:
            type_input.setCurrentText(var_data['type'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.variables['function_canvases'][function_id][var_id]['type'] = var_data['type']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=var_id, t="Variable", r=canvas_reference, w=type_input: self.type_changed(text, v_id , t, r, w))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_input)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=canvas_reference.row_widget, t="Variable", r=canvas_reference: self.remove_internal_row(rw, v_id, t, r))

        for function_id, function_info in Utils.functions.items():
            if function_info['canvas'] == canvas_reference:
                Utils.variables['function_canvases'][function_id][var_id]['widget'] = canvas_reference.row_widget
                Utils.variables['function_canvases'][function_id][var_id]['name_input'] = name_input
                Utils.variables['function_canvases'][function_id][var_id]['type_input'] = type_input
        panel_layout = canvas_reference.internal_layout
        panel_layout.insertWidget(panel_layout.count() - 2 - canvas_reference.internal_devs_rows_count, canvas_reference.row_widget)

        #print(f"Added variable: {self.var_id}")
    def add_internal_device_row(self, dev_id=None, dev_data=None, canvas_reference=None):
        #print(f"Adding variable row to canvas_reference: {canvas_reference}")
        id_dev_generated = False
        if dev_id is None:
            while not id_dev_generated:
                dev_id = f"device_{str(int(random()*100000))}"
                #print(f"Generated device_id attempt: {dev_id}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas_reference == canvas and info['ref'] == 'canvas':
                        #print(f"Checking main_canvas for dev_id: {dev_id}")
                        pass
                    elif canvas_reference == canvas and info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                if dev_id not in Utils.devices['function_canvases'][function_id].keys():
                                    Utils.devices['function_canvases'][function_id][dev_id] = {
                                        'name': '',
                                        'type': self.t("main_GUI.internal_tab.output"),
                                        'type_index': 0,
                                        'widget': None,
                                        'name_input': None,
                                        'type_input': None,
                                    }
                                    id_dev_generated = True
                                    break
                                else:
                                    dev_id = None
                    else:
                        print("Error: Canvas reference not found in Utils.canvas_instances")
        else:
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas and info['ref'] == 'canvas':
                    #print(f"Adding predefined dev_id to main_canvas: {dev_id}")
                    pass
                elif canvas_reference == canvas and info['ref'] == 'function':
                    for function_id, function_info in Utils.functions.items():
                        if function_info['canvas'] == canvas_reference:
                            Utils.devices['function_canvases'][function_id][dev_id] = {
                                'name': '',
                                'type': self.t("main_GUI.internal_tab.output"),
                                'type_index': 0,
                                'widget': None,
                                'name_input': None,
                                'type_input': None,
                            }
                else:
                    print("Error: Canvas reference not found in Utils.canvas_instances")
        #print(f"Utils.devices after adding new device: {Utils.devices}")
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)

        name_input = QLineEdit()
        name_input.setPlaceholderText(self.t("main_GUI.internal_tab.device_name_placeholder"))
        if dev_data and 'name' in dev_data:
            name_input.setText(dev_data['name'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.devices['function_canvases'][function_id][dev_id]['name'] = dev_data['name']
        
        name_input.textChanged.connect(lambda text, v_id=dev_id, t="Device", r=canvas_reference: self.name_changed(text, v_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems([self.t("main_GUI.internal_tab.output"), self.t("main_GUI.internal_tab.input"), self.t("main_GUI.internal_tab.button"), "PWM"])
        if dev_data and 'type' in dev_data:
            type_input.setCurrentIndex(dev_data['type_index'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.devices['function_canvases'][function_id][dev_id]['type'] = dev_data['type']
                    Utils.devices['function_canvases'][function_id][dev_id]['type_index'] = dev_data['type_index']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=dev_id, t="Device", r=canvas_reference, w=type_input: self.type_changed(text, v_id , t, r, w))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_input)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=dev_id, rw=canvas_reference.row_widget, t="Device", r=canvas_reference: self.remove_internal_row(rw, v_id, t, r))

        for function_id, function_info in Utils.functions.items():
            if function_info['canvas'] == canvas_reference:
                Utils.devices['function_canvases'][function_id][dev_id]['widget'] = canvas_reference.row_widget
                Utils.devices['function_canvases'][function_id][dev_id]['name_input'] = name_input
                Utils.devices['function_canvases'][function_id][dev_id]['type_input'] = type_input
        panel_layout = canvas_reference.internal_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        canvas_reference.internal_devs_rows_count += 1
    #MARK: - Variable Panel Methods
    def add_variable_row(self, var_id=None, var_data=None, canvas_reference=None):
        """Add a new variable row"""
        #print(f"Adding variable row to canvas_reference: {canvas_reference}")
        id_var_generated = False
        if var_id is None:
            while not id_var_generated:
                var_id = f"variable_{str(int(random()*100000))}"
                #print(f"Generated variable_id attempt: {var_id}"
                if var_id not in Utils.variables['main_canvas'].keys():
                    Utils.variables['main_canvas'][var_id] = {
                        'name': '',
                        'type': 'Int',
                        'value': '',
                        'widget': None,
                        'name_input': None,
                        'type_input': None,
                        'value_input': None,
                        'current_value_display': None
                    }
                    id_var_generated = True
                    break
                else:
                    var_id = None
        else:
            Utils.variables['main_canvas'][var_id] = {
                'name': '',
                'type': 'Int',
                'value': '',
                'widget': None,
                'name_input': None,
                'type_input': None,
                'value_input': None,
                'current_value_display': None
            }
        #print(f"Utils.variables after adding new variable: {Utils.variables}")
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)

        name_input = QLineEdit()
        name_input.setPlaceholderText(self.t("main_GUI.variables_tab.name_placeholder"))
        if var_data and 'name' in var_data:
            name_input.setText(var_data['name'])
            Utils.variables['main_canvas'][var_id]['name'] = var_data['name']
        
        name_input.textChanged.connect(lambda text, v_id=var_id, t="Variable", r=canvas_reference: self.name_changed(text, v_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Bool"])
        if var_data and 'type' in var_data:
            type_input.setCurrentText(var_data['type'])
            Utils.variables['main_canvas'][var_id]['type'] = var_data['type']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=var_id, t="Variable", r=canvas_reference, w=type_input: self.type_changed(text, v_id , t, r, w))
        
        value_var_input = QLineEdit()
        if var_data and 'type' in var_data:
            if var_data['type'] == 'Int':
                value_var_input.setValidator(QIntValidator(-1073741824, 1073741823))
            elif var_data['type'] == 'Float':
                regex = QRegularExpression(r"^-?[0-9]*\.?[0-9]*$")
                value_var_input.setValidator(QRegularExpressionValidator(regex, self))
                value_var_input.setMaxLength(14) # Hard caps total characters
            elif var_data['type'] == 'Bool':
                regex = QRegularExpression(r"^[01]$")
                value_var_input.setValidator(QRegularExpressionValidator(regex, self))
                value_var_input.setMaxLength(1)
            elif var_data['type'] == 'String':
                value_var_input.setValidator(None)
        else:
            value_var_input.setValidator(QIntValidator(-1073741824, 1073741823))
        value_var_input.setPlaceholderText(self.t("main_GUI.variables_tab.initial_value_placeholder"))
        if var_data and 'value' in var_data:
            print(f"Setting initial value for variable {var_id}: {var_data['value']}")
            value_var_input.setText(var_data['value'])
            Utils.variables['main_canvas'][var_id]['value'] = var_data['value']
        value_var_input.textChanged.connect(lambda text, v_id=var_id, t="Variable", r=canvas_reference, w=value_var_input: self.value_changed(text, v_id, t, r, w))
        
        current_value = QLineEdit()
        current_value.setReadOnly(True)
        current_value.setPlaceholderText(self.t("main_GUI.variables_tab.current_value_placeholder"))

        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_input)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(value_var_input)
        canvas_reference.row_layout.addWidget(current_value)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=canvas_reference.row_widget, t="Variable", r=canvas_reference: self.remove_row(rw, v_id, t, r))

        Utils.variables['main_canvas'][var_id]['widget'] = canvas_reference.row_widget
        Utils.variables['main_canvas'][var_id]['name_input'] = name_input
        Utils.variables['main_canvas'][var_id]['type_input'] = type_input
        Utils.variables['main_canvas'][var_id]['value_input'] = value_var_input
        Utils.variables['main_canvas'][var_id]['current_value_display'] = current_value
        panel_layout = canvas_reference.var_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        
        #print(f"Added variable: {self.var_id}")
    
    def Clear_All_Variables(self):
        #print("Clearing all variables")
        var_ids_to_remove = []
        # Get a SNAPSHOT of variable IDs BEFORE modifying anything
        for canvas, info in Utils.canvas_instances.items():
            if canvas == info['canvas']:
                var_ids_to_remove += list(Utils.variables['main_canvas'].keys())
            elif canvas == info['function']:
                for function_id, function_info in Utils.functions.items():
                    var_ids_to_remove += list(Utils.variables['function_canvases'][function_id].keys())
        #print(f"Current Utils.variables before clearing: {Utils.variables}")
        #print(f"Variable IDs to remove: {var_ids_to_remove}")
        
        # Now remove them
        try:
            for varid in var_ids_to_remove:
                #print(f"Removing varid: {varid}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas == info['canvas']:
                        canvas_reference = info['canvas']
                        rowwidget = Utils.variables['main_canvas'][varid]['widget']
                        self.remove_row(rowwidget, varid, 'Variable', canvas_reference)
                    elif canvas == info['canvas']:
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas:
                                canvas_reference = function_info['canvas']
                                rowwidget = Utils.variables['function_canvases'][function_id][varid]['widget']
                                self.remove_row(rowwidget, varid, 'Variable', canvas_reference)
        except Exception as e:
            print(f"Error while clearing variables: {e}")

    #MARK: - Devices Panel Methods
    def add_device_row(self, device_id=None, dev_data=None, canvas_reference=None):
        """Add a new device row"""
        #print(f"Adding device row called with device_id: {device_id}, dev_data: {dev_data}")
        #print(f"Current Utils.devices before adding new device: {Utils.devices}")
        id_dev_generated = False
        if device_id is None:
            while not id_dev_generated:
                device_id = f"device_{str(int(random()*100000))}"
                if device_id not in Utils.devices['main_canvas'].keys():
                    Utils.devices['main_canvas'][device_id] = {
                        'name': '',
                        'type': self.t("main_GUI.devices_tab.output"),
                        'type_index': 0,
                        'PIN': '',
                        'widget': None,
                        'name_input': None,
                        'type_input': None,
                        'value_input': None,
                        'current_state_display': None
                    }
                    id_dev_generated = True
                    break
                else:
                    device_id = None
        else:
            Utils.devices['main_canvas'][device_id] = {
                'name': '',
                'type': self.t("main_GUI.devices_tab.output"),
                'type_index': 0,
                'PIN': '',
                'widget': None,
                'name_input': None,
                'type_input': None,
                'value_input': None,
                'current_state_display': None
            }
        #print(f"Generated device_id: {device_id}")
        self.device_id = device_id
        #print(f"Adding device row {self.device_id}, dev_data: {dev_data}. Current devices: {Utils.devices}")

        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_input = QLineEdit()
        name_input.setPlaceholderText(self.t("main_GUI.devices_tab.name_placeholder"))
        if dev_data and 'name' in dev_data:
            name_input.setText(dev_data['name'])
            Utils.devices['main_canvas'][device_id]['name'] = dev_data['name']
        
        name_input.textChanged.connect(lambda text, d_id=device_id, t="Device", r=canvas_reference: self.name_changed(text, d_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems([self.t("main_GUI.devices_tab.output"), self.t("main_GUI.devices_tab.input"), self.t("main_GUI.devices_tab.button"), "PWM"])
        if dev_data and 'type_index' in dev_data:
            type_input.setCurrentIndex(dev_data['type_index'])
            Utils.devices['main_canvas'][device_id]['type_index'] = dev_data['type_index']
        
        type_input.currentTextChanged.connect(lambda text, d_id=device_id, t="Device", r=canvas_reference, w=type_input: self.type_changed(text, d_id, t, r, w))
        
        value_dev_input = QLineEdit()
        value_dev_input.setPlaceholderText(self.t("main_GUI.devices_tab.pin"))
        if dev_data and 'PIN' in dev_data:
            print(f"Setting initial PIN value for device {device_id}: {dev_data['PIN']}")
            value_dev_input.setText(str(dev_data['PIN']))
            Utils.devices['main_canvas'][device_id]['PIN'] = dev_data['PIN']

        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        value_dev_input.setValidator(validator)
        value_dev_input.textChanged.connect(lambda text, d_id=device_id, t="Device", r=canvas_reference, w=value_dev_input: self.value_changed(text, d_id, t, r, w))
        
        current_state = QLineEdit()
        current_state.setReadOnly(True)
        current_state.setPlaceholderText(self.t("main_GUI.devices_tab.current_state_placeholder"))

        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_input)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(value_dev_input)
        canvas_reference.row_layout.addWidget(current_state)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, d_id=device_id, rw=canvas_reference.row_widget, t="Device", r=canvas_reference: self.remove_row(rw, d_id, t, r))
        
        panel_layout = canvas_reference.dev_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        Utils.devices['main_canvas'][device_id]['widget'] = canvas_reference.row_widget
        Utils.devices['main_canvas'][device_id]['name_input'] = name_input
        Utils.devices['main_canvas'][device_id]['type_input'] = type_input
        Utils.devices['main_canvas'][device_id]['value_input'] = value_dev_input
        Utils.devices['main_canvas'][device_id]['current_state_display'] = current_state

    def Clear_All_Devices(self):
        #print("Clearing all devices")
        dev_ids_to_remove = []
        # Get a SNAPSHOT of variable IDs BEFORE modifying anything
        for canvas, info in Utils.canvas_instances.items():
            if canvas == info['canvas']:
                dev_ids_to_remove += list(Utils.devices['main_canvas'].keys())
            elif canvas == info['function']:
                for function_id, function_info in Utils.functions.items():
                    dev_ids_to_remove += list(Utils.devices['function_canvases'][function_id].keys())
        #print(f"Current Utils.devices before clearing: {Utils.devices}")
        #print(f"Device IDs to remove: {dev_ids_to_remove}")
        # Now remove them
        try:
            for device_id in dev_ids_to_remove:
                #print(f"Removing device_id: {device_id}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas == info['canvas']:
                        canvas_reference = info['canvas']
                        rowwidget = Utils.devices['main_canvas'][device_id]['widget']
                        self.remove_row(rowwidget, device_id, 'Device', canvas_reference)
                    elif canvas == info['function']:
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas:
                                canvas_reference = function_info['canvas']
                                rowwidget = Utils.devices['function_canvases'][function_id][device_id]['widget']
                                self.remove_row(rowwidget, device_id, 'Device', canvas_reference)
        except Exception as e:
            print(f"Error while clearing devices: {e}")
    
    #MARK: - Common Methods
    def remove_row(self, row_widget, var_id, type, canvas_reference=None):
        """Remove a variable row"""
        #print(f"Removing row {var_id} of type {type}")
        if type == "Variable":
                
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        del Utils.variables['main_canvas'][var_id]
                        for input, var_ids in Utils.vars_same.items():
                            if var_id in var_ids:
                                var_ids.remove(var_id)
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.variables['function_canvases'][function_id][var_id]
                                for input, var_ids in Utils.vars_same.items():
                                    if var_id in var_ids:
                                        var_ids.remove(var_id)
                                break
            
            for input2, var in Utils.vars_same.items():
                #print(f"Var {var}, len var {len(var)}")
                if len(var) <= 1:
                    for var_id in var:
                        if info['ref'] == 'canvas':
                            Utils.variables['main_canvas'][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
                        elif info['ref'] == 'function':
                            Utils.variables['function_canvases'][function_id][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.var_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
        elif type == "Device":
                
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        del Utils.devices['main_canvas'][var_id]
                        for input, dev_ids in Utils.devs_same.items():
                            if var_id in dev_ids:
                                dev_ids.remove(var_id)
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.devices['function_canvases'][function_id][var_id]
                                for input, dev_ids in Utils.devs_same.items():
                                    if var_id in dev_ids:
                                        dev_ids.remove(var_id)
                                break
            
            for input2, dev in Utils.devs_same.items():
                #print(f"Dev {dev}, len dev {len(dev)}")
                if len(dev) <= 1:
                    for dev_id in dev:
                        if info['ref'] == 'canvas':
                            Utils.devices['main_canvas'][dev_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
                        elif info['ref'] == 'function':
                            Utils.devices['function_canvases'][function_id][dev_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.dev_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
        #print(f"Deleted variable: {var_id}")
    
    def remove_internal_row(self, row_widget, var_id, type, canvas_reference=None):
        if type == "Variable":
                
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        pass
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.variables['function_canvases'][function_id][var_id]
                                for input, var_ids in Utils.vars_same.items():
                                    if var_id in var_ids:
                                        var_ids.remove(var_id)
                                break
            
            for input2, var in Utils.vars_same.items():
                #print(f"Var {var}, len var {len(var)}")
                if len(var) <= 1:
                    for var_id in var:
                        if info['ref'] == 'canvas':
                            pass
                        elif info['ref'] == 'function':
                            Utils.variables['function_canvases'][function_id][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.internal_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
        elif type == "Device":

            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        pass
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.devices['function_canvases'][function_id][var_id]
                                for input, dev_ids in Utils.devs_same.items():
                                    if var_id in dev_ids:
                                        dev_ids.remove(var_id)
                                break
            
            for input2, dev in Utils.devs_same.items():
                #print(f"Dev {dev}, len dev {len(dev)}")
                if len(dev) <= 1:
                    for dev_id in dev:
                        if info['ref'] == 'canvas':
                            pass
                        elif info['ref'] == 'function':
                            Utils.devices['function_canvases'][function_id][dev_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.internal_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            

    def name_changed(self, text, var_id, type, canvas_reference=None):
        #print(f"Name changed to {text} for {type} with id {var_id}")
        if type == "Variable":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.variables['main_canvas'][var_id]['name'] = text
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.variables['function_canvases'][function_id][var_id]['name'] = text
                                break
            #print(f"Utils.variables before name change: {Utils.variables}")
            # Step 1: Group all var_ids by their name value
            Utils.vars_same.clear() 
            if info['ref'] == 'canvas':
                Utils.variables['main_canvas'][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            elif info['ref'] == 'function':
                Utils.variables['function_canvases'][function_id][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            if info['ref'] == 'canvas':
                for v_id, v_info in Utils.variables['main_canvas'].items():
                    name = v_info['name_input'].text().strip()
                    if name:
                        Utils.vars_same.setdefault(name, []).append(v_id)
            elif info['ref'] == 'function':
                for v_id, v_info in Utils.variables['function_canvases'][function_id].items():
                    name = v_info['name_input'].text().strip()
                    if name:
                        Utils.vars_same.setdefault(name, []).append(v_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.vars_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                if info['ref'] == 'canvas':
                    for v_id in id_list:
                        Utils.variables['main_canvas'][v_id]['name_input'].setStyleSheet(border_col)
                elif info['ref'] == 'function':                
                    for v_id in id_list:
                        Utils.variables['function_canvases'][function_id][v_id]['name_input'].setStyleSheet(border_col)
            #print("Utils.variables:", Utils.variables)
        
        elif type == "Device":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.devices['main_canvas'][var_id]['name'] = text
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.devices['function_canvases'][function_id][var_id]['name'] = text
                                break
            #print(f"Utils.devices before name change: {Utils.devices}")
            # Step 1: Group all var_ids by their name value
            Utils.devs_same.clear() 
            if info['ref'] == 'canvas':
                Utils.devices['main_canvas'][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            elif info['ref'] == 'function':
                Utils.devices['function_canvases'][function_id][var_id]['name_input'].setStyleSheet("border-color: #3F3F3F;")
            if info['ref'] == 'canvas':
                for d_id, d_info in Utils.devices['main_canvas'].items():
                    name = d_info['name_input'].text().strip()
                    if name:
                        Utils.devs_same.setdefault(name, []).append(d_id)
            elif info['ref'] == 'function':
                for d_id, d_info in Utils.devices['function_canvases'][function_id].items():
                    name = d_info['name_input'].text().strip()
                    if name:
                        Utils.devs_same.setdefault(name, []).append(d_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.devs_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                if info['ref'] == 'canvas':
                    for d_id in id_list:
                        Utils.devices['main_canvas'][d_id]['name_input'].setStyleSheet(border_col)
                elif info['ref'] == 'function':                
                    for d_id in id_list:
                        Utils.devices['function_canvases'][function_id][d_id]['name_input'].setStyleSheet(border_col)
            #print("Utils.devices:", Utils.devices)
        for canvas, block in self.opend_inspectors.items():
            self.update_inspector_content(block, canvas=canvas)
    
    def type_changed(self, input, id, type, canvas_reference=None, widget=None):
        #print(f"Updating variable {input}")
        if type == "Variable":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.variables['main_canvas'][id]['type'] = input
                        print(f"Index of type for variable {id} set to {widget.currentIndex()}")
                        Utils.variables['main_canvas'][id]['type_index'] = widget.currentIndex()
                        value_input = Utils.variables['main_canvas'][id]['value_input']
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.variables['function_canvases'][function_id][id]['type'] = input
                                Utils.variables['function_canvases'][function_id][id]['type_index'] = widget.currentIndex()
                                value_input = Utils.variables['function_canvases'][function_id][id]['value_input']
                                break
            if value_input:
                if input == "Int":
                    value_input.setValidator(QIntValidator(-1073741824, 1073741823))
                elif input == "Float":
                    #print("Setting float validator")
                    regex = QRegularExpression(r"^-?[0-9]*\.?[0-9]*$")
                    value_input.setValidator(QRegularExpressionValidator(regex, self))
                    value_input.setMaxLength(14) # Hard caps total characters
                elif input == "Bool":
                    regex = QRegularExpression(r"^[01]$")
                    value_input.setValidator(QRegularExpressionValidator(regex, self))
                    value_input.setMaxLength(1)
                elif input == "String":
                    value_input.setValidator(None)
        elif type == "Device":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.devices['main_canvas'][id]['type'] = input
                        print(f"Index of type for device {id} set to {widget.currentIndex()}")
                        Utils.devices['main_canvas'][id]['type_index'] = widget.currentIndex()
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.devices['function_canvases'][function_id][id]['type'] = input
                                Utils.devices['function_canvases'][function_id][id]['type_index'] = widget.currentIndex()
                                break
    
    def value_changed(self, input, id, type, canvas_reference=None, widget=None):
        #print(f"Updating variable {input}")
        
        if type == "Variable":
            try:
                for v_id, v_info in Utils.variables['main_canvas'].items():
                    if v_id == id:
                        v_type = Utils.variables['main_canvas'][id]['type']
                        break
                print(f"Variable {id} of type {v_type} changed to value: {input}")
                
                if input and widget:
                    if v_type == "Int":
                        clamped_val = max(-1073741824, min(1073741823, int(input)))  # Clamp to 64-bit signed int range
                        next_input = str(clamped_val)
                    elif v_type == "Float":
                        clamped_val = max(-3.4e38, min(3.4e38, float(input)))  # Clamp to float range
                        next_input = f"{clamped_val:2.g}" # Format to 2 significant digits
                    elif v_type == "Bool":
                        clamped_val = max(0, min(1, int(input)))  # Clamp to 0 or 1
                        next_input = str(clamped_val)
                    else:
                        next_input = input  # For strings, just take the input
                
                    if widget.text() != next_input:
                        widget.blockSignals(True)
                        widget.setText(next_input)
                        widget.blockSignals(False)
                        input = next_input

            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.variables['main_canvas'][id]['value'] = input
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.variables['function_canvases'][function_id][id]['value'] = input
                                break
        elif type == "Device":
            try:
                if input and widget:
                    clamped_val = max(0, min(40, int(input)))  # Clamp to valid GPIO pin numbers (0-40 for Raspberry Pi)
                    next_input = str(clamped_val)
                    if widget.text() != next_input:
                        widget.blockSignals(True)
                        widget.setText(next_input)
                        widget.blockSignals(False)
                        input = next_input
            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.devices['main_canvas'][id]['PIN'] = input
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.devices['function_canvases'][function_id][id]['PIN'] = input
                                break    
                                
    def update_current_values(self):
        for var_name, var in Utils.reports['variables'].items():
            for var_id in Utils.variables['main_canvas'].keys():
                if Utils.variables['main_canvas'][var_id]['name'] == var_name:
                    widget = Utils.variables['main_canvas'][var_id]['current_value_display']
                    widget.setText(str(var['value']))
        for dev_name, dev in Utils.reports['devices'].items():
            for dev_id in Utils.devices['main_canvas'].keys():
                if Utils.devices['main_canvas'][dev_id]['name'] == dev_name:
                    widget = Utils.devices['main_canvas'][dev_id]['current_state_display']
                    if Utils.reports['devices'][dev_name]['type'] == "PWM":
                        widget.setText(str(dev['value']) + "%")
                    else:
                        widget.setText(str(dev['state']))
        
    #MARK: - Other Methods
    def compile_code(self):
        """Compile the visual code"""
        try:
            #print("Starting code compilation...")
            Utils.compiler.compile()
            #print("Code compiled successfully")
        except Exception as e:
            print(f"Compilation error: {e}")
            pass

    def on_save_file(self):
        """Save current project"""
        
        name = Utils.project_data.metadata.get('name', 'Untitled')
        if name == 'Untitled':
            self.on_save_file_as()
            Utils.config['opend_project'] = name
            return
        #print(f"Metadata: {Utils.project_data.metadata}")
        #print(f"Saving project as '{name}'")
        if Utils.file_manager.save_project(name):
            print(f"Project '{name}' saved")
            Utils.config['opend_project'] = name

    def on_save_file_as(self):
        """Save current project with new name"""
        self.raise_()  # Bring main window to front

        text, ok = QInputDialog.getText(self, self.t("main_GUI.dialogs.file_dialogs.save_project_as"), 
            self.t("main_GUI.dialogs.file_dialogs.enter_project_name"), QLineEdit.EchoMode.Normal, 
            Utils.project_data.metadata.get('name', ''))
        
        if ok and text:
            Utils.project_data.metadata['name'] = text
            if Utils.file_manager.save_project(text):
                print(f"Project saved as '{text}'")
        
    def on_open_file(self):
        """Open saved project"""
        
        projects = Utils.file_manager.list_projects()
        if not projects:
            QMessageBox.information(self, self.t("main_GUI.dialogs.file_dialogs.no_projects"), self.t("main_GUI.dialogs.file_dialogs.no_saved_projects_found"))
            return
        
        items = [p['name'] for p in projects]
        item, ok = QInputDialog.getItem(self, self.t("main_GUI.dialogs.file_dialogs.open_project"), 
            "Select project:", items, 0, False)
        
        if ok and item:
            self.stop_execution()
            self.wipe_canvas()
            if Utils.file_manager.load_project(item):
                Utils.config['opend_project'] = item
                self.rebuild_from_data()
                #print(f"Project '{item}' loaded")

    def on_open_specific_file(self, file):
        projects = Utils.file_manager.list_projects()
        print(f"Projects available for opening: {[p['name'] for p in projects]} at path: {[p['path'] for p in projects]}. Opening file: {file}")
        if file in [p['name'] for p in projects]:
            print(f"Found project '{file}' for opening")
            self.stop_execution()
            self.wipe_canvas()
            if Utils.file_manager.load_project(file):
                Utils.config['opend_project'] = Utils.project_data.metadata.get('name', 'Untitled')
                self.rebuild_from_data()
                #print(f"Project loaded from '{file_path}'")
        else:
            QMessageBox.warning(self, self.t("main_GUI.dialogs.file_dialogs.open_project"), self.t("main_GUI.dialogs.file_dialogs.project_file_not_found"))

    def clear_canvas(self):
        """Clear the canvas of all blocks and connections"""
        self.Clear_All_Variables()
        self.Clear_All_Devices()
        print(f"Canvas instances to clear: {list(Utils.canvas_instances.keys())}")
        for canvas in Utils.canvas_instances.keys():
            print("Clearing canvas:", canvas)
            if canvas:
                canvas.path_manager.clear_all_paths()
                #print("Cleared all paths")
                widget_ids_to_remove = []
                if canvas.reference == 'canvas':
                    widget_ids_to_remove += list(Utils.main_canvas['blocks'].keys())
                    #print(f"Widget IDs to remove from main canvas: {widget_ids_to_remove}")
                elif canvas.reference == 'function':
                    #print("Clearing function canvas")
                    for f_id, f_info in Utils.functions.items():
                        if canvas == f_info.get('canvas'):
                            widget_ids_to_remove += list(Utils.functions[f_id]['blocks'].keys())
                            #print(f"Widget IDs to remove from function {f_id} canvas: {widget_ids_to_remove}")
                for widget_id in widget_ids_to_remove:
                    if widget_id in Utils.main_canvas['blocks'].keys():
                        block_widget = Utils.main_canvas['blocks'][widget_id]['widget']
                        canvas.remove_block(block_widget)
                        #print(f"Removed block {widget_id} from main canvas")
                    else:
                        for f_id, f_info in Utils.functions.items():
                            if widget_id in Utils.functions[f_id]['blocks'].keys():
                                block_widget = Utils.functions[f_id]['blocks'][widget_id]['widget']
                                canvas.remove_block(block_widget)
                                #print(f"Removed block {widget_id} from function {f_id} canvas")
                QCoreApplication.processEvents()
                
                canvas.update()
    
    def wipe_canvas(self):
        self.close_child_windows()
        
        self.clear_canvas()
        
        self.delete_canvas_instance()
        
        Utils.file_manager.new_project()

        Utils.variables = {
            'main_canvas': {},
            'function_canvases': {}
        }
        Utils.devices = {
            'main_canvas': {},
            'function_canvases': {}
        }

        if self.main_layout is not None:
            print(f"Main layout {self.main_layout} exists, clearing widgets")
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    print(f"Deleting widget: {widget}")
                    widget.setParent(None)
                    widget.deleteLater()
                    
            QWidget().setLayout(self.main_layout)  # Detach layout from main window
            self.main_layout = None

        self.last_canvas = None
        self.blockIDs = {}
        self.execution_thread = None
        self.pico_thread = None
        self.canvas_added = None
        self.pages = {}
        self.page_count = 0
        self.count_w_separator = 0
        self.canvas_count = 0
        self.tab_buttons = []  # Track tab buttons
    
    def on_new_file(self):
        """Create new project"""
        Utils.config['opend_project'] = None
        self.stop_execution()
        self.wipe_canvas()
        
        self.create_canvas_frame()
        
    def delete_canvas_instance(self):
        """Delete a canvas instance from tracking"""
        canvases_to_delete = {}
        for canvas_key, info in list(Utils.canvas_instances.items()):
            canvases_to_delete[canvas_key] = info['canvas']
            if info['ref'] == 'canvas':
                #print(f"Preparing to delete main canvas instance: {canvas_key}")
                canvas_key.new_canvas_button.setParent(None)
                canvas_key.new_canvas_button.deleteLater()

        for canvas in canvases_to_delete:
            #print(f"Deleted canvas instance: {canvas}")
            if canvas.reference == 'canvas':
                canvas.var_button.setParent(None)
                canvas.dev_button.setParent(None)
                canvas.canvas_tab_button.setParent(None)
                canvas.var_button.deleteLater()
                canvas.dev_button.deleteLater()
                canvas.canvas_tab_button.deleteLater()
            elif canvas.reference == 'function':
                canvas.internal_var_button.setParent(None)
                canvas.canvas_tab_button.setParent(None)
                canvas.internal_var_button.deleteLater()
                canvas.canvas_tab_button.deleteLater()
    
    def remove_excess_separators(self, content_widget):
        """
        Deletes ALL separators for a canvas if it has more than one.
        """
        # Check if the list exists and has more than 1 item
        #print(f"Checking separators for canvas: {content_widget}")
        #print(f"Current separators: {getattr(content_widget, 'separators', None)}")
        if hasattr(content_widget, 'separators') and len(content_widget.separators) >= 1:
            #print(f"Found {len(content_widget.separators)} separators. Deleting all...")
            
            # Iterate through the list and remove each separator
            for sep in content_widget.separators:
                sep.setParent(None)
                sep.deleteLater()
                
                # IMPORTANT: Decrement the layout counter to keep indices correct
                self.count_w_separator -= 1

            # Clear the list and the single reference
            content_widget.separators.clear()
            content_widget.separator_container = None
            
            #print("All separators deleted.")    
        
    def close_child_windows(self):
        
        # Close blocks window if it exists
        try:
            if blocksWindow._instance is not None:
                if blocksWindow._instance.is_hidden == False:
                    print("Closing blocks window")
                    blocksWindow._instance.close()
                blocksWindow._instance = None
        except Exception as e:
            print(f"Error closing blocks window: {e}")
            # If instance already deleted, just reset
            blocksWindow._instance = None
        
        # Close Device Settings window if it exists
        try:
            device_settings_window = DeviceSettingsWindow.get_instance(self.current_canvas)
            print("Device settings window instance:", device_settings_window)
            if device_settings_window.is_hidden == False:
                print("Closing device settings window")
                device_settings_window.close()
            DeviceSettingsWindow._instance = None
        except Exception as e:
            print(f"Error closing device settings window: {e}")
            DeviceSettingsWindow._instance = None
        
        try:
            help_window = HelpWindow.get_instance(self.current_canvas)
            if help_window.is_hidden == False:
                print("Closing help window")
                help_window.close()
            HelpWindow._instance = None
        except Exception as e:
            print(f"Error closing help window: {e}")
            HelpWindow._instance = None

    #MARK: - Compile and Upload Methods
    def compile_and_upload(self):
        """
        Main compile and upload method.
        Updated to properly handle RPi execution.
        """
        try:
            # Show compilation message
            QMessageBox.information(
                self,
                self.t("main_GUI.dialogs.progress_dialogs.compiling"),
                self.t("main_GUI.dialogs.progress_dialogs.compilation_message"),
                QMessageBox.StandardButton.Ok
            )
            
            # ===== STEP 1: Compile code =====
            #print("Step 1: Compiling code...")
            Utils.compiler.compile()  # This creates File.py
            #print("Code compiled successfully to File.py")
            
            # ===== STEP 2: Show compiled output =====
            try:
                with open('File.py', 'r') as f:
                    compiled_code = f.read()
                #print("--- Generated Code ---")
                #print(compiled_code)
                #print("--- End of Code ---")
            except FileNotFoundError:
                print("Warning: Could not read compiled File.py")
            
            # ===== STEP 3: Execute based on device type =====
            #print("Step 3: Executing on device...")
            
            rpi_model = Utils.app_settings.rpi_model_index
            
            if rpi_model == 0:  # Pico W
                #print("Target: Pico W (MicroPython)")
                if self.execute_on_pico_w():
                    #print("Code executed successfully!")
                    QMessageBox.information(
                        self,
                        self.t("main_GUI.dialogs.progress_dialogs.success"),
                        self.t("main_GUI.dialogs.progress_dialogs.success_message"),
                        QMessageBox.StandardButton.Ok
                    )
                else:
                    #print("Execution warning - Check device connection")
                    QMessageBox.warning(
                        self,
                        self.t("main_GUI.dialogs.progress_dialogs.execution_issue"),
                        self.t("main_GUI.dialogs.progress_dialogs.execution_issue_message"),
                        QMessageBox.StandardButton.Ok
                    )
            
            elif rpi_model in [1, 2, 3, 4, 5, 6, 7]:  # Raspberry Pi
                #print(f"Target: Raspberry Pi (GPIO) - Model {rpi_model}")
                #Execute on RPi in background thread
                self.execute_on_rpi_ssh_background()
                
                #print("Execution started on Raspberry Pi")
                # Show info (don't show success here - let thread signals handle it)
                QMessageBox.information(
                    self,
                    self.t("main_GUI.dialogs.progress_dialogs.execution_started"),
                    self.t("main_GUI.dialogs.progress_dialogs.execution_message"),
                    QMessageBox.StandardButton.Ok
                )
            
            else:
                print("Unknown device model")
                QMessageBox.critical(
                    self,
                    self.t("main_GUI.dialogs.progress_dialogs.error"),
                    self.t("main_GUI.dialogs.progress_dialogs.unknown_model").format(model=rpi_model),
                    QMessageBox.StandardButton.Ok
                )
        
        except Exception as e:
            print(f"Error: {str(e)}")
            QMessageBox.critical(
                self,
                self.t("main_GUI.dialogs.progress_dialogs.compilation_error"),
                self.t("main_GUI.dialogs.progress_dialogs.compilation_error_message").format(error_details=str(e)),
                QMessageBox.StandardButton.Ok
            )
    
    #MARK: - RPi Execution Thread Signal Handlers
    def on_execution_status(self, status):
        """Handle status updates from execution thread"""
        print(f"[RPi Status] {status}")
    
    def on_execution_output(self, output):
        """Handle output from execution thread"""
        #print(f"[RPi Output] {output}")

        output = str(output).strip()
        if output.startswith("MicroPython") or 'Type "help()"' in output or output == ">>>":
            return

        if '__REPORT__' not in str(output):
            print(output)  # Regular log output
            QMessageBox.information(
                self,
                self.t("main_GUI.dialogs.progress_dialogs.execution_output"),
                output,
                QMessageBox.StandardButton.Ok
            )
        else:
            try:
                # Split by tag to handle cases where output has text before the tag
                parts = str(output).split('__REPORT__')
                
                # parts[0] is garbage/text before the tag
                # parts[1] starts with the JSON, but may have trailing data (newlines, next logs)
                if len(parts) > 1:
                    json_candidate = parts[1]
                    
                    # FIX: Use raw_decode instead of loads.
                    # raw_decode returns a tuple: (json_data, index_where_json_ended)
                    # This ignores any "Extra data" (newlines, subsequent logs) automatically.
                    data, _ = json.JSONDecoder().raw_decode(json_candidate)
                    
                    Utils.reports = data
                    print("Reports received:", Utils.reports)
                    
                    # Update GUI
                    self.update_current_values()
                    
                    # Save local copy
                    Reports_path = Utils.get_base_path() / "Resources"
                    os.makedirs(Reports_path, exist_ok=True)
                    with open(Reports_path / "last_report.json", "w+") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(parts[0])  # Print any text before the tag (optional)
                        
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error (Chunk might be incomplete): {e}")
            except Exception as e:
                print(f"Error processing report: {e}")
    
    def on_execution_error(self, error):
        """Handle errors from execution thread"""
        #print(f"[RPi Error] {error}")
        QMessageBox.critical(
            self,
            self.t("main_GUI.dialogs.progress_dialogs.execution_error"),
            error,
            QMessageBox.StandardButton.Ok
        )

    def on_host_key_verification(self, hostname, key_type, fingerprint):

        reply = QMessageBox.question(
            self,
            self.t("main_GUI.dialogs.progress_dialogs.host_key_verification"),
            self.t("main_GUI.dialogs.progress_dialogs.host_key_verification_message").format(hostname=hostname, key_type=key_type, fingerprint=fingerprint),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.execution_thread.key_prompt_accept = True
        else:
            self.execution_thread.key_prompt_accept = False

        self.execution_thread.key_prompt_event.set()

    def execute_on_pico_w(self):
        """
        Execute on Pico W using native pyboard library (No subprocess/Admin rights needed)
        """
        self.stop_pico_execution()  # Ensure any existing execution is stopped before starting new one
        print("Searching for Pico W...")
        target_port = None
        
        # 1. Auto-detect COM port
        # Look for typical Pico USB IDs or descriptions
        for p in serial.tools.list_ports.comports():
            # VID 2E8A is Raspberry Pi, PID 0005 is Pico
            if (p.vid == 0x2E8A and p.pid == 0x0005) or \
               "Board in FS mode" in p.description or \
               "USB Serial Device" in p.description:
                target_port = p.device
                break
        
        if not target_port:
            QMessageBox.warning(self, "Connection Error", "Could not find Raspberry Pi Pico.\nEnsure it is connected and not in Bootloader mode.")
            return False

        print(f"Found Pico on {target_port}")

        try:
            # 2. Connect directly using Pyboard class
            pyb = Pyboard(target_port, 115200)
            Utils.config['pico_port'] = target_port  # Save for future use
            # Enter Raw REPL (stops current program)
            pyb.enter_raw_repl()
            
            # 3. Upload File.py as main.py
            print("Uploading main.py...")
            with open("File.py", "rb") as f:
                pyb.fs_put("File.py", "main.py")     
            print("Upload complete")

            print("Resetting board to start code...")
            try:
                pyb.exec_("import machine; machine.reset()")  
            except Exception as e:
                print(f"Error during reset command: {e}")
            
            # Give it a moment to flush the command before closing
            QTimer.singleShot(500, lambda: print("Pico should be running now..."))

            try:
                pyb.close()
            except Exception as e:
                print(f"Error closing Pyboard connection: {e}")

            if hasattr(self, 'pico_thread') and self.pico_thread is not None:
                self.pico_thread.stop()
                self.pico_thread.wait()

            self.pico_thread = PicoListenerThread(target_port)
            self.pico_thread.output.connect(self.on_execution_output) # Reuse existing parser
            self.pico_thread.status.connect(self.on_execution_status)
            self.pico_thread.start()

            return True

        except Exception as e:
            print(f"Execution Error: {e}")
            QMessageBox.critical(self, "Execution Error", f"Failed to upload code:\n{str(e)}")
            return False
    
    def stop_pico_execution(self):

        if hasattr(self, 'pico_thread') and self.pico_thread is not None:
            print("Stopping listener thread...")
            self.pico_thread.stop()
            self.pico_thread.wait()
            self.pico_thread = None

        try:
            port = Utils.config.get('pico_port')
            if not port:
                return
            print(f"Connecting to {port} to stop execution...")
            pyb = Pyboard(port, 115200)
            
            pyb.enter_raw_repl()
            pyb.close()

            print("Pico W stopped and reset.")
            
            QMessageBox.information(
                self,
                self.t("main_GUI.dialogs.progress_dialogs.success"),
                "Pico W has been stopped and reset.",
                QMessageBox.StandardButton.Ok
            )

        except Exception as e:
            print(f"Error stopping Pico: {e}")

    def execute_on_rpi_ssh_background(self):
        """
        Execute code on RPi in background thread.
        """
        try:
            # ===== STEP 1: Stop old execution if running =====
            if self.execution_thread is not None and self.execution_thread.isRunning():
                #print("[GUI] Stopping previous execution...")
                self.execution_thread.stop()  # Signal it to stop
                
                # Wait for thread to finish (max 5 seconds)
                if not self.execution_thread.wait(5000):
                    print("[GUI] Warning: Thread didn't stop gracefully")
                    # Optional: Force terminate (not recommended, but available)
                    # self.execution_thread.terminate()
                    pass
                
                #print("[GUI] Previous execution stopped")
            
            # ===== STEP 2: Get RPi settings =====
            rpi_host = Utils.app_settings.rpi_host
            rpi_user = Utils.app_settings.rpi_user
            rpi_password = Utils.app_settings.rpi_password
            
            if not rpi_host or not rpi_user:
                QMessageBox.warning(
                    self,
                    self.t("main_GUI.dialogs.progress_dialogs.config_error"),
                    self.t("main_GUI.dialogs.progress_dialogs.config_error_message"),
                    QMessageBox.StandardButton.Ok
                )
                return
            
            # ===== STEP 3: Create new thread =====
            ssh_config = {
                'filepath': 'File.py',  # Your compiled file
                'rpi_host': rpi_host,
                'rpi_user': rpi_user,
                'rpi_password': rpi_password,
            }
            
            self.execution_thread = RPiExecutionThread(ssh_config)
            
            # Connect signals to UI slots
            self.execution_thread.status.connect(self.on_execution_status)
            self.execution_thread.output.connect(self.on_execution_output)
            self.execution_thread.error.connect(self.on_execution_error)
            self.execution_thread.host_key_verification.connect(self.on_host_key_verification)
            
            # ===== STEP 4: Start execution =====
            self.execution_thread.start()
            print("[GUI] New execution started")
        
        except Exception as e:
            print(f"[GUI]Error: {str(e)}")
            QMessageBox.critical(
                self,
                self.t("main_GUI.dialogs.progress_dialogs.execution_error"),
                self.t("main_GUI.dialogs.progress_dialogs.execution_error_message").format(error_details=str(e)),
                QMessageBox.StandardButton.Ok
            ) 

    
    #MARK: - Rebuild UI from Saved Data
    def rebuild_from_data(self):
        """
        Reconstruct the entire UI from Utils.project_data
        
        Called after loading a project file.
        
        Rebuilds:
        1. All blocks on canvas with their positions
        2. All connections between blocks
        3. Variables in the side panel
        4. Devices in the side panel
        """
        #print("Starting rebuild from saved data...")
        
        self.rebuild_canvas_instances()
        
        self._rebuild_settings()
        
        # Rebuild variable panel
        self._rebuild_variables_panel()
        
        # Rebuild devices panel
        self._rebuild_devices_panel()
        
        # Clear canvas and rebuild blocks
        self._rebuild_blocks()
        
        # Rebuild connections
        self._rebuild_connections()
        
        
        #print("Project rebuild complete")

    def rebuild_canvas_instances(self):
        """Rebuild canvas instances from project data"""
        #print("Rebuilding canvas instances...")
        # Recreate main canvas
        self.create_canvas_frame()
        #print("Main canvas recreated")
        
        # Recreate function canvases
        #print(f"Recreating {len(Utils.project_data.canvases)-1} function canvases from project data...")
        #print(f" Canvas data: {Utils.project_data.canvases}")
        for canvas, canvas_info in Utils.project_data.canvases.items():
            print(f" Recreating canvas: {canvas_info['name']} (Ref: {canvas_info['ref']})")
            name = canvas_info['name']
            if canvas_info['ref'] == 'main_canvas':
                print(" Skipping main canvas, already created")
                continue  # Skip main canvas, already created
            elif canvas_info['ref'] == 'function':
                print(f" Creating function canvas: {canvas_info['name']}")
                new_canvas = GridCanvas()
                new_canvas.GUI = self
                new_canvas.main_window = self.main_window
                new_tab_index = self.add_tab(
                    tab_name=canvas_info['name'],
                    content_widget=new_canvas,
                    reference="function",
                    function_id=canvas_info['id']
                )
                Utils.canvas_instances[new_canvas] = {
                    'canvas': new_canvas,
                    'index': new_tab_index,
                    'ref': 'function',
                    'name': name,
                    'id': canvas_info['id']
                }
        
        #print("Canvas instances rebuilt")
    
    def _rebuild_settings(self):
        """Rebuild settings from project_data"""
        #print(f"Rebuilding {len(Utils.project_data.settings)} settings...")
        #print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        Utils.app_settings.rpi_model = Utils.project_data.settings.get('rpi_model', "RPI 4 model B")
        Utils.app_settings.rpi_model_index = Utils.project_data.settings.get('rpi_model_index', 6)
        #print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        self.current_canvas.update()
        #print(" Settings rebuilt")

    def _rebuild_blocks(self):
        """Recreate all block widgets on canvas from project_data"""
        try:
            for canvas, canvas_info in Utils.canvas_instances.items():
                if canvas_info['ref'] == 'canvas':
                    for block_id, block in Utils.project_data.main_canvas['blocks'].items():
                        self.add_block_from_data(
                            block_type=block['type'],
                            x=block['x'],
                            y=block['y'],
                            block_id=str(block_id),
                            canvas=canvas,
                            name=block['name'] if 'name' in block else None
                        )
                            
                elif canvas_info['ref'] == 'function':
                    print("Rebuilding blocks for function canvas")
                    for function_id, function_info in Utils.functions.items():
                        print(f" Checking function: {function_id}")
                        if function_info['canvas'] == canvas:
                            print(f" Found matching canvas for function: {function_id}")
                            for block_id, block in Utils.project_data.functions[function_id]['blocks'].items():
                                print(f"  Rebuilding block {block_id} of type {block['type']}")
                                self.add_block_from_data(
                                    block_type=block['type'],
                                    x=block['x'],
                                    y=block['y'],
                                    block_id=str(block_id),
                                    canvas=canvas,
                                    name=block['name'] if 'name' in block else None,
                                )
            #print("Blocks rebuilt on canvas")
        except Exception as e:
            print(f"Error rebuilding blocks: {e}")
        

    def add_block_from_data(self, block_type, x, y, block_id, canvas=None, name=None):
        """Add a new block to the canvas"""
        for canvas_key, canvas_info in Utils.canvas_instances.items():
            if canvas_info['canvas'] == canvas:
                if canvas_info['ref'] == 'canvas':
                    data = Utils.project_data.main_canvas['blocks'][block_id]
                    break
                elif canvas_info['ref'] == 'function':
                    for function_id, function_info in Utils.functions.items():
                        if function_info['canvas'] == canvas:
                            data = Utils.project_data.functions[function_id]['blocks'][block_id]
                            break
        print(f" Adding block from data: ID={block_id}, Type={block_type}, X={x}, Y={y}, Canvas {canvas}")
        block = BlockGraphicsItem(
            x=x, y=y,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=canvas,
            conditions=data.get('conditions', 1) if block_type == 'If' else None,
            networks=data.get('networks', 2) if block_type == 'Networks' else None,
            name=name
        )
        for canvas_key, canvas_info in Utils.canvas_instances.items():
            if canvas_info['canvas'] == canvas:
                break
        if block_type in ('While', 'Button', 'Switch', 'Basic_operations', 'Exponential_operations', 'Random_number',
                          'Blink_LED', 'Toggle_LED', 'LED_ON', 'LED_OFF', 'PWM_LED', 'Plus_one', 'Minus_one'):
            block.value_1_name = data.get('value_1_name', "N")
        if block_type in ('While', 'Basic_operations', 'Exponential_operations', 'Random_number'):
            block.value_2_name = data.get('value_2_name', 'N')
        if block_type in ('While', 'Basic_operations', 'Exponential_operations', 'Random_number'):
            block.operator = data.get('operator', "==")
        if block_type in ('Basic_operations', 'Exponential_operations', 'Random_number'):
            block.result_var_name = data.get('result_var_name', "result")
        if block_type in ('Timer', 'Blink_LED'):
            block.sleep_time = data.get('sleep_time', "1000")
        if block_type in ('PWM_LED'):
            block.PWM_value = data.get('PWM_value', "50")
        if block_type == 'If':
            for i in range(data.get('conditions', 1)):
                str_1 = f"value_{i+1}_1_name"
                str_2 = f"value_{i+1}_2_name"
                str_op = f"operator_{i+1}"
                setattr(block, str_1, data['first_vars'].get(str_1, f"N"))
                setattr(block, str_2, data['second_vars'].get(str_2, f"N"))
                setattr(block, str_op, data['operators'].get(str_op, "=="))
        if block_type == 'RGB_LED':
            for i in range(1, 4):
                str_1 = f"value_{i}_1_name"
                str_2 = f"value_{i}_2_PWM"
                setattr(block, str_1, data['first_vars'].get(str_1, f"N"))
                setattr(block, str_2, data['second_vars'].get(str_2, f"N"))
                
        canvas.scene.addItem(block)
        
        # Store in Utils
        if canvas_info['ref'] == 'canvas':
            Utils.main_canvas['blocks'][block_id] = Utils.data_control.load_from_data(block, block_id, block_type, x, y, canvas, 'canvas')
        if canvas_info['ref'] == 'function':
            Utils.functions[function_id]['blocks'][block_id] = Utils.data_control.load_from_data(block, block_id, block_type, x, y, canvas, 'function')
        block.connect_graphics_signals()
        return block

    def _rebuild_connections(self):
        """Recreate all connection paths from projectdata"""
        for canvas, canvas_info in Utils.canvas_instances.items():
            if canvas_info['ref'] == 'canvas':
                #print(f"Rebuilding {len(Utils.project_data.main_canvas['paths'])} connections...")
                #print(f"Utils.top_infos contains: {list(Utils.main_canvas['blocks'].keys())}")
                #print(f"Project connections: {list(Utils.project_data.main_canvas['paths'].keys())}")
                #print(f"Path conections before rebuild: {Utils.project_data.main_canvas['paths']}")
            
                for conn_id, conn_data in Utils.project_data.main_canvas['paths'].items():
                    try:
                        from_block_id = str(conn_data.get("from"))
                        to_block_id = str(conn_data.get("to"))
                        
                        #print(f"Processing connection {conn_id}: {from_block_id} -> {to_block_id}")
                        
                        # DEBUG: Check what's actually in Utils.top_infos
                        #print(f"Available block IDs in Utils.top_infos: {list(Utils.main_canvas['blocks'].keys())}")
                        #print(f"Is {from_block_id} in top_infos? {from_block_id in Utils.main_canvas['blocks']}")
                        #print(f"Is {to_block_id} in top_infos? {to_block_id in Utils.main_canvas['blocks']}")
                        
                        if from_block_id not in Utils.main_canvas['blocks'] or to_block_id not in Utils.main_canvas['blocks']:
                            print(f"Connection {conn_id}: Missing block reference!")
                            #print(f"  from_block_id ({from_block_id}) exists: {from_block_id in Utils.main_canvas['blocks']}")
                            #print(f"  to_block_id ({to_block_id}) exists: {to_block_id in Utils.main_canvas['blocks']}")
                            continue
                        
                        from_block = Utils.main_canvas['blocks'][from_block_id]
                        to_block = Utils.main_canvas['blocks'][to_block_id]
                        
                        from_blockwidget = from_block.get("widget")
                        to_blockwidget = to_block.get("widget")
                        
                        path_item = PathGraphicsItem(
                            from_block=from_blockwidget,
                            to_block=to_blockwidget,
                            path_id=conn_id,
                            parent_canvas=canvas,
                            to_circle_type=conn_data.get("to_circle_type", "in"),
                            from_circle_type=conn_data.get("from_circle_type", "out"),
                            waypoints=conn_data.get("waypoints", [])
                        )
                        canvas.scene.addItem(path_item)
                        # Recreate connection
                        Utils.main_canvas['paths'][conn_id] = {
                            'from': from_block_id,
                            'from_circle_type': conn_data.get("from_circle_type", "out"),
                            'to': to_block_id,
                            'to_circle_type': conn_data.get("to_circle_type", "in"),
                            'waypoints': conn_data.get("waypoints", []),
                            'canvas': canvas,
                            'color': QColor(31, 83, 141),
                            'item': path_item
                        }
                        #print(f"Recreated path in Utils.main_canvas: {Utils.main_canvas['paths'][conn_id]}")
                        Utils.scene_paths[conn_id] = path_item
                        
                        # Update block connection references
                        if conn_id not in from_block["out_connections"].keys():
                            from_block["out_connections"][conn_id] = conn_data.get("from_circle_type", "out")
                        if conn_id not in to_block["in_connections"].keys():
                            to_block["in_connections"][conn_id] = conn_data.get("to_circle_type", "in")
                        
                        #print(f"Connection {conn_id} recreated")
                        
                    except Exception as e:
                        print(f"Error recreating connection {conn_id}: {e}")
                        import traceback
                        traceback.print_exc()
            elif canvas_info['ref'] == 'function':
                for function_id, function_info in Utils.functions.items():
                    #print(f" Checking function: {function_id}")
                    if function_info['canvas'] == canvas:
                        #print(f" Found matching canvas for function: {function_id}")
                        #print(f"Rebuilding {len(Utils.project_data.functions[function_id]['paths'])} connections...")
                        #print(f"Utils.top_infos contains: {list(Utils.functions[function_id]['blocks'].keys())}")
                        #print(f"Project connections: {list(Utils.project_data.functions[function_id]['paths'].keys())}")
                        #print(f"Path conections before rebuild: {Utils.project_data.functions[function_id]['paths']}")
                    
                        for conn_id, conn_data in Utils.project_data.functions[function_id]['paths'].items():
                            try:
                                from_block_id = str(conn_data.get("from"))
                                to_block_id = str(conn_data.get("to"))
                                
                                #print(f"Processing connection {conn_id}: {from_block_id} -> {to_block_id}")
                                
                                # DEBUG: Check what's actually in Utils.top_infos
                                #print(f"Available block IDs in Utils.top_infos: {list(Utils.functions[function_id]['blocks'].keys())}")
                                #print(f"Is {from_block_id} in top_infos? {from_block_id in Utils.functions[function_id]['blocks']}")
                                #print(f"Is {to_block_id} in top_infos? {to_block_id in Utils.functions[function_id]['blocks']}")
                                
                                if from_block_id not in Utils.functions[function_id]['blocks'] or to_block_id not in Utils.functions[function_id]['blocks']:
                                    print(f"Connection {conn_id}: Missing block reference!")
                                    #print(f"  from_block_id ({from_block_id}) exists: {from_block_id in Utils.functions[function_id]['blocks']}")
                                    #print(f"  to_block_id ({to_block_id}) exists: {to_block_id in Utils.functions[function_id]['blocks']}")
                                    continue
                                
                                from_block = Utils.functions[function_id]['blocks'][from_block_id]
                                to_block = Utils.functions[function_id]['blocks'][to_block_id]
                                
                                from_blockwidget = from_block.get("widget")
                                to_blockwidget = to_block.get("widget")
                                
                                path_item = PathGraphicsItem(
                                    from_block=from_blockwidget,
                                    to_block=to_blockwidget,
                                    path_id=conn_id,
                                    parent_canvas=canvas,
                                    to_circle_type=conn_data.get("to_circle_type", "in"),
                                    from_circle_type=conn_data.get("from_circle_type", "out"),
                                    waypoints=conn_data.get("waypoints", [])
                                )
                                canvas.scene.addItem(path_item)
                                # Recreate connection
                                Utils.functions[function_id]['paths'][conn_id] = {
                                    'from': from_block_id,
                                    'from_circle_type': conn_data.get("from_circle_type", "out"),
                                    'to': to_block_id,
                                    'to_circle_type': conn_data.get("to_circle_type", "in"),
                                    'waypoints': conn_data.get("waypoints", []),
                                    'canvas': canvas,
                                    'color': QColor(31, 83, 141),
                                    'item': path_item
                                }
                                #print(f"Recreated path in Utils.functions for {function_id}: {Utils.functions[function_id]['paths'][conn_id]}")
                                Utils.scene_paths[conn_id] = path_item
                                
                                # Update block connection references
                                if conn_id not in from_block["out_connections"].keys():
                                    from_block["out_connections"][conn_id] = conn_data.get("from_circle_type", "out")
                                if conn_id not in to_block["in_connections"].keys():
                                    to_block['in_connections'][conn_id] = conn_data.get("to_circle_type", "in")
                                
                                #print(f"Connection {conn_id} recreated")
                                
                            except Exception as e:
                                print(f"Error recreating connection {conn_id}: {e}")
                                import traceback
                                traceback.print_exc()
                                
        for canvas, canvas_info in Utils.canvas_instances.items():
            canvas.scene.update()
            
        
    def _rebuild_variables_panel(self):
        """Recreate variables in the side panel"""
        #print(f"Rebuilding {len(Utils.project_data.variables)} variables...")
        #print(f" Project variables data: {Utils.project_data.variables}")
        for canvas, canvas_info in Utils.canvas_instances.items():
            #print(f" Canvas: {canvas_info['name']} (Ref: {canvas_info['ref']})")
            if canvas_info['ref'] == 'canvas':
                #print(" Recreating variables for main canvas")
                for var_id, var_info in list(Utils.project_data.variables['main_canvas'].items()):
                    #print(f"  Recreating variable {var_id} on main canvas")
                    self.add_variable_row(var_id, var_info, canvas)
                print(f"Variables after main canvas rebuild: {Utils.variables['main_canvas']}")
            elif canvas_info['ref'] == 'function':
                #print(f" Recreating variables for function canvas: {canvas_info['name']}")
                for var_id, var_info in list(Utils.project_data.variables['function_canvases'][canvas_info['id']].items()):
                    #print(f"  Recreating variable {var_id} on function canvas")
                    self.add_internal_variable_row(var_id, var_info, canvas)
                print(f"Variables after function canvas rebuild: {Utils.variables['function_canvases'][canvas_info['id']]}")

    def _rebuild_devices_panel(self):
        """Recreate devices in the side panel"""
        #print(f"Rebuilding {len(Utils.project_data.devices)} devices...")
        
        for canvas, canvas_info in Utils.canvas_instances.items():
            #print(f" Canvas: {canvas_info['name']} (Ref: {canvas_info['ref']})")
            if canvas_info['ref'] == 'canvas':
                #print(" Recreating devices for main canvas")
                for dev_id, dev_info in list(Utils.project_data.devices['main_canvas'].items()):
                    #print(f"  Recreating device {dev_id} on main canvas")
                    self.add_device_row(dev_id, dev_info, canvas)
                print(f"Devices after main canvas rebuild: {Utils.devices['main_canvas']}")
            elif canvas_info['ref'] == 'function':
                #print(f" Recreating devices for function canvas: {canvas_info['name']}")
                for dev_id, dev_info in list(Utils.project_data.devices['function_canvases'][canvas_info['id']].items()):
                    #print(f"  Recreating device {dev_id} on function canvas")
                    self.add_internal_device_row(dev_id, dev_info, canvas)
                print(f"Devices after function canvas rebuild: {Utils.devices['function_canvases'][canvas_info['id']]}")