from Imports import get_State_Machine, logging

AppStateMachine, CanvasStateMachine = get_State_Machine()

class StateManager:
    """Central state management for entire application"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            #logging.info("Creating StateManager instance")
            cls._instance = super().__new__(cls)
        #logging.info("Returning StateManager instance")
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            #logging.info("Initializing StateManager")
            self.canvas_state = CanvasStateMachine()
            self.app_state = AppStateMachine(canvas_state_machine=self.canvas_state)
            #logging.info(f"StateManager canvas_state id: {id(self.canvas_state)}")
            #logging.info(f"AppStateMachine canvas_state_machine id: {id(self.app_state.canvas_state_machine)}")
            self.initialized = True
    
    @classmethod
    def get_instance(cls):
        #logging.info("Getting StateManager instance")
        return cls()