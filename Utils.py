from Imports import AppSettings, ProjectData, sys, os, Path
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
    'CURRENT_VERSION': "v0.22.17",
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