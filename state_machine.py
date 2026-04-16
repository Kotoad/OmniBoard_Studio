from enum import Enum, auto

from Imports import pyqtSignal, QObject, logging


class CanvasState(Enum):
    IDLE = auto()
    ADDING_BLOCK = auto()
    ADDING_PATH = auto()
    MOVING_ITEM = auto()
    DELETING_ITEM = auto()

class CanvasStateMachine(QObject):
    state_changed = pyqtSignal(CanvasState)

    def __init__(self):
        super().__init__()
        #logging.info("canvas state machine initialized with IDLE state")
        self.state = CanvasState.IDLE
        #logging.info(f"Current state: {self.state.name}")
    
    def can_place_block(self):
        return self.state == CanvasState.IDLE

    def can_move_item(self):
        return self.state in {CanvasState.IDLE, CanvasState.MOVING_ITEM}
    
    def can_delete_item(self):
        return self.state == CanvasState.IDLE
    
    def can_add_path(self):
        return self.state == CanvasState.IDLE

    def can_idle(self):
        return self.state != CanvasState.IDLE

    def on_adding_block(self):
        if self.can_place_block():
            self.change_state(CanvasState.ADDING_BLOCK)
            return True
        return False

    def on_moving_item(self):
        if self.can_move_item():
            self.change_state(CanvasState.MOVING_ITEM)
            return True
        return False

    def on_deleting_item(self):
        if self.can_delete_item():
            self.change_state(CanvasState.DELETING_ITEM)
            return True
        return False
    
    def on_adding_path(self):
        if self.can_add_path():
            self.change_state(CanvasState.ADDING_PATH)
            return True
        return False
    
    def on_idle(self):
        if self.can_idle():
            self.change_state(CanvasState.IDLE)
            return True
        return False

    def change_state(self, new_state: CanvasState):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(self.state)
            #logging.info(f"State changed to: {self.state.name}")
        else:
            #logging.info(f"State remains: {self.state.name}")
            pass

    def current_state(self):
        if self.state.name:
            return self.state.name
        return None

class AppStates(Enum):
    MAIN_WINDOW = auto()
    SETTINGS_DIALOG = auto()
    HELP_DIALOG = auto()
    BLOCKS_DIALOG = auto()
    COMPILING = auto()

class AppStateMachine(QObject):

    state_changed = pyqtSignal(AppStates)
    window_opened = pyqtSignal(str)
    window_closed = pyqtSignal(str)

    def __init__(self, canvas_state_machine=None):
        super().__init__()
        self.state = AppStates.MAIN_WINDOW
        self.open_windows = set()
        self.canvas_state_machine = canvas_state_machine or CanvasStateMachine()
        self.current_tab_reference = None
    
    def can_open_window(self, window_name: str):
        return self.canvas_state_machine.current_state() == 'IDLE'
    
    def can_close_window(self, window_name: str):
        return window_name in self.open_windows

    def can_compile(self):
        return self.state != AppStates.COMPILING
    
    def can_change_tab(self):
        return self.state != AppStates.BLOCKS_DIALOG and self.canvas_state_machine.current_state() == 'IDLE'

    def can_create_canvas_tab(self):
        return self.state == AppStates.MAIN_WINDOW and self.canvas_state_machine.current_state() == 'IDLE'

    def on_main_window(self):
        if self.can_go_to_main_window():
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False
    
    def on_settings_dialog_open(self):
        if self.can_open_window('Settings'):
            self.open_windows.add('Settings')
            self.window_opened.emit('Settings')
            self.change_state(AppStates.SETTINGS_DIALOG)
            return True
        return False
    
    def on_settings_dialog_close(self):
        if self.can_close_window('Settings'):
            self.open_windows.discard('Settings')
            self.window_closed.emit('Settings')
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_help_dialog_open(self):
        if self.can_open_window('Help'):
            self.open_windows.add('Help')
            self.window_opened.emit('Help')
            self.change_state(AppStates.HELP_DIALOG)
            return True
        return False
    
    def on_help_dialog_close(self):
        if self.can_close_window('Help'):
            self.open_windows.discard('Help')
            self.window_closed.emit('Help')
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_blocks_dialog_open(self):
        #logging.debug(f"Attempting to open Blocks dialog from tab: {self.current_tab_reference}")
        if self.can_open_window('Blocks') and self.current_tab_reference in ('canvas', 'function'):
            #logging.info(f"Opening Blocks dialog from tab: {self.current_tab_reference}")
            self.open_windows.add('Blocks')
            self.window_opened.emit('Blocks')
            self.change_state(AppStates.BLOCKS_DIALOG)
            return True
        logging.warning("Cannot open Blocks dialog: either already open or invalid tab.")
        return False
    
    def on_blocks_dialog_close(self):
        if self.can_close_window('Blocks'):
            self.open_windows.discard('Blocks')
            self.window_closed.emit('Blocks')
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_compiling_start(self):
        if self.can_compile():
            self.change_state(AppStates.COMPILING)
            return True
        return False

    def on_compiling_finish(self):
        if self.state == AppStates.COMPILING:
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_code_viewer_dialog_open(self):
        if self.can_open_window('CodeViewer'):
            self.open_windows.add('CodeViewer')
            self.window_opened.emit('CodeViewer')
            return True
        return False

    def on_code_viewer_dialog_close(self):
        if self.can_close_window('CodeViewer'):
            self.open_windows.discard('CodeViewer')
            self.window_closed.emit('CodeViewer')
            return True
        return False

    def on_code_editor_dialog_open(self):
        if self.can_open_window('EditCode'):
            self.open_windows.add('EditCode')
            self.window_opened.emit('EditCode')
            return True
        return False
    
    def on_code_editor_dialog_close(self):
        if self.can_close_window('EditCode'):
            self.open_windows.discard('EditCode')
            self.window_closed.emit('EditCode')
            return True
        return False

    def on_tab_changed(self):
        #logging.debug(f"Check {self.state != AppStates.BLOCKS_DIALOG and self.canvas_state_machine.current_state() == 'IDLE'} to go to MAIN_WINDOW")
        #logging.debug(f"Current state: {self.state}, Canvas state: {self.canvas_state_machine.current_state()}")
        if self.can_change_tab():
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_tab_created(self):
        if self.can_create_canvas_tab():
            self.change_state(AppStates.MAIN_WINDOW)
            return True

    def change_state(self, new_state: AppStates):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(self.state)
            #logging.info(f"App state changed to: {self.state.name}")
        else:
            #logging.info(f"App state remains: {self.state.name}")
            pass