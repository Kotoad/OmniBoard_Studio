from Imports import get_Utils, logging
Utils = get_Utils()

#MARK: Code Compiler
class CodeCompiler:
    def __init__(self):
        self.file = None
        self.indent_level = 0
        self.memory_indent_level = 0
        self.indent_str = "    "  # 4 spaces
        self.MC_compile = False  # Microcontroller mode flag
        self.GPIO_compile = False  # GPIO mode flag
        self.compiling_function = None  # Current function being compiled
        self.compiling_what = 'canvas'  # 'canvas' or 'function'
        self.header_lines = []
        self.main_lines = []
        self.function_lines = []
        self.footer_lines = []
        self.last_block = None
        self.btn_in_code = False
        self.led_in_code = False
        self.current_lines = self.header_lines  # Pointer to current lines being written
        self.process_map = {
            'If': self.handle_if_block,
            'While': self.handle_while_block,
            'While_true': self.handle_while_block,
            'Timer': self.handle_timer_block,
            'End': self.handle_end_block,
            'Switch': self.handle_switch_block,
            'Button': self.handle_button_block,
            'Blink_LED': self.handle_LED_block,
            'Toggle_LED': self.handle_LED_block,
            'PWM_LED': self.handle_LED_block,
            'RGB_LED': self.handle_LED_block,
            'LED_ON': self.handle_LED_block,
            'LED_OFF': self.handle_LED_block,
            "Plus": self.handle_math_block,
            "Minus": self.handle_math_block,
            "Multiply": self.handle_math_block,
            "Divide": self.handle_math_block,
            "Modulo": self.handle_math_block,
            "Power": self.handle_math_block,
            "Root": self.handle_math_block,
            "Plus_one": self.handle_math_block,
            "Minus_one": self.handle_math_block,
            "Random_number": self.handle_rand_block,
            "Lower": self.handle_logic_block,
            "Greater": self.handle_logic_block,
            "Equal": self.handle_logic_block,
            "Not_equal": self.handle_logic_block,
            "Greater_equal": self.handle_logic_block,
            "Lower_equal": self.handle_logic_block,
            "Function": self.handle_function_block,
            "Networks": self.handle_networks_block,
            "Return": self.handle_return_block
        }
    
    def compile(self):
        """Main entry point"""
        self.MC_compile = False
        self.GPIO_compile = False
        self.indent_level = 0
        self.header_lines = []
        self.main_lines = []
        self.function_lines = []
        self.footer_lines = []
        self.current_lines = self.header_lines
        #logging.info("Compiling code to File.py...")
        #logging.info(f"RPI Model: {Utils.app_settings.rpi_model}")
        #logging.info(f"RPI Model Index: {Utils.app_settings.rpi_model_index}")
        if Utils.app_settings.rpi_model_index == 0:
            #logging.info(f"RPI Model selected: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
            self.MC_compile = True
        elif Utils.app_settings.rpi_model_index in (1,2,3,4,5,6,7):
            #logging.info(f"RPI Model selected: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
            self.GPIO_compile = True

        self.func_to_compile = {}

        for func_id, func_info in Utils.functions.items():
            #logging.info(f"Registering function for compilation: {func_info['name']} (ID: {func_id})")
            if func_id not in self.func_to_compile:
                #logging.info(f"Adding function '{func_info['name']}' to compilation list with ID: {func_id}")
                self.func_to_compile[func_id] = func_info['name'], "Not Compiled", ""

        self.create_hashmap()

        self.write_imports()
        self.write_setup()
        self.write_reporting_system()
        
        self.current_lines = self.main_lines
        # Find Start block
        start_block = self.find_block_by_type('Start')
        if start_block:
            #logging.info(f"Found Start block: {start_block['id']}")
            self.writeline("try:")
            self.indent_level += 1
            if self.GPIO_compile:
                #self.writeline("print(\"System booting... waiting 1.5s\", flush=True)")
                pass
            if self.MC_compile:
                #self.writeline("print(\"System booting... waiting 1.5s\")")
                pass
            self.writeline("time.sleep(1.5)  # Initial delay to allow reporter thread to start and stabilize")
            if self.led_in_code:
                self.writeline("led = LED()")
            if self.btn_in_code:
                self.writeline("btn = Button()")
            if self.GPIO_compile:
                self.writeline("report_thread = threading.Thread(target=data_reporter, daemon=True)")
                self.writeline("report_thread.start()")
            elif self.MC_compile:
                self.writeline("_thread.start_new_thread(data_reporter, ())")
            next_id = self.get_next_block(start_block['id'])
            #logging.info(f"Processing blocks starting from: {next_id}")
            self.process_block(next_id)
            self.indent_level -= 1
        self.current_lines = self.footer_lines
        self.write_cleanup()
        file = open("File.py", "w")
        if file:
            file.writelines(self.header_lines)
            file.writelines(self.function_lines)
            file.writelines(self.main_lines)
            file.writelines(self.footer_lines)
            #logging.info("Code written to File.py")
        else:
            logging.error("Error opening File.py for writing")
        file.close()
            
    

    def process_block(self, block_id):
        """Process single block - dispatch to handler"""
        if not block_id:
            return
        if self.compiling_what == 'canvas':
            block = Utils.main_canvas['blocks'][block_id]
        elif self.compiling_what == 'function':
            block = Utils.functions[self.compiling_function]['blocks'][block_id]

        #logging.info(f"Processing block {block_id} of type {block['type']}")
        
        handler = self.process_map.get(block['type'])
        if handler:
            handler(block)
        else:
            logging.warning(f"No handler for block type: {block['type']} (Block ID: {block_id})")
    #MARK: Code Setup
    def write_imports(self):
        #logging.info("Writing import statements...")
        if self.GPIO_compile:
            self.writeline("import RPi.GPIO as GPIO")
            self.writeline("import time")
            self.writeline("import sys")
            self.writeline("import signal")
            self.writeline("import threading")
            self.writeline("import json\n")
            
        elif self.MC_compile:
            self.writeline("import machine")
            self.writeline("import time")
            self.writeline("import sys")
            self.writeline("import _thread")
            self.writeline("import json\n")

    def write_setup(self):
        #logging.info("Writing setup code...")
        self.writeline("shutdown = False\n")
        self.writeline("reporter_running = False  # Flag to control reporter thread\n")
        self.writeline("last_report = ''")
        self.writeline("printed_report = False  # Flag to track if we've printed at least one report\n")
        if self.GPIO_compile:
            self.writeline("data_lock = threading.Lock()  # Lock for synchronizing access to shared data if needed\n")
            self.writeline("# Gracefully handle SIGTERM (pkill)")
            self.writeline("def handle_sigterm(signum, frame):")
            self.indent_level += 1
            self.writeline("sys.exit(0)")
            self.indent_level -= 1
            self.writeline("signal.signal(signal.SIGTERM, handle_sigterm)\n")
            self.writeline("signal.signal(signal.SIGINT, handle_sigterm)\n")
            self.writeline("# Preventive cleanup to reset any dirty pins")
            # Smart Cleanup: Silence warnings just for this preventive step
            #self.writeline("GPIO.setwarnings(False)")
            self.writeline("try:")
            self.indent_level += 1
            self.writeline("for mode in [GPIO.BCM, GPIO.BOARD]:")
            self.indent_level += 1
            self.writeline("GPIO.setmode(mode)")
            self.writeline("GPIO.cleanup()")
            self.indent_level -= 2
            self.writeline("except: pass")
            # Re-enable warnings so you still see legitimate errors later
            self.writeline("GPIO.setmode(GPIO.BCM)\n")
            self.writeline("Devices_main = {")
            self.indent_level+=1
            for dev_name, dev_info in Utils.devices['main_canvas'].items():
                #logging.debug(f"Compiling device: {dev_info['name']} (PIN: {dev_info['PIN']}, Type Index: {dev_info['type_index']})")
                if dev_info['type_index'] == 0:
                    dev_type_str = "Output"
                elif dev_info['type_index'] == 1:
                    dev_type_str = "Input"
                elif dev_info['type_index'] == 2:
                    dev_type_str = "Button"
                elif dev_info['type_index'] == 3:
                    dev_type_str = "PWM"
                text = f"\"{dev_info['name']}\":{{\"name\":\"{dev_info['name']}\", \"PIN\": {dev_info['PIN']}, \"type\":\"{dev_type_str}\", \"state\": None}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}\n")
            self.writeline("# Force reinitialization of GPIO pins")
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['type'] in ['Output', 'PWM']:")
            self.indent_level += 1
            self.writeline("try:")
            self.indent_level += 1
            self.writeline("GPIO.cleanup(dev_config['PIN'])")
            self.indent_level -= 1
            self.writeline("except: pass")
            self.indent_level -= 2
            #self.writeline("GPIO.setwarnings(True)\n")
            self.writeline("")
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level+=1
            self.writeline("if dev_config['type'] == 'Output':")
            self.indent_level+=1
            self.writeline(f"GPIO.setup(dev_config['PIN'], GPIO.OUT, initial=GPIO.LOW)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Input':")
            self.indent_level+=1
            self.writeline(f"GPIO.setup(dev_config['PIN'], GPIO.IN)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Button':")
            self.indent_level+=1
            self.writeline(f"GPIO.setup(dev_config['PIN'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)")
            self.indent_level-=1
            self.writeline("if dev_config['type'] == 'PWM':")
            self.indent_level+=1
            self.writeline("GPIO.setup(dev_config['PIN'], GPIO.OUT)")
            self.writeline("PWM_instance = GPIO.PWM(dev_config['PIN'], 1000)")
            self.writeline("PWM_instance.start(0)")
            self.writeline("if 'CurrentDutyCycle' not in dev_config:")
            self.indent_level+=1
            self.writeline("dev_config['CurrentDutyCycle'] = 0")
            self.indent_level-=1
            self.writeline("if 'PWM_instance' not in dev_config:")
            self.indent_level+=1
            self.writeline("dev_config['PWM_instance'] = PWM_instance")
            self.indent_level-=3
            #self.writeline("GPIO.setwarnings(True)")

            self.writeline("Variables_main = {")
            self.indent_level+=1
            for var_name, var_info in Utils.variables['main_canvas'].items():
                text = f"\"{var_info['name']}\":{{"f"\"value\": {var_info['value']}}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}\n")
            
        elif self.MC_compile:
            self.writeline("data_lock = _thread.allocate_lock()  # Lock for synchronizing access to shared data if needed\n")   
            self.writeline("Devices_main = {")
            self.indent_level+=1
            for dev_name, dev_info in Utils.devices['main_canvas'].items():
                #logging.debug(f"Compiling device: {dev_info['name']} (PIN: {dev_info['PIN']}, Type Index: {dev_info['type_index']})")
                if dev_info['type_index'] == 0:
                    dev_type_str = "Output"
                elif dev_info['type_index'] == 1:
                    dev_type_str = "Input"
                elif dev_info['type_index'] == 2:
                    dev_type_str = "Button"
                elif dev_info['type_index'] == 3:
                    dev_type_str = "PWM"
                text = f"\"{dev_info['name']}\":{{\"name\":\"{dev_info['name']}\", \"PIN\": {dev_info['PIN']}, \"type\":\"{dev_type_str}\", \"state\": None}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}")

            self.writeline("Variables_main = {")
            self.indent_level+=1
            for var_name, var_info in Utils.variables['main_canvas'].items():
                text = f"\"{var_info['name']}\":{{"f"\"value\": {var_info['value']}}},"
                self.writeline(text)
            self.indent_level-=1
            self.writeline("}\n")
            self.writeline("hardware_map = {}  # Map PIN numbers to machine.Pin objects\n")
            
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level+=1
            self.writeline("if dev_config['type'] == 'Output':")
            self.indent_level+=1
            self.writeline(f"hardware_map[dev_config['PIN']] = machine.Pin(dev_config['PIN'], machine.Pin.OUT)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Input':")
            self.indent_level+=1
            self.writeline(f"hardware_map[dev_config['PIN']] = machine.Pin(dev_config['PIN'], machine.Pin.IN)")
            self.indent_level-=1
            self.writeline("elif dev_config['type'] == 'Button':")
            self.indent_level+=1
            self.writeline(f"hardware_map[dev_config['PIN']] = machine.Pin(dev_config['PIN'], machine.Pin.IN, machine.Pin.PULL_DOWN)")
            self.indent_level-=1
            self.writeline("if dev_config['type'] == 'PWM':")
            self.indent_level+=1
            self.writeline("p = machine.Pin(dev_config['PIN'])")
            self.writeline("pwm_obj = machine.PWM(p)")
            self.writeline("pwm_obj.freq(1000)")
            self.writeline("pwm_obj.duty_u16(0)  # Start with 0 duty cycle")
            self.writeline("hardware_map[dev_config['PIN']] = pwm_obj  # Store PWM object in hardware map")
            self.writeline("dev_config['driver'] = pwm_obj  # Link PWM object in config for easy access")
            self.writeline("if 'CurrentDutyCycle' not in dev_config:")
            self.indent_level+=1
            self.writeline("dev_config['CurrentDutyCycle'] = 0")
            self.indent_level-=3

        for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info['type'] == 'Button':
                    self.btn_in_code = True
                if 'LED' in block_info['type']:
                    self.led_in_code = True
        for func_id, func_info in Utils.functions.items():
            for block_id, block_info in func_info['blocks'].items():
                if block_info['type'] == 'Button':
                    self.btn_in_code = True
                if 'LED' in block_info['type']:
                    self.led_in_code = True
        if self.btn_in_code:
            self.create_btn_class()
        if self.led_in_code:
            self.create_led_class()

    def write_reporting_system(self):
        """Injects a background thread to report state via stdout"""
        self.writeline("\n# --- Real-time Reporting Thread ---")
        self.writeline("def data_reporter():")
        self.indent_level += 1
        self.writeline("global last_report, reporter_running, printed_report")
        self.writeline("reporter_running = True")
        self.writeline("time.sleep(1)  # Initial delay to allow main thread to set up")
        self.writeline("while not shutdown:")
        self.indent_level += 1
        self.writeline("try:")
        self.indent_level += 1
        self.writeline("with data_lock:  # Ensure thread-safe access to shared data")
        self.indent_level += 1
            
        # 1. Sanitize Devices_main (remove non-serializable objects like GPIO instances)
        self.writeline("sanitized_devices = {}")
        self.writeline("for k, v in Devices_main.items():")
        self.indent_level += 1
        self.writeline("sanitized_devices[k] = {")
        self.indent_level += 1
        self.writeline("'name': v.get('name', ''),")
        self.writeline("'PIN': v.get('PIN', ''),")
        self.writeline("'type': v.get('type', ''),")
        self.writeline("'state': v.get('state', None) if v.get('type') in ['Input', 'Output', 'Button'] else None,")
        self.writeline("'value': v.get('CurrentDutyCycle', 0) if v.get('type') == 'PWM' else 0")
        self.indent_level -= 1
        self.writeline("}")
        self.indent_level -= 1
        
        # 2. Prepare Report Data
        self.writeline("report = {")
        self.indent_level += 1
        self.writeline("'variables': Variables_main,")
        self.writeline("'devices': sanitized_devices,")
        self.indent_level -= 1
        self.writeline("}")
        self.indent_level -= 1
        # 3. Print with Prefix (flush=True is critical for real-time SSH)
        if self.GPIO_compile:
            self.writeline("current_report_str = json.dumps(report, sort_keys=True)")
        elif self.MC_compile:
            self.writeline("current_report_str = json.dumps(report)")
        self.writeline("if current_report_str != last_report:")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("print('__REPORT__' + current_report_str, flush=True)")
        elif self.MC_compile:
            self.writeline("print('__REPORT__' + current_report_str)")
        self.writeline("last_report = current_report_str")
        self.writeline("printed_report = True")
        while self.indent_level > 2:
            self.indent_level -= 1
        self.writeline("except Exception as e:")
        self.indent_level += 1
        self.writeline("print(f\"Error in reporter thread: {e}\")")
        self.writeline("time.sleep(1)  # Sleep longer on error to avoid spamming")
        self.writeline("if printed_report:")
        self.indent_level += 1
        self.writeline("time.sleep(0.25)")
        self.writeline("printed_report = False  # Reset flag after sleeping")
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        self.writeline("time.sleep(0.1)")
        while self.indent_level > 1:
            self.indent_level -= 1
        self.writeline("reporter_running = False  # Signal reporter thread is stopping")
        while self.indent_level > 0:
            self.indent_level -= 1

        # Start the thread
        self.writeline("# --------------------------------\n")

    def write_cleanup(self):
        self.writeline("\nexcept (KeyboardInterrupt, SystemExit):")
        self.indent_level += 1
        self.writeline("print(\"\\nProgram interrupted by user.\")")
        self.indent_level -= 1
        self.writeline("except Exception as e:")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("print(f\"Unexpected error: {e}\", flush=True)")
        if self.MC_compile:
            self.writeline("print(f\"Unexpected error: {e}\")")
        self.indent_level -= 1
        self.writeline("finally:")
        self.indent_level += 1
        self.writeline("shutdown = True  # Signal any running threads to stop")
        self.writeline("while reporter_running:")  # Wait for reporter thread to finish
        self.indent_level += 1
        self.writeline("time.sleep(0.1)")
        self.indent_level -= 1
        if self.GPIO_compile:
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['type'] == 'PWM':")
            self.indent_level += 1
            self.writeline("dev_config['PWM_instance'].stop()")
            self.indent_level -= 2
            self.writeline("GPIO.cleanup()")
            self.indent_level -= 1
        elif self.MC_compile:
            self.writeline("for pin, obj in hardware_map.items():")
            self.indent_level += 1
            self.writeline("if isinstance(obj, machine.PWM):")
            self.indent_level += 1
            self.writeline("obj.duty_u16(0)  # Stop PWM")
            self.indent_level -= 1
            self.writeline("elif hasattr(obj, 'init'):")
            self.indent_level += 1
            self.writeline("obj.init(machine.Pin.IN)  # Reset pin to input")
            self.indent_level -= 2

    #MARK: Device Classes
    def create_btn_class(self):
        #logging.info("Creating Button class...")
        self.writeline("\nclass Button:")
        self.indent_level += 1
        self.writeline("def __init__(self):")
        self.indent_level += 1
        self.writeline("pass")
        self.indent_level -= 1
        self.writeline("def is_pressed(self, pin):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("if GPIO.input(pin) == GPIO.HIGH:")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Button':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("return True")
            self.indent_level -= 3
            self.writeline("else:")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Button':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("return False")
        if self.MC_compile:
            self.writeline("if pin in hardware_map:")
            self.indent_level += 1
            self.writeline("pin_obj = hardware_map[pin]")
            self.writeline("if pin_obj.value() == 1:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Button':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("return True")
            while self.indent_level > 3:
                self.indent_level -= 1
            self.writeline("else:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Button':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("return False")
        while self.indent_level > 0:
            self.indent_level -= 1
    
    def create_led_class(self):
        #logging.info("Creating LED class...")
        self.writeline("\nclass LED:")
        self.indent_level += 1
        self.writeline("def __init__(self):")
        self.indent_level += 1
        self.writeline("self.pin_state = {}")
        self.writeline("with data_lock:  # Ensure thread-safe access to shared state")
        self.indent_level += 1
        self.writeline("for dev_name, dev_config in Devices_main.items():")
        self.indent_level += 1
        self.writeline("if dev_config['type'] == 'Output':")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("self.pin_state[dev_config['PIN']] = GPIO.LOW")
            self.writeline("dev_config['state'] = \"LOW\"")
        if self.MC_compile:
            self.writeline("if dev_config['PIN'] in hardware_map:")
            self.indent_level += 1
            self.writeline("hardware_map[dev_config['PIN']].value(0)")
            self.indent_level -= 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("self.pin_state[dev_config['PIN']] = 0")
        while self.indent_level > 1:
            self.indent_level -= 1
        #Toggle method
        self.writeline("def Toggle_LED(self, pin):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("if pin in self.pin_state and self.pin_state[pin] == GPIO.HIGH:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("GPIO.output(pin, GPIO.LOW)")
            self.writeline("self.pin_state[pin] = GPIO.LOW")
            while self.indent_level > 2:
                self.indent_level -= 1
            self.writeline("elif pin in self.pin_state and self.pin_state[pin] == GPIO.LOW:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("GPIO.output(pin, GPIO.HIGH)")
            self.writeline("self.pin_state[pin] = GPIO.HIGH")
        if self.MC_compile:
            self.writeline("if pin in self.pin_state and pin in hardware_map:")
            self.indent_level += 1
            self.writeline("pin_obj = hardware_map[pin]")
            self.writeline("if self.pin_state[pin] == 1:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("pin_obj.value(0)")
            self.writeline("self.pin_state[pin] = 0")
            while self.indent_level > 3:
                self.indent_level -= 1
            self.writeline("elif self.pin_state[pin] == 0:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("pin_obj.value(1)")
            self.writeline("self.pin_state[pin] = 1")
        while self.indent_level > 1:
            self.indent_level -= 1
        #Turn ON method
        self.writeline("def LED_OFF(self, pin):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("if pin in self.pin_state and self.pin_state[pin] == GPIO.LOW:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("GPIO.output(pin, GPIO.HIGH)")
            self.writeline("self.pin_state[pin] = GPIO.HIGH")
        if self.MC_compile:
            self.writeline("if pin in self.pin_state and pin in hardware_map and self.pin_state[pin] == 0:")
            self.indent_level += 1
            self.writeline("pin_obj = hardware_map[pin]")
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("pin_obj.value(1)")
            self.writeline("self.pin_state[pin] = 1")
        while self.indent_level > 1:
            self.indent_level -= 1
        #Turn OFF method
        self.writeline("def LED_ON(self, pin):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("if pin in self.pin_state and self.pin_state[pin] == GPIO.HIGH:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("GPIO.output(pin, GPIO.LOW)")
            self.writeline("self.pin_state[pin] = GPIO.LOW")
        if self.MC_compile:
            self.writeline("if pin in self.pin_state and pin in hardware_map and self.pin_state[pin] == 1:")
            self.indent_level += 1
            self.writeline("pin_obj = hardware_map[pin]")
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("pin_obj.value(0)")
            self.writeline("self.pin_state[pin] = 0")
        while self.indent_level > 1:
            self.indent_level -= 1
        #Blink method
        self.writeline("def Blink_LED(self, pin, duration_ms):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("if pin in self.pin_state and self.pin_state[pin] == GPIO.HIGH:")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("self.pin_state[pin] = GPIO.LOW")
            self.writeline("GPIO.output(pin, GPIO.LOW)")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("self.pin_state[pin] = GPIO.HIGH")
            self.writeline("GPIO.output(pin, GPIO.HIGH)")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
            while self.indent_level > 2:
                self.indent_level -= 1
            self.writeline("elif pin in self.pin_state and self.pin_state[pin] == GPIO.LOW:")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("GPIO.output(pin, GPIO.HIGH)")
            self.writeline("self.pin_state[pin] = GPIO.HIGH")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("self.pin_state[pin] = GPIO.LOW")
            self.writeline("GPIO.output(pin, GPIO.LOW)")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
        if self.MC_compile:
            self.writeline("if pin in self.pin_state and pin in hardware_map:")
            self.indent_level += 1
            self.writeline("pin_obj = hardware_map[pin]")
            self.writeline("if self.pin_state[pin] == 1:")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("pin_obj.value(0)")
            self.writeline("self.pin_state[pin] = 0")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("pin_obj.value(1)")
            self.writeline("self.pin_state[pin] = 1")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
            while self.indent_level > 3:
                self.indent_level -= 1
            self.writeline("elif self.pin_state[pin] == 0:")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'Output':")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"HIGH\"")
            self.writeline("pin_obj.value(1)")
            self.writeline("self.pin_state[pin] = 1")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("dev_config['state'] = \"LOW\"")
            self.writeline("pin_obj.value(0)")
            self.writeline("self.pin_state[pin] = 0")
            self.indent_level -= 1
            self.writeline("time.sleep(duration_ms / 1000)")
        while self.indent_level > 1:
            self.indent_level -= 1
        #PWM method
        self.writeline("def PWM_LED(self, pin, PWM_value):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'PWM':")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("pwm_instance = dev_config['PWM_instance']")
            self.writeline("pwm_instance.ChangeDutyCycle(PWM_value)")
            self.writeline("dev_config['CurrentDutyCycle'] = PWM_value")
            self.indent_level -= 1
            self.writeline("time.sleep(0.05)")
        if self.MC_compile:
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin and dev_config['type'] == 'PWM':")
            self.indent_level += 1
            self.writeline("if pin in hardware_map:")
            self.indent_level += 1
            self.writeline("with data_lock:  # Ensure thread-safe updates to shared state")
            self.indent_level += 1
            self.writeline("pwm_instance = hardware_map[pin]")
            self.writeline("if PWM_value < 0: PWM_value = 0")
            self.writeline("if PWM_value > 100: PWM_value = 100")
            self.writeline("pwm_instance.duty_u16(int(PWM_value * 655.35))")  # Scale 0-100 to 0-65500
            self.writeline("dev_config['CurrentDutyCycle'] = PWM_value")
            self.indent_level -= 1
            self.writeline("time.sleep(0.05)")
        while self.indent_level > 1:
            self.indent_level -= 1
        #RGB method
        self.writeline("def RGB_LED(self, pin_r, pin_g, pin_b, r_value, g_value, b_value):")
        self.indent_level += 1
        if self.GPIO_compile:
            self.writeline("with data_lock:  # Ensure thread-safe access to shared state")
            self.indent_level += 1
            self.writeline("for def_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] in [pin_r, pin_g, pin_b] and dev_config['type'] == 'PWM':")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin_r:")
            self.indent_level += 1
            self.writeline("dev_config['PWM_instance'].ChangeDutyCycle(r_value)")
            self.writeline("dev_config['CurrentDutyCycle'] = r_value")
            self.indent_level -= 1
            self.writeline("elif dev_config['PIN'] == pin_g:")
            self.indent_level += 1
            self.writeline("dev_config['PWM_instance'].ChangeDutyCycle(g_value)")
            self.writeline("dev_config['CurrentDutyCycle'] = g_value")
            self.indent_level -= 1
            self.writeline("elif dev_config['PIN'] == pin_b:")
            self.indent_level += 1
            self.writeline("dev_config['PWM_instance'].ChangeDutyCycle(b_value)")
            self.writeline("dev_config['CurrentDutyCycle'] = b_value")
        if self.MC_compile:
            self.writeline("with data_lock:  # Ensure thread-safe access to shared state")
            self.indent_level += 1
            self.writeline("for dev_name, dev_config in Devices_main.items():")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] in [pin_r, pin_g, pin_b] and dev_config['type'] == 'PWM':")
            self.indent_level += 1
            self.writeline("if dev_config['PIN'] == pin_r:")
            self.indent_level += 1
            self.writeline("if pin_r in hardware_map:")
            self.indent_level += 1
            self.writeline("hardware_map[pin_r].duty_u16(int(r_value * 655.35))")
            self.writeline("dev_config['CurrentDutyCycle'] = r_value")
            self.indent_level -= 2
            self.writeline("elif dev_config['PIN'] == pin_g:")
            self.indent_level += 1
            self.writeline("if pin_g in hardware_map:")
            self.indent_level += 1
            self.writeline("hardware_map[pin_g].duty_u16(int(g_value * 655.35))")
            self.writeline("dev_config['CurrentDutyCycle'] = g_value")
            self.indent_level -= 2
            self.writeline("elif dev_config['PIN'] == pin_b:")
            self.indent_level += 1
            self.writeline("if pin_b in hardware_map:")
            self.indent_level += 1
            self.writeline("hardware_map[pin_b].duty_u16(int(b_value * 655.35))")
            self.writeline("dev_config['CurrentDutyCycle'] = b_value")
        while self.indent_level > 0:
            self.indent_level -= 1


    #MARK: Helper Methods

    def create_hashmap(self):
        self.hashmap = {}
        for block_id, block_info in Utils.main_canvas['blocks'].items():
            for conn_id in block_info.get('out_connections', {}).keys():
                self.hashmap[conn_id] = conn_id.split('-')[1]  # Map connection ID to block ID
        for func_name, func_info in Utils.functions.items():
            for block_id, block_info in func_info.get('blocks', {}).items():
                for conn_id in block_info.get('out_connections', {}).keys():
                    self.hashmap[conn_id] = conn_id.split('-')[1]  # Map connection ID to block ID

    def find_block_by_type(self, block_type):
        """Find first block of given type"""
        if self.compiling_what == 'canvas':
            search_infos = Utils.main_canvas['blocks']
        elif self.compiling_what == 'function':
            search_infos = Utils.functions[self.compiling_function]['blocks']
        for block_id, block_info in search_infos.items():
            if block_info['type'] == block_type:
                return block_info
        return None
    
    def get_next_block(self, current_block_id):
        #logging.info(f"Hashmap for connections: {self.hashmap}")
        """Get the block connected to output of current block"""
        #logging.debug(f"Getting next block from {current_block_id}")
        if self.compiling_what == 'canvas':
            #logging.debug(f"Searching in main canvas blocks")
            current_info = Utils.main_canvas['blocks'][current_block_id]
        elif self.compiling_what == 'function':
            #logging.debug(f"Searching in function canvas blocks for function {self.compiling_function}")
            current_info = Utils.functions[self.compiling_function]['blocks'][current_block_id]
        
        # Get first out_connection
        if current_info['out_connections']:
            #logging.debug(f"Current block out_connections: {current_info['out_connections']}")
            for conn_id in current_info['out_connections'].keys():
                #logging.debug(f"Checking connection ID: {conn_id}")
                if conn_id in self.hashmap:
                    next_block_id = self.hashmap[conn_id]
                    #logging.debug(f"Next block ID: {next_block_id}")
                    return next_block_id
        return None 
    
    def get_next_block_from_output(self, current_block_id, output_circle):
        """Get the block connected to specific output circle of current block"""
        if self.compiling_what == 'canvas':
            current_info = Utils.main_canvas['blocks'][current_block_id]
            path_info = Utils.main_canvas['paths']
            #logging.debug(f"Current block info: {current_info}")
        elif self.compiling_what == 'function':
            current_info = Utils.functions[self.compiling_function]['blocks'][current_block_id]
            path_info = Utils.functions[self.compiling_function]['paths']
            #logging.debug(f"Current block info: {current_info}")

        # Find connection from specified output circle

        for conn_id in current_info['out_connections'].keys():
            #logging.debug(f"Utils.paths: {path_info}")
            conn_info = path_info.get(conn_id)
            #logging.debug(f"Checking connection ID: {conn_id} with info: {conn_info}")
            if conn_info and conn_info['from_circle_type'] == output_circle:
                # Find which block this connection goes to 
                #logging.debug(f"Getting next block from output circle '{output_circle}' of block {current_block_id}")
                if self.compiling_what == 'canvas':
                    #logging.info(f"Searching in main canvas blocks")
                    search_infos = Utils.main_canvas['blocks']
                elif self.compiling_what == 'function':
                    #loggin.info(f"Searching in function canvas blocks for function {self.compiling_function}")
                    search_infos = Utils.functions[self.compiling_function]['blocks']
                for block_id, info in search_infos.items():
                    if conn_id in info['in_connections']:
                        #logging.info(f"Next block is {block_id}")
                        return block_id
        return None
    
    def resolve_value(self, value_str, value_type):
        """Convert value to actual value - handle variable or literal"""
        if value_type in ('switch', 'N/A'):
            #logging.debug(f"Resolving value: {value_str}")
            return value_str  # Return as is for switch
        
        if self.is_variable_reference(value_str):
            #logging.debug(f"Resolving variable reference: {value_str}")
            # Look up variable's current runtime value
            if value_type == 'Device':
                #moggin.info(f"Looking up device: {value_str}")
                #logging.debug(f"Utils.devices: {Utils.devices}")
                if self.compiling_what == 'canvas':
                    #logging.info(f"Searching in main canvas devices")
                    search_devices = Utils.devices['main_canvas']
                elif self.compiling_what == 'function':
                    #logging.info(f"Searching in function canvas devices for function {self.compiling_function}")
                    search_devices = Utils.devices['function_canvases'][self.compiling_function]
                #logging.debug(f"Devices to search: {search_devices}")
                if self.compiling_what == 'canvas':
                    for dev_id, dev_info in search_devices.items():
                        #logging.debug(dev_info)
                        if dev_info['name'] == value_str:
                            #logging.debug(f"Found device {value_str} with PIN {dev_info['PIN']}")
                            return f"Devices_main['{value_str}']['PIN']"
                elif self.compiling_what == 'function':
                    return f"{value_str}"
            elif value_type == 'Variable':
                #logging.info(f"Looking up variable: {value_str}")
                #logging.debug(f"Utils.variables: {Utils.variables}")
                if self.compiling_what == 'canvas':
                    #logging.info(f"Searching in main canvas variables")
                    search_variables = Utils.variables['main_canvas']
                elif self.compiling_what == 'function':
                    #logging.debug(f"Searching in function canvas variables for function {self.compiling_function}")
                    search_variables = Utils.variables['function_canvases'][self.compiling_function]
                #logging.debug(f"Variables to search: {search_variables}")
                if self.compiling_what == 'canvas':
                    for var_id, var_info in search_variables.items():
                        #logging.debug(var_info)
                        if var_info['name'] == value_str:
                            #logging.debug(f"Found variable {value_str} with value {var_info['value']}")
                            return f"Variables_main['{value_str}']['value']"
                elif self.compiling_what == 'function':
                    return f"{value_str}"
                
        else:
            #logging.info(f"Using literal value: {value_str}")
            pass
        return value_str  # It's a literal
    
    def is_variable_reference(self, value_str):
        """Check if value is a variable name (not a number)"""
        try:
            float(value_str)  # Can convert to number?
            #logging.debug(f"{value_str} is a literal number.")
            return False      # It's a literal number
        except ValueError:
            logging.error(f"{value_str} is a variable reference.")
            return True 
        
    def writeline(self, text):
        """Write indented line"""
        indent = self.indent_str * self.indent_level
        self.current_lines.append(indent + text + "\n")
        
    def write_condition(self, type,  value1, operator, value2):
        """Write condition code - DRY principle"""
        text = f"{type} {value1} {operator} {value2}:"
        #logging.info(f"Writing condition: {text}")
        self.writeline(text)
    
    def get_comparison_operator(self, combo_value):
        #logging.info(f"Mapping combo value '{combo_value}' to operator")
        """Map combo box value to Python operator"""
        operators = {
            "==": "==",
            "!=": "!=",
            "<": "<",
            "<=": "<=",
            ">": ">",
            ">=": ">="
        }
        #logging.info(f"Mapped to operator: {operators.get(combo_value, '==')}")
        return operators.get(combo_value, "==")
    
    def get_math_operator(self, operator):
        """Map math block type to Python operator"""
        operators = {
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%",
            "√": "** 0.5",
            "^": "**"

        }
        return operators.get(operator, "+")

    #MARK: Block Handlers
    def handle_if_block(self, block):
        #logging.info(f"Handling If block {block}")
        first_values = []
        second_values = []
        operators = []
        outputs = []
        for i in range(block['conditions']):
            first_values.append(self.resolve_value(block['first_vars'][f'value_{i+1}_1_name'], block['first_vars'][f'value_{i+1}_1_type'] if f'value_{i+1}_1_type' in block['first_vars'] else 'Variable'))
            second_values.append(self.resolve_value(block['second_vars'][f'value_{i+1}_2_name'], block['second_vars'][f'value_{i+1}_2_type'] if f'value_{i+1}_2_type' in block['second_vars'] else 'Variable'))
            operators.append(self.get_comparison_operator(block['operators'][f'operator_{i+1}']))
            outputs.append(self.get_next_block_from_output(block['id'], f'out_{i+1}'))  # True path for this condition



        self.write_condition("if", first_values[0], operators[0], second_values[0])
        self.indent_level += 1
        self.process_block(outputs[0])
        #logging.info(f"Completed If true branch, now handling else branch")
        self.indent_level -= 1
        for i in range(1, block['conditions']):
            self.write_condition("elif", first_values[i], operators[i], second_values[i])
            self.indent_level += 1
            self.process_block(outputs[i])
            #logging.info(f"Completed Elif branch {i}, now checking next condition or else")
            self.indent_level -= 1
        if len(outputs) > block['conditions']:
            self.writeline("else:")
            #logging.info(f"Processing else branch for If block")
            self.indent_level += 1
            self.process_block(outputs[-1])
            self.indent_level -= 1
    
    def handle_while_block(self, block):
        if block['type'] == 'While_true':
            #logging.info(f"Handling While true block {block}")
            next_id = self.get_next_block(block['id'])
            self.writeline("while True:")
            self.indent_level += 1
            #logging.info(f"Processing While true branch for While true block")
            self.process_block(next_id)
            self.indent_level -= 1
            return
        
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'] if block['value_1_type'] in block else 'Variable')
        value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'] if block['value_2_type'] in block else 'Variable')
        #logging.debug(f"Resolved While block values: {value_1}, {value_2}")
        operator = self.get_comparison_operator(block['operator'])
        #logging.debug(f"Using operator: {operator}")
        out1_id = self.get_next_block_from_output(block['id'], 'out_1')  # True path
        out2_id = self.get_next_block_from_output(block['id'], 'out_2')  # False path
        #logging.debug(f"While block outputs: out1 -> {out1_id}, out2 -> {out2_id}")
        self.write_condition("while", value_1, operator, value_2)
        self.indent_level += 1
        #logging.info(f"Processing While true branch for While block")
        self.process_block(out1_id)
        self.indent_level -= 1
        #logging.info(f"Processing While false branch for While block")
        self.process_block(out2_id)
           
    def handle_timer_block(self, block):
        self.writeline(f"time.sleep({block['sleep_time']}/1000)")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after Timer: {next_id}")
            pass
        self.process_block(next_id)
    
    def handle_switch_block(self, block):
        switch_state = block['switch_state']
    
    #Check if it's already a boolean
        if isinstance(switch_state, bool):
            switch_state = switch_state 
        else:
            # Only resolve if it's a string (variable reference or literal)
            switch_state = self.resolve_value(switch_state, 'switch')
        
        Var_1 = self.resolve_value(block['value_1_name'], 'Device')
        
        #logging.info(f"Resolved Switch block value: {switch_state} (type: {type(switch_state).__name__})")
        if self.GPIO_compile:
            if switch_state is True:
                #logging.info(f"Writing GPIO HIGH for Switch block")
                self.writeline(f"GPIO.output({Var_1}, GPIO.HIGH)")
            elif switch_state is False:
                #logging.info(f"Writing GPIO LOW for Switch block")
                self.writeline(f"GPIO.output({Var_1}, GPIO.LOW)")
            else:
                #logging.warninig(f"Unknown Switch value {switch_state}, defaulting to LOW")
                self.writeline(f"GPIO.output({Var_1}, GPIO.LOW)")
        elif self.MC_compile:
            if switch_state is True:
                #logging.info(f"Writing PIN HIGH for Switch block")
                self.writeline(f"{Var_1}.value(1)")
            elif switch_state is False:
                #logging.info(f"Writing PIN LOW for Switch block")
                self.writeline(f"{Var_1}.value(0)")
            else:
                #logging.warninig(f"Unknown Switch value {switch_state}, defaulting to LOW")
                self.writeline(f"{Var_1}.value(0)")
        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after Switch: {next_id}")
            pass
        self.process_block(next_id)
    
    def handle_button_block(self, block):
        DEV_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        out1_id = self.get_next_block_from_output(block['id'], 'out_1')  # ON path
        out2_id = self.get_next_block_from_output(block['id'], 'out_2')
        #logging.debug(f"Resolved Button block device: {DEV_1}")
        if self.GPIO_compile:
            self.writeline(f"if Button().is_pressed({DEV_1}):")
            self.indent_level += 1
            #logging.debug(f"Processing Button ON branch for Button block")
            self.process_block(out1_id)
            self.indent_level -= 1
            self.writeline("else:")
            #logging.debug(f"Processing Button OFF branch for Button block")
            self.indent_level += 1
            self.process_block(out2_id)
            self.indent_level -= 1
        elif self.MC_compile:
            self.writeline(f"if Button().is_pressed({DEV_1}):")
            self.indent_level += 1
            #logging.debug(f"Processing Button ON branch for Button block")
            self.process_block(out1_id)
            self.indent_level -= 1
            self.writeline("else:")
            #logging.debug(f"Processing Button OFF branch for Button block")
            self.indent_level += 1
            self.process_block(out2_id)
            self.indent_level -= 1
            
    def handle_function_block(self, block):

        self.last_block = block
        func_name = block['name']

        for f_id, f_info in self.func_to_compile.items():
            if f_info[0] == func_name:
                if f_info[1] == "Not Compiled":
                    self.func_to_compile[f_id] = (f_info[0], "Compiled", "")
                    self.memory_indent_level = self.indent_level
                    self.indent_level = 0  # Reset indent for function definition
                    self.current_lines = self.function_lines
                    self.writeline("")  # Blank line before function
                    self.writeline(f"def {func_name}(")
                    self.indent_level += 1
                    #logging.debug(f"ref_vars: {block['internal_vars']['ref_vars']}")
                    #logging.debug(f"ref_devs: {block['internal_devs']['ref_devs']}")
                    for l_widget, v_info in block['internal_vars']['ref_vars'].items():
                        #logging.debug(f"Function variable parameter: {v_info['name']}")
                        self.writeline(f"{v_info['name']},")
                    for l_widget, d_info in block['internal_devs']['ref_devs'].items():
                        #logging.debug(f"Function device parameter: {d_info['name']}")
                        self.writeline(f"{d_info['name']},")
                    self.indent_level -= 1
                    self.writeline("):")
                    self.indent_level += 1
                    self.compiling_what = 'function'
                    for fu_id, fu_info in Utils.functions.items():
                        #logging.debug(f"{f_id}: {f_info}")
                        if fu_info['name'] == func_name:
                            self.compiling_function = fu_info['id']
                            break
                    start_block = self.find_block_by_type('Start')
                    if start_block:
                        next_id = self.get_next_block(start_block['id'])
                        self.process_block(next_id)

                #logging.debug("Function block return var name: %s, compiling what: %s", block.get('return_var_name'), self.compiling_what)
                target_var = self.resolve_value(block['return_var_name'], 'Variable') if 'return_var_name' in block else None
                #logging.debug("Resolved target variable for function return: %s", target_var)
                if target_var:
                    self.writeline(f"{target_var} = {func_name}(")
                else:
                    self.writeline(f"{func_name}(")
                #logging.debug(f"block internal vars: {block['internal_vars']}")
                #logging.debug(f"block internal devs: {block['internal_devs']}")
                self.indent_level += 1
                for l_widget, v_info in block['internal_vars']['main_vars'].items():
                    #logging.debug(f"Function argument: {v_info['name']}")
                    resolved_value = self.resolve_value(v_info['name'], v_info['type'])
                    #logging.info(f"Resolved argument value: {resolved_value}")
                    self.writeline(f"{resolved_value},")
                for l_widget, d_info in block['internal_devs']['main_devs'].items():
                    #logging.debug(f"Function device argument: {d_info['name']}")
                    resolved_value = self.resolve_value(d_info['name'], d_info['type'])
                    #logging.info(f"Resolved device argument value: {resolved_value}")
                    self.writeline(f"{resolved_value},")
                self.indent_level -= 1
                self.writeline(")")
                
                next_id = self.get_next_block(block['id'])
                if next_id:
                    #logging.info(f"Processing next block after Function call: {next_id}")
                    pass

                self.process_block(next_id)
        
    def handle_return_block(self, block):
        return_value = self.resolve_value(block['value_1_name'], block['value_1_type'])
        self.writeline(f"return {return_value}")
        if self.compiling_what == 'function':
            self.func_to_compile[self.compiling_function] = (self.func_to_compile[self.compiling_function][0], "Compiled", return_value)
        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after Return: {next_id}")
            pass
        self.process_block(next_id)

    def handle_math_block(self, block):
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        if block['type'] not in ('Plus_one', 'Minus_one'):
            value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
            operators = {
                'Add': '+',
                'Subtract': '-',
                'Multiply': '*',
                'Divide': '/',
                'Modulo': '%',
                'Root': '** 0.5',
                'Power': '**'
            }
            result_var = self.resolve_value(block['result_var_name'], block['result_var_type'])
        #logging.info(f"Resolved Math block values: {value_1}, {value_2}, result var: {result_var}")
        if block['type'] not in ('Plus_one', 'Minus_one'):
            self.writeline(f"{result_var} = {value_1} {operators[block['operator']]} {value_2}")
        elif block['type'] == 'Plus_one':
            self.writeline(f"{value_1} = {value_1} + 1")
        elif block['type'] == 'Minus_one':
            self.writeline(f"{value_1} = {value_1} - 1")
        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after Math: {next_id}")
            pass
        self.process_block(next_id)
    
    def handle_rand_block(self, block):
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
        result_var = self.resolve_value(block['result_var_name'], block['result_var_type'])

        self.writeline(f"{result_var} = random.randint({value_1}, {value_2})")
        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after Random: {next_id}")
            pass
        self.process_block(next_id)

    def handle_logic_block(self, block):
        value_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        value_2 = self.resolve_value(block['value_2_name'], block['value_2_type'])
        operators = {
            'Lower': '<',
            'Lower_equal': '<=',
            'Greater': '>',
            'Greater_equal': '>=',
            'Equal': '==',
            'Not_equal': '!=',
        }
        out_1_id = self.get_next_block_from_output(block['id'], 'out_1')  # True path
        out_2_id = self.get_next_block_from_output(block['id'], 'out_2')  # False path

        self.writeline(f"if {value_1} {operators[block['operator']]} {value_2}:")
        self.indent_level += 1
        self.process_block(out_1_id)
        self.indent_level -= 1
        self.writeline("else:")
        self.indent_level += 1
        self.process_block(out_2_id)
        self.indent_level -= 1

        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after Logic: {next_id}")
            pass
        self.process_block(next_id)

    def handle_LED_block(self, block):
        if block['type'] in ('Blink_LED', 'Toggle_LED', 'PWM_LED', 'LED_ON', 'LED_OFF'):
            DEV_1 = self.resolve_value(block['value_1_name'], block['value_1_type'])
        if block['type'] == 'Blink_LED':
            duration = block['sleep_time']
            self.writeline(f"led.Blink_LED({DEV_1}, {duration})")
        elif block['type'] == 'Toggle_LED':
            self.writeline(f"led.Toggle_LED({DEV_1})")
        elif block['type'] == 'PWM_LED':
            pwm_value = self.resolve_value(block['PWM_value'], 'Variable')
            self.writeline(f"led.PWM_LED({DEV_1}, {pwm_value})")
        elif block['type'] == 'RGB_LED':
            Pins = []
            PWM_values = []
            for i in range(1, 4):
                DEV_i = self.resolve_value(block['first_vars'][f'value_{i}_1_name'], block['first_vars'][f'value_{i}_1_type'] if f'value_{i}_1_type' in block['first_vars'] else 'Device')
                PWM_value = self.resolve_value(block['second_vars'][f'value_{i}_2_PWM'], block['second_vars'][f'value_{i}_2_type'] if f'value_{i}_2_type' in block['second_vars'] else 'Variable')
                Pins.append(DEV_i)
                PWM_values.append(PWM_value)
            self.writeline(f"led.RGB_LED({Pins[0]}, {Pins[1]}, {Pins[2]}, {PWM_values[0]}, {PWM_values[1]}, {PWM_values[2]})")
        elif block['type'] == 'LED_ON':
            self.writeline(f"led.LED_ON({DEV_1})")
        elif block['type'] == 'LED_OFF':
            self.writeline(f"led.LED_OFF({DEV_1})")
        
        next_id = self.get_next_block(block['id'])
        if next_id:
            #logging.info(f"Processing next block after LED: {next_id}")
            pass
        self.process_block(next_id)

    def handle_networks_block(self, block):
        outputs = []
        for i in range(1, block['networks']+1):
            outputs.append(self.get_next_block_from_output(block['id'], f'out_{i}'))
        #logging.info("Handling Networks block %s with outputs: %s (count=%s)", block['id'], outputs, len(outputs))
        for i in range(block['networks']):
            #logging.debug("Processing network block output %s with next block ID: %s", i, outputs[i])
            self.process_block(outputs[i])

    def handle_end_block(self, block):
        #logging.info(f"Handling End block {block['id']}")
        if self.compiling_what == 'function':
            #logging.info(f"Ending function compilation for {self.compiling_function}")
            self.compiling_what = 'canvas'
            self.compiling_function = None
            self.writeline("")  # Blank line after function
            self.current_lines = self.main_lines
            self.indent_level = self.memory_indent_level+1
            #logging.info(f"Resuming canvas compilation at indent level {self.indent_level}")
            #logging.info(f"Last block was function call: {self.last_block}")
            next_id = self.get_next_block(self.last_block['id'])
            self.process_block(next_id)
        else:
            #logging.info("End block reached in canvas - no action needed")
            pass
        return
    