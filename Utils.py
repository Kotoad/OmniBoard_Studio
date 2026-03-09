from Imports import AppSettings, ProjectData, sys, os, Path
if sys.platform == 'win32':
    from ctypes import windll, wintypes, byref
app_settings = AppSettings()
project_data = ProjectData()
# ============================================================================
# GLOBAL DICTIONARIES - Data Storage for the Visual Programming System
# ============================================================================

runtime_widgets = {
    'blocks': {},      # block_id -> QWidget
    'lines': {},       # connection_id -> QLine
}

paths = {}
variables = {
    'main_canvas': {},      
    'function_canvases': {} 
}

devices = {
    'main_canvas': {},      
    'function_canvases': {} 
}
vars_same = {}
devs_same = {}
var_items = {}
dev_items = {}
scene_paths = {}
functions = {}
main_canvas = {}
canvas_instances = {}
reports = {}

config = {
    'grid_size': 25,  # Snap-to-grid pixel size
    'pico_port': None,  # Serial port for Pico W (auto-detected)
    'opend_project': None,  # Currently opened project name
    'CURRENT_VERSION': "V0.14",
}

compiler = None
state_manager = None
translation_manager = None
file_manager = None
data_control = None
add_block_command = None
# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_dpi_for_monitor(window_id):
    """
    Get DPI scaling factors for the monitor containing the window.
    
    Why Use This?
    - Different monitors have different DPI (dots per inch)
    - Modern high-resolution displays need scaling to render UI blocks at correct size
    - Example: A 27" 1440p monitor has ~110 DPI, needs 1.15x scaling for readability
    - Example: A 15" laptop with 4K has ~294 DPI, needs ~3x scaling
    
    Args:
        window_id: Native window handle (HWND on Windows)
    
    Returns:
        Tuple[float, float]: (scaling_factor_x, scaling_factor_y)
        - (1.0, 1.0) = 96 DPI (standard, no scaling)
        - (1.5, 1.5) = 144 DPI (150% scale - high-res display)
        - (2.0, 2.0) = 192 DPI (200% scale - very high-res display)
    
    Edge Cases (What To Watch For):
        - If DPI query fails, returns (1.0, 1.0) as safe default
        - Works on Windows; other platforms need different implementation
        - Window spanning multiple monitors: uses nearest monitor's DPI
    
    Example Usage:
        scale_x, scale_y = get_dpi_for_monitor(hwnd)
        scaled_font_size = 12 * scale_x
        scaled_block_width = 100 * scale_x
    """
    DPI_100_PC = 96  # Windows standard DPI (100% scale) - baseline reference
    
    if sys.platform != 'win32':
        # Non-Windows platforms: DPI handling is different (e.g., Linux with X11/Wayland, macOS)
        # For simplicity, return (1.0, 1.0) as default scaling on unsupported platforms
        return (1.0, 1.0)

    try:
        # Get handle for monitor containing the window
        # MONITOR_DEFAULTTONEAREST (2) = use nearest monitor if window spans multiple displays
        monitor = windll.user32.MonitorFromWindow(window_id, 2)
        
        # Create variables to hold DPI values (Windows API requirement)
        dpi_x = wintypes.UINT()
        dpi_y = wintypes.UINT()
        
        # Query the monitor's DPI
        # MDT_EFFECTIVE_DPI = 0 (what the user actually sees, accounting for overrides)
        windll.shcore.GetDpiForMonitor(monitor, 0, byref(dpi_x), byref(dpi_y))
        
        # Calculate scaling: 144 DPI display = 144/96 = 1.5x scale
        scaling_factor_x = dpi_x.value / DPI_100_PC
        scaling_factor_y = dpi_y.value / DPI_100_PC
        
        return (scaling_factor_x, scaling_factor_y)
    
    except Exception:
        # Defaults if unable to get DPI
        # Reasons this might fail:
        #   - Running on non-Windows platform
        #   - Windows API unavailable
        #   - Window handle invalid
        # Safe fallback: assume no scaling needed (96 DPI standard)
        return (1.0, 1.0)

def get_base_path():
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (compiled .exe),
        # the PyInstaller bootloader sets the sys.frozen attribute
        # and sys.executable points to the .exe file itself.
        return Path(os.path.dirname(sys.executable))
    else:
        # If running as a normal Python script
        return Path(os.path.dirname(os.path.abspath(__file__)))