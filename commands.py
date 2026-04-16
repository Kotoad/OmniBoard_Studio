from Imports import (QUndoCommand, get_Utils, logging)

Utils = get_Utils()

class AddBlockCommand(QUndoCommand):
    def __init__(self, canvas, block_type, x, y, block_id, name=None):
        super().__init__(f"Add {block_type} Block")
        self.canvas = canvas
        self.block_type = block_type
        self.x = x
        self.y = y
        self.block_id = block_id
        self.name = name
        
        # We will store the block and its Utils data here so we can re-inject them
        self.block_widget = None
        self.block_utils_data = None

    def redo(self):
        """Executes the action (or re-executes it after an undo)"""
        if self.block_widget is None:
            # First time execution: Use your existing add_block logic
            self.block_widget = self.canvas.add_block(
                self.block_type, 
                self.x, 
                self.y, 
                self.block_id, 
                self.name
            )
            #logging.info(f"Blocks events {self.block_widget.signals}")
        else:
            # Redo execution: Safely re-add the preserved object to the scene
            self.canvas.scene.addItem(self.block_widget)
            
            # Re-inject the preserved data back into Utils
            if self.canvas.reference == "canvas":
                Utils.main_canvas['blocks'][self.block_id] = self.block_utils_data
            elif self.canvas.reference == "function":
                for f_id, f_info in Utils.functions.items():
                    if self.canvas == f_info.get('canvas'):
                        Utils.functions[f_id]['blocks'][self.block_id] = self.block_utils_data
                        break

    def undo(self):
        """Reverses the action without destroying the C++ object"""
        # 1. Remove from scene (does NOT destroy the object)
        self.canvas.scene.removeItem(self.block_widget)
        
        # 2. Extract and preserve the Utils data, then remove it from the active dictionary
        if self.canvas.reference == "canvas":
            self.block_utils_data = Utils.main_canvas['blocks'].pop(self.block_id, None)
        elif self.canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    self.block_utils_data = Utils.functions[f_id]['blocks'].pop(self.block_id, None)
                    break
    
class RemoveBlockCommand(QUndoCommand):
    def __init__(self, parent, block_id):
        super().__init__(f"Remove Block {block_id}")
        self.canvas = parent
        self.block_id = block_id
        self.removed_block = None
        self.removed_block_utils_data = None
        self.paths_data = {}

        if self.canvas.reference == "canvas":
            self.blocks_dict = Utils.main_canvas['blocks']
            self.paths_dict = Utils.main_canvas['paths']
        elif self.canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    self.blocks_dict = Utils.functions[f_id]['blocks']
                    self.paths_dict = Utils.functions[f_id]['paths']
                    break

    def redo(self):
        """Executes the action (or re-executes it after an undo)"""
        # Store the block being removed so we can restore it on undo
        if self.removed_block_utils_data is None:
            if self.block_id not in self.blocks_dict:
                logging.error(f"Error: Block ID {self.block_id} not found in Utils for removal.")
                return

            self.removed_block_utils_data = self.blocks_dict.pop(self.block_id)
            self.removed_block = self.removed_block_utils_data['widget']
            self.canvas.scene.removeItem(self.removed_block)

            out_conns = list(self.removed_block_utils_data.get('out_connections', {}).keys())
            in_conns = list(self.removed_block_utils_data.get('in_connections', {}).keys())

            for path_id in out_conns + in_conns:
                if path_id in self.paths_dict:
                    path_data = self.paths_dict.pop(path_id)
                    path_widget = path_data['item']
                    self.canvas.scene.removeItem(path_widget)

                    out_part, in_part = path_id.split("-")
                    is_out = (self.block_id == out_part)
                    other_block_id = in_part if is_out else out_part

                    other_conn_type = None

                    if other_block_id in self.blocks_dict:
                        if is_out:
                            other_conn_type = self.blocks_dict[other_block_id]['in_connections'].get(path_id)
                            self.blocks_dict[other_block_id]['in_connections'].pop(path_id, None)
                        else:
                            other_conn_type = self.blocks_dict[other_block_id]['out_connections'].get(path_id)
                            self.blocks_dict[other_block_id]['out_connections'].pop(path_id, None)
                        
                        self.paths_data[path_id] = {
                            'data': path_data,
                            'other_block_id': other_block_id,
                            'other_conn_type': other_conn_type,
                            'is_out': is_out
                        }

                        #logging.info(f"Block {self.block_id} removed and its connections updated.")
                        
        else:
            self.blocks_dict.pop(self.block_id, None)
            self.canvas.scene.removeItem(self.removed_block)

            for path_id, path_info in self.paths_data.items():
                self.paths_dict[path_id] = path_info['data']
                self.canvas.scene.addItem(path_info['data']['item'])

                other_id = path_info['other_block_id']
                if other_id in self.blocks_dict and path_info['other_conn_type'] is not None:
                    if path_info['is_out']:
                        self.blocks_dict[other_id]['in_connections'][path_id] = path_info['other_conn_type']
                    else:
                        self.blocks_dict[other_id]['out_connections'][path_id] = path_info['other_conn_type']


    def undo(self):
        """Reverses the action without destroying the C++ object"""
        self.blocks_dict[self.block_id] = self.removed_block_utils_data
        self.canvas.scene.addItem(self.removed_block)

        for path_id, path_info in self.paths_data.items():
            self.paths_dict[path_id] = path_info['data']
            self.canvas.scene.addItem(path_info['data']['item'])

            other_id = path_info['other_block_id']
            if other_id in self.blocks_dict and path_info['other_conn_type'] is not None:
                if path_info['is_out']:
                    self.blocks_dict[other_id]['in_connections'][path_id] = path_info['other_conn_type']
                else:
                    self.blocks_dict[other_id]['out_connections'][path_id] = path_info['other_conn_type']

class MoveBlockCommand(QUndoCommand):
    def __init__(self, block_widget, old_pos, new_pos):
        super().__init__("Move Block")
        self.block_widget = block_widget
        self.old_pos = old_pos
        self.new_pos = new_pos

    def redo(self):
        """Executes the action (or re-executes it after an undo)"""
        self.block_widget.setPos(self.new_pos)
        self.update_positions_data(self.new_pos)
        self.block_widget.state_manager.canvas_state.on_idle()

    def undo(self):
        """Reverses the action without destroying the C++ object"""
        self.block_widget.setPos(self.old_pos)
        self.update_positions_data(self.old_pos)
        self.block_widget.state_manager.canvas_state.on_idle()

    def update_positions_data(self, pos):
        """Update positions for consecutive moves of the same block"""
        canvas = self.block_widget.canvas
        
        if canvas.reference == 'canvas':
            if self.block_widget.block_id in Utils.main_canvas['blocks']:
                Utils.main_canvas['blocks'][self.block_widget.block_id]['x'] = pos.x()
                Utils.main_canvas['blocks'][self.block_widget.block_id]['y'] = pos.y()
        elif canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if canvas == f_info.get('canvas'):
                    if self.block_widget.block_id in f_info['blocks']:
                        f_info['blocks'][self.block_widget.block_id]['x'] = pos.x()
                        f_info['blocks'][self.block_widget.block_id]['y'] = pos.y()
                    break
                    
        if hasattr(canvas, 'path_manager'):
            canvas.path_manager.update_paths_for_widget(self.block_widget)


class AddPathCommand(QUndoCommand):
    def __init__(self, canvas, path_id, path_data):
        super().__init__(f"Add Path {path_id}")
        self.canvas = canvas
        self.path_id = path_id
        self.path_data = path_data

    def redo(self):
        """Executes the action (or re-executes it after an undo)"""
        if self.canvas.reference == "canvas":
            Utils.main_canvas['paths'][self.path_id] = self.path_data
        elif self.canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    Utils.functions[f_id]['paths'][self.path_id] = self.path_data
                    break
        self.canvas.scene.addItem(self.path_data['item'])

    def undo(self):
        """Reverses the action without destroying the C++ object"""
        if self.canvas.reference == "canvas":
            Utils.main_canvas['paths'].pop(self.path_id, None)

            from_block = self.path_data['from']
            to_block = self.path_data['to']

            if from_block in Utils.main_canvas['blocks']:
                Utils.main_canvas['blocks'][from_block]['out_connections'].pop(self.path_id, None)
            if to_block in Utils.main_canvas['blocks']:
                Utils.main_canvas['blocks'][to_block]['in_connections'].pop(self.path_id, None)
        elif self.canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    Utils.functions[f_id]['paths'].pop(self.path_id, None)

                    from_block = self.path_data['from']
                    to_block = self.path_data['to']
                    if from_block in Utils.functions[f_id]['blocks']:
                        Utils.functions[f_id]['blocks'][from_block]['out_connections'].pop(self.path_id, None)
                    if to_block in Utils.functions[f_id]['blocks']:
                        Utils.functions[f_id]['blocks'][to_block]['in_connections'].pop(self.path_id, None)
                    break
        self.canvas.scene.removeItem(self.path_data['item'])
    
class RemovePathCommand(QUndoCommand):
    def __init__(self, canvas, path_id):
        super().__init__(f"Remove Path {path_id}")
        self.canvas = canvas
        self.path_id = path_id
        self.removed_path_data = None

    def redo(self):
        """Executes the action (or re-executes it after an undo)"""
        if self.canvas.reference == "canvas":
            self.removed_path_data = Utils.main_canvas['paths'].pop(self.path_id, None)
            if self.removed_path_data:
                from_block = self.removed_path_data['from']
                to_block = self.removed_path_data['to']
                if from_block in Utils.main_canvas['blocks']:
                    Utils.main_canvas['blocks'][from_block]['out_connections'].pop(self.path_id, None)
                if to_block in Utils.main_canvas['blocks']:
                    Utils.main_canvas['blocks'][to_block]['in_connections'].pop(self.path_id, None)
        elif self.canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    self.removed_path_data = Utils.functions[f_id]['paths'].pop(self.path_id, None)
                    if self.removed_path_data:
                        from_block = self.removed_path_data['from']
                        to_block = self.removed_path_data['to']
                        if from_block in Utils.functions[f_id]['blocks']:
                            Utils.functions[f_id]['blocks'][from_block]['out_connections'].pop(self.path_id, None)
                        if to_block in Utils.functions[f_id]['blocks']:
                            Utils.functions[f_id]['blocks'][to_block]['in_connections'].pop(self.path_id, None)
                    break
        if self.removed_path_data:
            self.canvas.scene.removeItem(self.removed_path_data['item'])

    def undo(self):
        """Reverses the action without destroying the C++ object"""
        if not self.removed_path_data:
            return
        
        if self.canvas.reference == "canvas":
            Utils.main_canvas['paths'][self.path_id] = self.removed_path_data
            from_block = self.removed_path_data['from']
            to_block = self.removed_path_data['to']
            if from_block in Utils.main_canvas['blocks']:
                Utils.main_canvas['blocks'][from_block]['out_connections'][self.path_id] = None
            if to_block in Utils.main_canvas['blocks']:
                Utils.main_canvas['blocks'][to_block]['in_connections'][self.path_id] = None
        elif self.canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    Utils.functions[f_id]['paths'][self.path_id] = self.removed_path_data
                    from_block = self.removed_path_data['from']
                    to_block = self.removed_path_data['to']
                    if from_block in Utils.functions[f_id]['blocks']:
                        Utils.functions[f_id]['blocks'][from_block]['out_connections'][self.path_id] = None
                    if to_block in Utils.functions[f_id]['blocks']:
                        Utils.functions[f_id]['blocks'][to_block]['in_connections'][self.path_id] = None
                    break
        self.canvas.scene.addItem(self.removed_path_data['item'])