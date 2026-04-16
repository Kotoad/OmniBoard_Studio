from Imports import get_Utils, logging
Utils = get_Utils()


class DataControl:
    def __init__(self):
        pass
    #MARK: Inicilize_date
    def inicilize_date(self, block, block_type, block_id, x, y, name=None):
        """Load data from a block into the application state."""
        # Placeholder for loading data logic
        #logging.info(f"Loading data from block: {block_id} of type {block_type}")
        if block_type in ('While'):
            info = {
                'type': block_type.split('_')[0],
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'value_2_name': 'N',
                'value_2_type': None,
                'operator': "==",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Return':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Button':
            info = {
                'type': block_type.split('_')[0],
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'If':
            info = {
                'type': block_type.split('_')[0],
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'first_vars': {},
                'second_vars': {},
                'operators': {},
                'conditions': 1,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Networks':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'networks': 2,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Timer':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'sleep_time': "1000",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Switch':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'switch_state': False,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ('Start', 'End', 'While_true'):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Function":
            info = {
                'type': 'Function',
                'id': block_id,
                'name': name,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'return_var_name': '',
                'return_var_type': None,
                'internal_vars': {
                    'main_vars': {},
                    'ref_vars': {},
                },
                'internal_devs': {
                    'main_devs': {},
                    'ref_devs': {},
                },
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ("Plus", "Minus", "Multiply", "Divide", "Modulo", "Power", "Root", "Random_number"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'value_2_name': 'N',
                'value_2_type': None,
                'operator': None,
                'result_var_name': 'N',
                'result_var_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ("Lower", "Greater", "Equal", "Not_equal", "Greater_equal", "Lower_equal"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 2,
                'value_1_name': 'N',
                'value_1_type': None,
                'value_2_name': 'N',
                'value_2_type': None,
                'operator': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ("Plus_one", "Minus_one"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Blink_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'sleep_time': "1000",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ("Toggle_LED", "LED_ON", "LED_OFF"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "PWM_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'value_1_name': 'N',
                'value_1_type': None,
                'PWM_value': "50",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'RGB_LED':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'first_vars': {},
                'second_vars': {},
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        else:
            logging.warning(f"Unknown block type {block_type}")
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': 1,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        return info
    #MARK: Load_from_data
    def load_from_data(self, block, block_id, block_type, x, y, canvas, from_where):
        """Load block data into the application state."""
        # Placeholder for loading data logic
        if from_where == 'canvas':
            data = Utils.project_data.main_canvas['blocks'][block_id]
        elif from_where == 'function':
            data = None
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas:
                    data = Utils.project_data.functions[function_id]['blocks'][block_id]
                    break
        if data is None:
            logging.warning(f"Block ID {block_id} not found in any function for the given canvas.")
            return None
        if block_type in ('While'):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'value_2_name': data.get('value_2_name', "N"),
                'value_2_type': data.get('value_2_type', "N/A"),
                'operator': data.get('operator', "=="),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Return':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Button':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'If':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'first_vars': data.get('first_vars', {}),
                'second_vars': data.get('second_vars', {}),
                'operators': data.get('operators', {}),
                'conditions': data.get('conditions', 1),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Networks':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'networks': data.get('networks', 2),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Timer':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'sleep_time': data.get('sleep_time', "1000"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Switch':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'switch_state': data.get('switch_state', False),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type in ('Start', 'End', 'While_true'):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type in ["Plus", "Minus", "Multiply", "Divide", "Modulo", "Power", "Root", "Random_number"]:
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'value_2_name': data.get('value_2_name', "N"),
                'value_2_type': data.get('value_2_type', "N/A"),
                'operator': data.get('operator', None),
                'result_var_name': data.get('result_var_name', "N"),
                'result_var_type': data.get('result_var_type', "N/A"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type in ("Lower", "Greater", "Equal", "Not_equal", "Greater_equal", "Lower_equal"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'value_2_name': data.get('value_2_name', "N"),
                'value_2_type': data.get('value_2_type', "N/A"),
                'operator': data.get('operator', None),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type in ("Plus_one", "Minus_one"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Blink_LED':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'sleep_time': data.get('sleep_time', "1000"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type in ('Toggle_LED', 'LED_ON', 'LED_OFF'):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'PWM_LED':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'value_1_name': data.get('value_1_name', "N"),
                'value_1_type': data.get('value_1_type', "N/A"),
                'PWM_value': data.get('PWM_value', "50"),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'Function':
            info = {
                'type': 'Function',
                'id': block_id,
                'name': data.get('name', ''),
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'return_var_name': data.get('return_var_name', ''),
                'return_var_type': data.get('return_var_type', None),
                'internal_vars': {
                    'main_vars': data.get('internal_vars', {}).get('main_vars', {}),
                    'ref_vars': data.get('internal_vars', {}).get('ref_vars', {}),
                },
                'internal_devs': {
                    'main_devs': data.get('internal_devs', {}).get('main_devs', {}),
                    'ref_devs': data.get('internal_devs', {}).get('ref_devs', {}),
                },
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        elif block_type == 'RGB_LED':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'first_vars': data.get('first_vars', {}),
                'second_vars': data.get('second_vars', {}),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        else:
            logging.warning(f"Unknown block type {block_type}")
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'outputs': data.get('outputs', 1),
                'in_connections': data.get('in_connections', {}),
                'out_connections': data.get('out_connections', {}),
                'canvas': canvas
            }
        return info
    #MARK: Save_data
    def save_data(self, block_id, block_info):
        if block_info['type'] in ('While'):
            info = {
                'type': block_info['type'].split('_')[0],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'value_2_name': block_info.get('value_2_name', ''),
                'value_2_type': block_info.get('value_2_type', ''),
                'operator': block_info.get('operator', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Return':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Button':
            info = {
                'type': block_info['type'].split('_')[0],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'If':
            info = {
                'type': block_info['type'].split('_')[0],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'first_vars': block_info.get('first_vars', {}),
                'operators': block_info.get('operators', {}),
                'second_vars': block_info.get('second_vars', {}),
                'conditions': block_info.get('conditions', 1),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Networks':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'networks': block_info.get('networks', 2),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Timer':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'sleep_time': block_info.get('sleep_time', '1000'),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Switch':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'switch_state': block_info.get('switch_state', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] in ('Start', 'End', 'While_true'):
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] in ("Plus", "Minus", "Multiply", "Divide", "Modulo", "Power", "Root", "Random_number"):
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'value_2_name': block_info.get('value_2_name', ''),
                'value_2_type': block_info.get('value_2_type', ''),
                'operator': block_info.get('operator', ''),
                'result_var_name': block_info.get('result_var_name', ''),
                'result_var_type': block_info.get('result_var_type', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] in ("Lower", "Greater", "Equal", "Not_equal", "Greater_equal", "Lower_equal"):
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'value_2_name': block_info.get('value_2_name', ''),
                'value_2_type': block_info.get('value_2_type', ''),
                'operator': block_info.get('operator', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] in ("Plus_one", "Minus_one"):
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', "N"),
                'value_1_type': block_info.get('value_1_type', "N/A"),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Blink_LED':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'sleep_time': block_info.get('sleep_time', '1000'),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] in ('Toggle_LED', 'LED_ON', 'LED_OFF'):
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'PWM_LED':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'value_1_name': block_info.get('value_1_name', ''),
                'value_1_type': block_info.get('value_1_type', ''),
                'PWM_value': block_info.get('PWM_value', '50'),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'Function':
            info = {
                'type': 'Function',
                'id': block_id,
                'name': block_info['name'],
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'return_var_name': block_info.get('return_var_name', ''),
                'return_var_type': block_info.get('return_var_type', None),
                'internal_vars': {
                    'main_vars': block_info['internal_vars'].get('main_vars', {}),
                    'ref_vars': block_info['internal_vars'].get('ref_vars', {}),
                },
                'internal_devs': {
                    'main_devs': block_info['internal_devs'].get('main_devs', {}),
                    'ref_devs': block_info['internal_devs'].get('ref_devs', {}),
                },
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        elif block_info['type'] == 'RGB_LED':
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'first_vars': block_info.get('first_vars', {}),
                'second_vars': block_info.get('second_vars', {}),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        else:
            logging.warning(f"Unknown block type {block_info['type']}")
            info = {
                'type': block_info['type'],
                'id': block_id,
                'width': block_info['widget'].boundingRect().width(),
                'height': block_info['widget'].boundingRect().height(),
                'x': block_info['x'],
                'y': block_info['y'],
                'outputs': block_info.get('outputs', 1),
                'in_connections': block_info.get('in_connections', {}),
                'out_connections': block_info.get('out_connections', {}),
            }
        return info