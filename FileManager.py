"""
FileManager.py - Complete Save/Load System for Visual Programming Projects

Handles serialization and deserialization of projects with proper separation
of persistent data (JSON-safe) and runtime references (QWidget objects).
"""
from Imports import (json, os, datetime, Path, get_Utils, ProjectData)

Utils = get_Utils()
        
class FileManager:
    """Manages project file operations with auto-save capabilities"""
    
    # Directory structure
    PROJECTS_DIR = Utils.get_base_path() / "projects"
    AUTOSAVE_DIR = Utils.get_base_path() / "autosave"
    COMPARE_DIR = Utils.get_base_path() / "compare"
    APPDATA_DIR = os.path.expanduser("~\\AppData\\Local\\Visual Programming\\projects")
    PROJECT_EXTENSION = ".project"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.PROJECTS_DIR, exist_ok=True)
        os.makedirs(cls.AUTOSAVE_DIR, exist_ok=True)
        os.makedirs(cls.COMPARE_DIR, exist_ok=True)
        os.makedirs(cls.APPDATA_DIR, exist_ok=True)
    
    # ========================================================================
    # SAVE OPERATIONS
    # ========================================================================
    #MARK: - Save Operations
    @classmethod
    def save_project(cls, project_name: str, is_autosave: bool = False, is_compare=False) -> bool:
        """
        Save current project to file
        
        Args:
            project_name: Name of project (without extension)
            is_autosave: If True, save to autosave folder, else projects folder
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            cls.ensure_directories()
            
            # Determine save location
            if is_autosave:
                filename = os.path.join(cls.AUTOSAVE_DIR, project_name + cls.PROJECT_EXTENSION)
            elif is_compare:
                filename = os.path.join(cls.COMPARE_DIR, project_name + "_TEMP" + cls.PROJECT_EXTENSION)
            else:
                filename = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
                filename2 = os.path.join(cls.APPDATA_DIR, f"{project_name}" + cls.PROJECT_EXTENSION)
            
            # Build project data
            project_dict = cls._build_save_data(project_name)
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(project_dict, f, indent=2, ensure_ascii=False)
            if not is_autosave and not is_compare:
                with open(filename2, 'w', encoding='utf-8') as f:
                    json.dump(project_dict, f, indent=2, ensure_ascii=False)

            print(f"✓ Project saved: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving project: {e}")
            return False
    
    @classmethod
    def _build_save_data(cls, project_name: str, for_dict=True) -> dict:

        """
        Build complete project data for serialization
        
        Converts all runtime data to pure JSON-safe format
        """
        # Build blocks data (WITHOUT widget references)
        main_canvas = {
            'blocks': {},
            'paths': {}
        }
        functions = {}
        for canvas in Utils.canvas_instances:
            #print(f"Processing canvas: {canvas}")
            if canvas.reference == 'canvas':
                #print("Processing main canvas blocks")
                for block_id, block_info in Utils.main_canvas['blocks'].items():
                    info = Utils.data_control.save_data(block_id, block_info)

                    if info:
                        main_canvas['blocks'][block_id] = info
            elif canvas.reference == 'function':
                #print("Processing function canvas blocks")
                for f_id, f_info in Utils.functions.items():
                    if canvas == f_info.get('canvas'):
                        functions[f_id] = {'blocks': {},
                                           'paths': {}}
                        for block_id, block_info in f_info['blocks'].items():
                            #print(f"Processing block {block_id} in function {f_id}, type {block_info['type']}, name: {block_info.get('name', 'N/A')}")
                            if f_id not in functions:
                                #print(f"Creating new function entry for {f_id}")
                                functions[f_id] = {'blocks': {}}
                            
                            info = Utils.data_control.save_data(block_id, block_info)
                            
                            if info:
                                functions[f_id]['blocks'][block_id] = info
        # Build connections data (using block IDs, NOT widget references)
        for canvas in Utils.canvas_instances:
            #print(f"Processing connections for canvas: {canvas}")
            if canvas.reference == 'canvas':
                #print("Processing main canvas connections")
                for conn_id, conn_info in Utils.main_canvas['paths'].items():
                    #print(f"Processing connection {conn_id} on main canvas")
                    if conn_info.get('canvas') == canvas:
                        main_canvas['paths'][conn_id] = {
                            'from': conn_info['from'],
                            'from_circle_type': conn_info.get('from_circle_type', 'out'),
                            'to': conn_info['to'],
                            'to_circle_type': conn_info.get('to_circle_type', 'in'),
                            'waypoints': conn_info.get('waypoints', []),
                        }
            elif canvas.reference == 'function':
                #print("Processing function canvas connections")
                for f_id, f_info in Utils.functions.items():
                    if canvas == f_info.get('canvas'):
                        #print(f"Processing connections for function {f_id}")
                        #print(f" Function connections: {Utils.functions[f_id]['paths']}")
                        if f_id not in functions:
                            #print(f"Creating new function entry for connections for {f_id}")
                            functions[f_id] = {'blocks': {}, 'paths': {}}
                        for conn_id, conn_info in Utils.functions[f_id]['paths'].items():
                            #print(f"Conn_info: {conn_info}")
                            if conn_info.get('canvas') == canvas:
                                #print(f"Processing connection {conn_id} in function {f_id}")
                                functions[f_id]['paths'][conn_id] = {
                                    'from': conn_info['from'],
                                    'from_circle_type': conn_info.get('from_circle_type', 'out'),
                                    'to': conn_info['to'],
                                    'to_circle_type': conn_info.get('to_circle_type', 'in'),
                                    'waypoints': conn_info.get('waypoints', []),
                                }
        #print(f"Saved main canvas paths : {main_canvas['paths']}")
        #for function_id, function_info in functions.items():
            #print(f"Saved function {function_id} paths : {function_info['paths']}")       
        # Build variables data (pure data, no widget references)
        variables_data = {
            'main_canvas': {},      
            'function_canvases': {} 
        }
        for canvas in Utils.canvas_instances:
            #print(f"Processing variables for canvas: {canvas}")
            if canvas.reference == 'canvas':
                #print("Processing main canvas variables")
                for var_id, var_info in Utils.variables['main_canvas'].items():
                    #print(f" Processing variable {var_id} for main canvas")
                    #print(f"  Var info: {var_info}")
                    variables_data['main_canvas'][var_id] = {
                        'name': var_info.get('name', ''),
                        'type': var_info.get('type', ''),
                        'value': var_info.get('value', ''),
                    }
            elif canvas.reference == 'function':
                #print("Processing function canvas variables")
                for f_id, f_info in Utils.functions.items():
                    if canvas == f_info.get('canvas'):
                        variables_data['function_canvases'][f_id] = {}
                        #print(f" Processing variables for function {f_id}")
                        for var_id, var_info in Utils.variables['function_canvases'][f_id].items():
                            variables_data['function_canvases'][f_id][var_id] = {
                                'name': var_info.get('name', ''),
                                'type': var_info.get('type', ''),
                                'value': var_info.get('value', ''),
                            }
        
        # Build devices data (pure data, no widget references)
        devices_data = {
            'main_canvas': {},      
            'function_canvases': {} 
        }
        for canvas in Utils.canvas_instances:
            #print(f"Processing devices for canvas: {canvas}")
            if canvas.reference == 'canvas':
                #print("Processing main canvas devices")
                for dev_id, dev_info in Utils.devices['main_canvas'].items():
                    #print(f" Processing device {dev_id} for main canvas")
                    #print(f"  Device info: {dev_info}")
                    devices_data['main_canvas'][dev_id] = {
                        'name': dev_info.get('name', ''),
                        'type': dev_info.get('type', ''),
                        'type_index': dev_info.get('type_index', 0),
                        'PIN': dev_info.get('PIN', ''),
                    }
            elif canvas.reference == 'function':
                #print("Processing function canvas devices")
                for f_id, f_info in Utils.functions.items():
                    if canvas == f_info.get('canvas'):
                        devices_data['function_canvases'][f_id] = {}
                        #print(f" Processing devices for function {f_id}")
                        for dev_id, dev_info in Utils.devices['function_canvases'][f_id].items():
                            devices_data['function_canvases'][f_id][dev_id] = {
                                'name': dev_info.get('name', ''),
                                'type': dev_info.get('type', ''),
                                'type_index': dev_info.get('type_index', 0),
                                'PIN': dev_info.get('PIN', ''),
                            }
        metadata = {
            'version': '1.0',
            'name': project_name,
            'created': Utils.project_data.metadata.get('created', 
                      datetime.now().isoformat()),
            'modified': datetime.now().isoformat(),
        }
        
        canvases = {}
        for canvas, canvas_info in Utils.canvas_instances.items():
            canvases[str(canvas)] = {
                'canvas': str(canvas),
                'ref': canvas_info.get('ref', 'canvas'),
                'id': canvas_info.get('id', ''),
                'index': canvas_info.get('index', 0),
                'name': canvas_info.get('name', ''),
            }
        
        settings = {
            'rpi_model': Utils.app_settings.rpi_model,
            'rpi_model_index': Utils.app_settings.rpi_model_index,
        }
        
        # Complete project structure
        if for_dict:
            project_dict = {
                'metadata': metadata,
                'settings': settings,
                'main_canvas': main_canvas,
                'canvases': canvases,
                'functions': functions,
                'variables': variables_data,
                'devices': devices_data,
            }
        
            return project_dict
        else:
            Utils.project_data.main_canvas = main_canvas
            Utils.project_data.functions = functions
            Utils.project_data.canvases = canvases
            Utils.project_data.variables = variables_data
            Utils.project_data.devices = devices_data
            Utils.project_data.settings = settings
            Utils.project_data.metadata = metadata
            return
    
    
    # ========================================================================
    # LOAD OPERATIONS
    # ========================================================================
    #MARK: - Load Operations
    @classmethod
    def load_app_settings(cls) -> bool:
        """
        Load application settings from file and populate Utils.app_settings
        
        Args:
            settings_filename: Path to app settings JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filename = os.path.join(Utils.get_base_path(), "app_settings.json")
            print(f"Loading app settings from: {filename}")
            with open(filename, 'r') as f:
                print("App settings file opened successfully.")
                settings_dict = json.load(f)
            
            print(f"App settings JSON loaded: {settings_dict}")
            cls._populate_app_settings_from_save(settings_dict)
            #print(f"✓ App settings loaded: {settings_filename}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON file: {e}")
            return False
        except Exception as e:
            print(f"✗ Error loading app settings: {e}")
            return False

    @classmethod
    def load_project(cls, project_name: str, is_autosave: bool = False) -> bool:
        """
        Load project from file and populate Utils
        
        Args:
            project_name: Name of project (without extension)
            is_autosave: If True, load from autosave folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cls.ensure_directories()
            
            # Determine load location
            if is_autosave:
                filename = os.path.join(cls.AUTOSAVE_DIR, project_name + cls.PROJECT_EXTENSION)
                app_settings_filename = os.path.join(Utils.get_base_path(), "app_settings.json")
            else:
                filename = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
                app_settings_filename = os.path.join(Utils.get_base_path(), "app_settings.json")

            appdata_filename = os.path.join(cls.APPDATA_DIR, project_name + cls.PROJECT_EXTENSION)
            appdata_app_settings_filename = os.path.join(cls.APPDATA_DIR, "app_settings.json")

            if not os.path.exists(filename):
                if os.path.exists(appdata_filename):
                    print(f"⚠️  Project not found in main folder, loading from AppData backup...")
                    filename = appdata_filename
                else:
                    print(f"✗ Project file not found: {filename}")
                    return False
            
            if not os.path.exists(app_settings_filename):
                if os.path.exists(appdata_app_settings_filename):
                    print(f"⚠️  App settings not found in main folder, loading from AppData backup...")
                    app_settings_filename = appdata_app_settings_filename
                else:
                    print(f"✗ App settings file not found: {app_settings_filename}")
                    return False

            # Load JSON
            with open(filename, 'r', encoding='utf-8') as f:
                project_dict = json.load(f)
            
            with open(app_settings_filename, 'r', encoding='utf-8') as f:
                app_settings_dict = json.load(f)

            # Populate Utils with loaded data (PURE DATA ONLY)
            cls._populate_utils_from_save(project_dict)
            cls._populate_app_settings_from_save(app_settings_dict)
            
            #print(f"✓ Project loaded: {filename}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON file: {e}")
            return False
        except Exception as e:
            print(f"✗ Error loading project: {e}")
            return False
    
    @classmethod
    def _populate_utils_from_save(cls, project_dict: dict):
        """
        Populate Utils with loaded data
        
        Does NOT create widgets - only populates persistent data.
        Widgets are created by GUI_pyqt.rebuild_from_data()
        """
        
        # Clear existing data
        Utils.project_data = ProjectData()
        
        # Load metadata
        Utils.project_data.metadata = project_dict.get('metadata', {})
        
        # Load RPI settings
        Utils.project_data.settings = project_dict.get('settings', {})
        
        # Load blocks (pure data only)
        Utils.project_data.main_canvas = project_dict.get('main_canvas', {})
        
        Utils.project_data.functions = project_dict.get('functions', {})
        
        # Load connections (pure data only)
        Utils.project_data.canvases = project_dict.get('canvases', {})
        
        # Load variables
        Utils.project_data.variables = project_dict.get('variables', {})
        
        # Load devices
        Utils.project_data.devices = project_dict.get('devices', {})
        
        #print(f"✓ Data loaded: {len(Utils.project_data.main_canvas)} blocks, "
        #      f"{len(Utils.project_data.functions)} functions, "
        #      f"{len(Utils.project_data.canvases)} connections, "
        #      f"{len(Utils.project_data.variables)} variables, "
        #      f"{len(Utils.project_data.devices)} devices, "
        #      f"Settings: {len(Utils.project_data.settings)}"
        #      f"Metadata: {len(Utils.project_data.metadata)}"
        #      )
    
    @classmethod
    def _populate_app_settings_from_save(cls, settings_dict: dict):
        """Populate Utils.app_settings from loaded settings dict"""
        Utils.app_settings.rpi_model = settings_dict.get('rpi_model', 'Raspberry Pi 4 Model B')
        Utils.app_settings.rpi_model_index = settings_dict.get('rpi_model_index', 0)
        Utils.app_settings.rpi_host = settings_dict.get('rpi_host', 'raspberrypi.local')
        Utils.app_settings.rpi_user = settings_dict.get('rpi_user', 'pi')
        Utils.app_settings.rpi_password = settings_dict.get('rpi_password', 'rasppberry')    
        Utils.app_settings.language = settings_dict.get('language', 'en')
        Utils.app_settings.theme = settings_dict.get('theme', 'dark')
        Utils.app_settings.ui_scale = settings_dict.get('ui_scale', 'medium')

    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================
    #MARK: - Utility Operations
    @classmethod
    def list_projects(cls) -> list:
        """List all saved projects"""
        cls.ensure_directories()
        projects = []
        
        for filename in os.listdir(cls.PROJECTS_DIR):
            if filename.endswith(cls.PROJECT_EXTENSION):
                project_name = filename[:-len(cls.PROJECT_EXTENSION)]
                filepath = os.path.join(cls.PROJECTS_DIR, filename)
                modified = os.path.getmtime(filepath)
                projects.append({
                    'name': project_name,
                    'path': filepath,
                    'modified': datetime.fromtimestamp(modified),
                })
        
        return sorted(projects, key=lambda x: x['modified'], reverse=True)
    
    @classmethod
    def delete_project(cls, project_name: str) -> bool:
        """Delete a saved project"""
        try:
            filepath = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
            if os.path.exists(filepath):
                os.remove(filepath)
                #print(f"✓ Project deleted: {project_name}")
                return True
            else:
                print(f"✗ Project not found: {project_name}")
                return False
        except Exception as e:
            print(f"✗ Error deleting project: {e}")
            return False
    
    @classmethod
    def project_exists(cls, project_name: str) -> bool:
        """Check if a project file exists"""
        filepath = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
        return os.path.exists(filepath)
    
    # ========================================================================
    # NEW PROJECT
    # ========================================================================
    #MARK: - New Project
    @classmethod
    def new_project(cls):
        """Initialize a new empty project"""
        # Clear all data
        Utils.main_canvas.clear()
        Utils.canvas_instances.clear()
        Utils.functions.clear()
        Utils.paths.clear()
        Utils.variables.clear()
        Utils.devices.clear()
        Utils.var_items.clear()
        Utils.dev_items.clear()
        Utils.vars_same.clear()
        Utils.devs_same.clear()
        
        # Reset project data
        Utils.project_data = ProjectData()
        Utils.project_data.metadata = {
            'version': '1.0',
            'name': 'Untitled',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
        }
        
        #print("✓ New project created")
    #MARK: - compare project
    @classmethod
    def compare_projects(cls, name: str) -> bool:
        """
        Compare the currently loaded project (Utils.projectdata) against 
        the last saved version on disk. Handles:
        - Main canvas blocks & connections
        - All function canvases blocks & connections
        - All variables (main + functions)
        - All devices (main + functions)
        - Settings
        
        Args:
            name: Project name to compare against
            
        Returns:
            True if changes are detected, False otherwise
        """
        print(f"Comparing current project against saved project: {name}")
        try:
            has_changes = False
            # Load the saved project data
            compare_dict = cls._load_project_dict(name)
            if not compare_dict:
                print(" No saved project data found for comparison.")
                return True
            
            saved_data = ProjectData.from_dict(compare_dict)
            cls._build_save_data(name, for_dict=False)
            current_data = Utils.project_data
            print(f"current_data: {current_data}\nsaved_data: {saved_data}")
            # =====================================================
            # 1. COMPARE MAIN CANVAS BLOCKS & CONNECTIONS
            # =====================================================
            if cls._compare_main_canvas_blocks(saved_data, current_data) and has_changes == False:
                print(" Main canvas blocks have changes.")
                has_changes = True
            
            # =====================================================
            # 1b. COMPARE MAIN CANVAS CONNECTIONS (separately to blocks)
            # =====================================================
            elif cls._compare_main_canvas_connections(saved_data, current_data) and has_changes == False:
                print(" Main canvas connections have changes.")
                has_changes = True
            # =====================================================
            # 2. COMPARE FUNCTION CANVASES (blocks + connections)
            # =====================================================
            elif cls._compare_function_canvases(saved_data, current_data) and has_changes == False:
                print(" Function canvases have changes.")
                has_changes = True
            
            # =====================================================
            # 3. COMPARE VARIABLES (main + all functions)
            # =====================================================
            elif cls._compare_variables_all(saved_data, current_data) and has_changes == False:
                print(" Variables have changes.")
                has_changes = True
            
            # =====================================================
            # 4. COMPARE DEVICES (main + all functions)
            # =====================================================
            elif cls._compare_devices_all(saved_data, current_data) and has_changes == False:
                print(" Devices have changes.")
                has_changes = True
                
            # =====================================================
            # 5. COMPARE SETTINGS
            # =====================================================
            elif cls._compare_settings(saved_data, current_data) and has_changes == False:
                print(" Settings have changes.")
                has_changes = True
            
            # Final tally
            print(f"Comparison complete. Changes detected: {has_changes}")
            return has_changes
            
        except Exception as e:
            print(f"Comparison error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # =========================================================================
    # MAIN CANVAS COMPARISONS
    # =========================================================================
    
    @staticmethod
    def _compare_main_canvas_blocks(saved_data, current_data):
        """Compare blocks in main canvas"""
        saved_blocks = saved_data.main_canvas.get("blocks", {})
        current_blocks = current_data.main_canvas.get("blocks", {})
        
        # Find added blocks
        for bid, c_block in current_blocks.items():
            if bid not in saved_blocks:
                print(f" New block detected: {bid}")
                return True
            else:
                # Check for modifications
                s_block = saved_blocks[bid]
                
                check_props = []
                # Properties to check
                if c_block.get('type') in ('While', 'Button', 'Switch', 'Basic_operations', 'Exponential_operations', 'Random_number',
                          'Blink_LED', 'Toggle_LED', 'Turn_OFF_LED', 'Turn_ON_LED', 'PWM_LED', 'Plus_one', 'Minus_one'):
                    check_props.append('value_1_name')
                    check_props.append('value_1_type')
                if c_block.get('type') in ('While', 'Basic_operations', 'Exponential_operations', 'Random_number'):
                    check_props.append('value_2_name')
                    check_props.append('value_2_type')
                if c_block.get('type') in ('While', 'Basic_operations', 'Exponential_operations', 'Random_number'):
                    check_props.append('operator')
                if c_block.get('type') in ('Basic_operations', 'Exponential_operations', 'Random_number'):
                    check_props.append('result_var_name')
                if c_block.get('type') in ('Timer', 'Blink_LED'):
                    check_props.append('sleep_time')
                if c_block.get('type') in ('PWM_LED'):
                    check_props.append('PWM_value')
                if c_block.get('type') == 'If':
                    for i in range(c_block.get('conditions', 1)):
                        check_props.append(f"value_{i+1}_1_name")
                        check_props.append(f"value_{i+1}_2_name")
                        check_props.append(f"operator_{i+1}")
                if c_block.get('type') == 'RGB_LED':
                    for i in range(1, 4):
                        check_props.append(f"value_{i}_1_name")
                        check_props.append(f"value_{i}_2_PWM")

                for prop in check_props:
                    val_c = c_block.get(prop, "")
                    val_s = s_block.get(prop, "")
                    if val_c != val_s:
                        print(f" Block {bid} property '{prop}' changed: saved='{val_s}' vs current='{val_c}'")
                        return True
                
                # Check connections
                c_in = c_block.get('in_connections', [])
                s_in = s_block.get('in_connections', [])
                c_out = c_block.get('out_connections', [])
                s_out = s_block.get('out_connections', [])
                
                if c_in != s_in or c_out != s_out:
                    print(f" Block {bid} connections changed: saved_in={s_in}, current_in={c_in}, saved_out={s_out}, current_out={c_out}")
                    return True
    
        # Find removed blocks
        for bid in saved_blocks:
            if bid not in current_blocks:
                print(f" Block removed: {bid}")
                return True
        
        return False

    @staticmethod
    def _compare_main_canvas_connections(saved_data, current_data):
        """Compare connections/paths in main canvas"""
        saved_paths = saved_data.main_canvas.get("paths", {})
        current_paths = current_data.main_canvas.get("paths", {})
        #print(f"Comparing main canvas connections: saved {saved_paths}, current {current_paths}")
        for connid, c_conn in current_paths.items():
            if connid not in saved_paths:
                return True
            else:
                # Check if connection properties changed
                s_conn = saved_paths[connid]
                if c_conn != s_conn:
                    return True
        
        for connid in saved_paths:
            if connid not in current_paths:
                return True
        
        return False
    
    # =========================================================================
    # FUNCTION CANVAS COMPARISONS
    # =========================================================================
    
    @staticmethod
    def _compare_function_canvases(saved_data, current_data):
        """Compare all function canvases"""
        saved_funcs = saved_data.functions
        current_funcs = current_data.functions
        
        # Find added function canvases
        for fid, func_info in current_funcs.items():
            if fid not in saved_funcs:
                return True
            else:
                # Compare blocks in this function
                FileManager._compare_function_blocks(
                    fid, saved_funcs, current_funcs
                )
                # Compare connections in this function
                FileManager._compare_function_connections(
                    fid, saved_funcs, current_funcs
                )
        
        # Find removed function canvases
        for fid, func_info in saved_funcs.items():
            if fid not in current_funcs:
                return True
            
        return False
    
    @staticmethod
    def _compare_function_blocks(fid, saved_funcs, current_funcs):
        """Compare blocks within a specific function"""
        saved_blocks = saved_funcs[fid].get("blocks", {})
        current_blocks = current_funcs[fid].get("blocks", {})
        
        # Check current blocks
        for bid, c_block in current_blocks.items():
            if bid in saved_blocks:
                s_block = saved_blocks[bid]
                
                check_props = []
                # Properties to check
                if c_block.get('type') in ('While', 'Button', 'Switch', 'Basic_operations', 'Exponential_operations', 'Random_number',
                          'Blink_LED', 'Toggle_LED', 'Turn_OFF_LED', 'Turn_ON_LED', 'PWM_LED', 'Plus_one', 'Minus_one'):
                    check_props.append('value_1_name')
                    check_props.append('value_1_type')
                if c_block.get('type') in ('While', 'Basic_operations', 'Exponential_operations', 'Random_number'):
                    check_props.append('value_2_name')
                    check_props.append('value_2_type')
                if c_block.get('type') in ('While', 'Basic_operations', 'Exponential_operations', 'Random_number'):
                    check_props.append('operator')
                if c_block.get('type') in ('Basic_operations', 'Exponential_operations', 'Random_number'):
                    check_props.append('result_var_name')
                if c_block.get('type') in ('Timer', 'Blink_LED'):
                    check_props.append('sleep_time')
                if c_block.get('type') in ('PWM_LED'):
                    check_props.append('PWM_value')
                if c_block.get('type') == 'If':
                    for i in range(c_block.get('conditions', 1)):
                        check_props.append(f"value_{i+1}_1_name")
                        check_props.append(f"value_{i+1}_2_name")
                        check_props.append(f"operator_{i+1}")
                if c_block.get('type') == 'RGB_LED':
                    for i in range(1, 4):
                        check_props.append(f"value_{i}_1_name")
                        check_props.append(f"value_{i}_2_PWM")
                
                for prop in check_props:
                    val_c = c_block.get(prop, "")
                    val_s = s_block.get(prop, "")
                    if val_c != val_s:
                        return True
            elif bid not in saved_blocks:
                return True
        
        for bid in saved_blocks:
            if bid not in current_blocks:
                return True

        return False
    
    @staticmethod
    def _compare_function_connections(fid, saved_funcs, current_funcs):
        """Compare connections within a specific function"""
        saved_paths = saved_funcs[fid].get("paths", {})
        current_paths = current_funcs[fid].get("paths", {})
        
        if saved_paths.keys() != current_paths.keys():
            return True
        else:
            # Check if any connection data changed
            for connid in saved_paths:
                if connid in current_paths:
                    if saved_paths[connid] != current_paths[connid]:
                        return True
                    
        return False
    
    # =========================================================================
    # VARIABLES COMPARISON (main + all functions)
    # =========================================================================
    
    @staticmethod
    def _compare_variables_all(saved_data, current_data):
        """Compare variables in main canvas and all functions"""
        
        # Compare main canvas variables
        saved_main_vars = saved_data.variables.get("main_canvas", {})
        current_main_vars = current_data.variables.get("main_canvas", {})
        
        if FileManager._compare_variable_group(saved_main_vars, current_main_vars, "main_canvas"):
            return True
        
        # Compare function canvas variables
        saved_func_vars = saved_data.variables.get("function_canvases", {})
        current_func_vars = current_data.variables.get("function_canvases", {})
        
        for fid in set(list(saved_func_vars.keys()) + list(current_func_vars.keys())):
            saved_fvars = saved_func_vars.get(fid, {})
            current_fvars = current_func_vars.get(fid, {})
            
            if FileManager._compare_variable_group(saved_fvars, current_fvars, f"function_{fid}"):
                return True
        
        return False
    
    @staticmethod
    def _compare_variable_group(saved_vars, current_vars, location):
        """Compare a group of variables (main or function)"""
        
        # Find added
        for vid, c_var in current_vars.items():
            if vid not in saved_vars:
                return True
            else:
                # Check for modifications
                s_var = saved_vars[vid]
                if c_var != s_var:
                    return True
            
        # Find removed
        for vid in saved_vars:
            if vid not in current_vars:
                return True
        
        return False
    
    # =========================================================================
    # DEVICES COMPARISON (main + all functions)
    # =========================================================================
    
    @staticmethod
    def _compare_devices_all(saved_data, current_data):
        """Compare devices in main canvas and all functions"""
        
        # Compare main canvas devices
        saved_main_devs = saved_data.devices.get("main_canvas", {})
        current_main_devs = current_data.devices.get("main_canvas", {})
        
        if FileManager._compare_device_group(saved_main_devs, current_main_devs):
            return True
        
        # Compare function canvas devices
        saved_func_devs = saved_data.devices.get("function_canvases", {})
        current_func_devs = current_data.devices.get("function_canvases", {})
        
        for fid in set(list(saved_func_devs.keys()) + list(current_func_devs.keys())):
            saved_fdevs = saved_func_devs.get(fid, {})
            current_fdevs = current_func_devs.get(fid, {})
            
            if FileManager._compare_device_group(saved_fdevs, current_fdevs):
                return True
            
        return False
    
    @staticmethod
    def _compare_device_group(saved_devs, current_devs):
        """Compare a group of devices (main or function)"""
        
        # Find added
        for did, c_dev in current_devs.items():
            if did not in saved_devs:
                return True
            else:
                # Check for modifications
                s_dev = saved_devs[did]
                if c_dev != s_dev:
                    return True
        
        # Find removed
        for did in saved_devs:
            if did not in current_devs:
                return True
        
        return False
    
    # =========================================================================
    # SETTINGS COMPARISON
    # =========================================================================
    
    @staticmethod
    def _compare_settings(saved_data, current_data):
        """Compare application settings"""
        saved_settings = saved_data.settings
        current_settings = current_data.settings
        
        all_keys = set(list(saved_settings.keys()) + list(current_settings.keys()))
        
        for key in all_keys:
            s_val = saved_settings.get(key)
            c_val = current_settings.get(key)
            
            if s_val != c_val:
                return True
        
        return False
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    @classmethod
    def _load_project_dict(cls, name: str) -> dict:
        """Load project as dictionary without populating Utils"""
        try:
            filepath = os.path.join(cls.PROJECTS_DIR, f"{name}" + cls.PROJECT_EXTENSION)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project dict: {e}")
            return None

    

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage:
    
    # Save current project
    FileManager.save_project("motor_control")
    
    # Load existing project
    if FileManager.load_project("motor_control"):
        print("Project loaded successfully")
    
    # List all projects
    projects = FileManager.list_projects()
    for project in projects:
        print(f"{project['name']} - Modified: {project['modified']}")
    
    # Delete a project
    FileManager.delete_project("old_project")
    
    # Auto-save
    FileManager.save_project("my_project", is_autosave=True)
    """
    pass
