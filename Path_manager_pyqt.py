from Imports import (Qt, QPoint, QLine, QPainter, QPen, QColor, QGraphicsPathItem,
                     QPointF, QPainterPath, QGraphicsEllipseItem, QGraphicsItem)
from Imports import get_Utils

Utils = get_Utils()
#MARK: - WaypointHandle
class WaypointHandle(QGraphicsEllipseItem):

    def __init__(self, x, y, index, parent=None):
        radius = 5
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.setPos(QPointF(x, y))
        self.setBrush(QColor(255, 0, 0))
        self.setZValue(1)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        #self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.radius = radius
        self.index = index  # Index of the waypoint in the path's waypoint list
        self.parent_path = parent  # Reference to the PathGraphicsItem

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # Snap to grid on move
            new_pos = value
            grid_size = 25 
            snapped_x = round(new_pos.x() / grid_size) * grid_size
            snapped_y = round(new_pos.y() / grid_size) * grid_size
            return QPointF(snapped_x, snapped_y)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            new_pos = self.pos()
            #print(f" → New position: {new_pos}")
            self.parent_path.move_waypoint(self.index, new_pos)
        return super().itemChange(change, value)

#MARK: - PathGraphicsItem
class PathGraphicsItem(QGraphicsPathItem):
    """Graphics item representing a connection path between blocks"""
    
    def __init__(self, from_block, to_block, path_id, parent_canvas, to_circle_type, from_circle_type, waypoints=None):
        super().__init__()
        if from_block == None:
            return
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)  # Ensure paths are behind blocks
        self.from_block = from_block
        self.to_block = to_block
        self.path_id = path_id
        self.canvas = parent_canvas
        self.to_circle_type = to_circle_type
        self.from_circle_type = from_circle_type
        self.waypoints = waypoints
        self.state_manager = Utils.state_manager
        #print(f"✓ PathGraphicsItem.__init__: {path_id} from {from_block.block_id} to {to_block.block_id}")
        #print(f"   from_circle_type: {from_circle_type}, to_circle_type: {to_circle_type}")
        
        # Style the path
        pen = QPen(QColor(31, 83, 141))
        pen.setWidth(2)
        self.setPen(pen)
        
        self.draw_path(self.waypoints)

    def draw_path(self, waypoints):
        """Update path using provided waypoints"""
        path = QPainterPath()
        if not waypoints:
            return
        
        start_point = QPointF(waypoints[0][0], waypoints[0][1])
        path.moveTo(start_point)

        for point in waypoints[1:]:
            #print(f"Adding line to point: {point}")
            path.lineTo(QPointF(point[0], point[1]))
        
        self.setPath(path)
        return path
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def move_waypoint(self, index, new_pos):
        """Move a specific waypoint to a new position"""
        if index < 0 or index >= len(self.waypoints):
            print("⚠ Invalid waypoint index")
            return
        print(f"Moving waypoint {index} to {new_pos}")
        self.waypoints[index] = (new_pos.x(), new_pos.y())
        self.draw_path(self.waypoints)

    def hoverEnterEvent(self, event):
        # Change color or show handle when mouse touches block
        if self.state_manager.canvas_state.current_state() != 'IDLE':
            return
        print("Mouse entered block!")
        pen = QPen(QColor(255, 0, 0))  # Change color on hover
        pen.setWidth(2)
        self.setPen(pen)
        
        self.draw_path(self.waypoints)
        self.highlight_waypoints()

        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # Reset color when mouse leaves
        print("Mouse left block!")
        pen = QPen(QColor(31, 83, 141))  # Reset color on hover leave
        pen.setWidth(2)
        self.setPen(pen)
        self.draw_path(self.waypoints)
        self.remove_waypoint_highlights()
        super().hoverLeaveEvent(event)
    
    def highlight_waypoints(self):
        """Highlight waypoints for editing"""
        for point in self.waypoints[1:len(self.waypoints)-1]:
            point_item = WaypointHandle(point[0], point[1], parent=self, index=self.waypoints.index(point))
            self.canvas.scene.addItem(point_item)
    
    def remove_waypoint_highlights(self):
        """Remove waypoint highlights"""
        for item in self.canvas.scene.items():
            if isinstance(item, WaypointHandle):
                self.canvas.scene.removeItem(item)

class PathManager:
    """Manages all path connections between blocks"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.start_node = None  # (widget, id, pos, circle_type)
        self.preview_points = []
        self.preview_item = None
        self.state_manager = Utils.state_manager
    #MARK: - Connection Management
    def start_connection(self, block, circle_center, circle_type):
        """Start a new connection from a block's output circle"""
        print(f"✓ PathManager.start_connection: {block.block_id} ({circle_type})")
        

        if self.canvas.reference == 'canvas':
            #print(" → Starting from main canvas")
            for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info.get('widget') == block:
                    if block_info.get('type') == 'End':
                        print("⚠ Cannot start connection from End block")
                        self.cancel_connection()
                        return
                    for conn_id, conn_type in block_info['out_connections'].items():
                        if conn_type == circle_type:
                            print("⚠ Output already connected on this circle")
                            self.cancel_connection()
                            return
                    self.start_node = {
                        'widget': block,
                        'id': block_id,
                        'pos': circle_center,
                        'circle_type': circle_type
                    }
                    #print(f" → Connection started from {block_id}")
                    break
        elif self.canvas.reference == 'function':
            #print(" → Starting from function canvas")
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    #print(f"   In function: {f_id}")
                    for block_id, block_info in f_info['blocks'].items():
                        if block_info.get('widget') == block:
                            if block_info.get('type') == 'End':
                                print("⚠ Cannot start connection from End block")
                                self.cancel_connection()
                                return
                            for conn_id, conn_type in block_info['out_connections'].items():
                                if conn_type == circle_type:
                                    print("⚠ Output already connected on this circle")
                                    self.cancel_connection()
                                    return
                            self.start_node = {
                                'widget': block,
                                'id': block_id,
                                'pos': circle_center,
                                'circle_type': circle_type
                            }
                            #print(f" → Connection started from {block_id} in function {f_id}")
                            break
    
    def cancel_connection(self):
        """Cancel the current connection"""
        print("✓ PathManager.cancel_connection")
        
        # Remove preview item
        if self.preview_item is not None:
            self.canvas.scene.removeItem(self.preview_item)
            self.preview_item = None
        
        self.start_node = None
        self.preview_points = []
        self.canvas.scene.update()
        self.state_manager.canvas_state.on_idle()
    
    def finalize_connection(self, block, circle_center, circle_type):
        """Finalize connection to a block's input circle"""
        if not self.start_node:
            print("⚠ No connection started")
            self.cancel_connection()
            return
        
        if self.canvas.reference == 'canvas':
            for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info.get('widget') == block:
                    print(f"✓ PathManager.finalize_connection: {block.block_id} ({circle_type})")
                    print(f"input connections: {block_info['in_connections']}, len: {len(block_info['in_connections'].keys())}")
                    for conn_id, conn_type in block_info['in_connections'].items():
                        if conn_type == circle_type:
                            print("⚠ Input already connected")
                            #self.cancel_connection()
                            return
                        print(self.start_node['widget'], block)
                    if self.start_node['widget'] == block:
                        print("⚠ Cannot connect block to itself")
                        #self.cancel_connection()
                        return
                    
        elif self.canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    for block_id, block_info in f_info['blocks'].items():
                        if block_info.get('widget') == block:
                            print(f"✓ PathManager.finalize_connection: {block.block_id} ({circle_type})")
                            print(f"input connections: {block_info['in_connections']}, len: {len(block_info['in_connections'].keys())}")
                            for conn_id, conn_type in block_info['in_connections'].items():
                                if conn_type == circle_type:
                                    print("⚠ Input already connected")
                                    #self.cancel_connection()
                                    return
                            if self.start_node['widget'] == block:
                                print("⚠ Cannot connect block to itself")
                                #self.cancel_connection()
                                return
        #print(f"✓ PathManager.finalize_connection: {block.block_id} ({circle_type})")
        
        # Find target block in Utils
        if self.canvas.reference == 'canvas':
            #print(" → Finalizing to main canvas")
            for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info.get('widget') == block:
                    from_block = self.start_node['widget']
                    to_block = block
                    connection_id = f"{self.start_node['id']}-{block_id}"
                    self.canvas.scene.removeItem(self.preview_item)
                    self.preview_item = None
                    # Create path graphics item
                    path_item = PathGraphicsItem(from_block, to_block, connection_id, self.canvas, circle_type, self.start_node['circle_type'], waypoints=self.preview_points)
                    print(f"    Created path item: {path_item}")
                    self.canvas.scene.addItem(path_item)
                    
                    # Store in Utils and scene_paths
                    Utils.main_canvas['paths'][connection_id] = {
                        'from': self.start_node['id'],
                        'from_circle_type': self.start_node['circle_type'],
                        'to': block_id,
                        'to_circle_type': circle_type,
                        'waypoints': self.preview_points,
                        'canvas': self.canvas,
                        'color': QColor(31, 83, 141),
                        'item': path_item
                    }
                    print(f"    Utils.main_canvas['paths'][{connection_id}] -> {Utils.main_canvas['paths'][connection_id]}") 
                    Utils.scene_paths[connection_id] = path_item
                    
                    # Update block connection info
                    Utils.main_canvas['blocks'][self.start_node['id']]['out_connections'].setdefault(connection_id, self.start_node['circle_type'])
                    Utils.main_canvas['blocks'][block_id]['in_connections'].setdefault(connection_id, circle_type)
                    
                    #print(f"  → Connection created: {connection_id}")
                    break
        elif self.canvas.reference == 'function':
            #print(" → Finalizing to function canvas")
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    #print(f"   In function: {f_id}")
                    for block_id, block_info in f_info['blocks'].items():
                        if block_info.get('widget') == block:
                            from_block = self.start_node['widget']
                            to_block = block
                            connection_id = f"{self.start_node['id']}-{block_id}"
                            self.canvas.scene.removeItem(self.preview_item)
                            self.preview_item = None
                            # Create path graphics item
                            path_item = PathGraphicsItem(from_block, to_block, connection_id, self.canvas, circle_type, self.start_node['circle_type'], waypoints=self.preview_points)
                            print(f"    Created path item: {path_item}")
                            try:
                                self.canvas.scene.addItem(path_item)
                                path_item.draw_path(self.preview_points)
                                self.canvas.scene.update()
                            except Exception as e:
                                print(f"Error adding path item to scene: {e}")
                            
                            # Store in Utils and scene_paths
                            Utils.functions[f_id]['paths'][connection_id] = {
                                'from': self.start_node['id'],
                                'from_circle_type': self.start_node['circle_type'],
                                'to': block_id,
                                'to_circle_type': circle_type,
                                'waypoints': self.preview_points,
                                'canvas': self.canvas,
                                'color': QColor(31, 83, 141),
                                'item': path_item
                            }
                            Utils.scene_paths[connection_id] = path_item
                            print(f"    Utils.functions[{f_id}]['paths'][{connection_id}] -> {Utils.functions[f_id]['paths'][connection_id]}")
                            # Update block connection info
                            Utils.functions[f_id]['blocks'][self.start_node['id']]['out_connections'].setdefault(connection_id, self.start_node['circle_type'])
                            Utils.functions[f_id]['blocks'][block_id]['in_connections'].setdefault(connection_id, circle_type)
                            
                            #print(f"  → Connection created: {connection_id}")
                            break
        # Reset
        self.state_manager.canvas_state.on_idle()
        self.preview_points = []
        self.start_node = None
            
    def add_point(self, pos):
        """Add a waypoint to the preview path"""
        if not self.start_node:
            return
        
        snapped_x = round(pos.x() / 25) * 25
        snapped_y = round(pos.y() / 25) * 25

        self.preview_points.insert(-1, (snapped_x, snapped_y))
        # Update preview path
        print(f"Preview points: {self.preview_points}")
        if self.preview_item:
            self.preview_item.draw_path(self.preview_points)
            self.canvas.scene.update()

    def update_preview_path(self, mouse_pos):
        """Update preview path as mouse moves"""
        if not self.start_node:
            return
        print(f"✓ PathManager.update_preview_path to {mouse_pos}")
        # Calculate waypoints
        if not self.preview_points:
            print(" → Initializing preview points")
            snapped_x = round(self.start_node['pos'].x() / 25) * 25
            snapped_y = round(self.start_node['pos'].y() / 25) * 25
            self.preview_points = [(snapped_x, snapped_y), (mouse_pos.x(), mouse_pos.y())]
        else:
            print(" → Updating last preview point")
            grid_size = 25
            snapped_x = round(mouse_pos.x() / grid_size) * grid_size
            snapped_y = round(mouse_pos.y() / grid_size) * grid_size
            self.preview_points[-1] = (snapped_x, snapped_y)
        # Create/update preview item if needed
        if self.preview_item is None:
            # CREATE an instance with a dummy path first
            print(" → Creating preview item")
            self.preview_item = PathGraphicsItem(
                self.start_node['widget'], 
                self.start_node['widget'],  # temp to_block
                "preview",
                self.canvas,
                None, 
                None
            )
            self.canvas.scene.addItem(self.preview_item)

        # Now update the preview path on the instance
        self.preview_item.draw_path(self.preview_points)
        self.canvas.scene.update()

    def update_paths_for_widget(self, widget):
        """Update all paths connected to a widget"""
        
        for path_id, path_item in Utils.scene_paths.items():
            if path_item.to_block == widget:
                #print(f"Updating to block path: {path_id}")
                if self.canvas.reference == 'function':
                    for f_id, f_info in Utils.functions.items():
                        if self.canvas == f_info.get('canvas'):
                            for path_id, path_info in Utils.functions[f_id]['paths'].items():
                                if path_id == path_item.path_id:
                                    waypoints = path_info['waypoints']
                                    #print(f"    Pos_x: {path_item.to_block.pos().x()+6}, Pos_y: {path_item.to_block.pos().y()}")
                                    if path_info['to_circle_type'] == 'in':
                                        waypoints[-1] = (path_item.to_block.pos().x()+6, path_item.to_block.pos().y() + (25 * ((path_item.to_block.height / 25) - 1)))
                                    #print(f" → Found waypoints for path {path_id}: {waypoints}")
                                    path_item.draw_path(waypoints)
                elif self.canvas.reference == 'canvas':
                    for path_id, path_info in Utils.main_canvas['paths'].items():
                        if path_id == path_item.path_id:
                            waypoints = path_info['waypoints']
                            #print(f"    Pos_x: {path_item.to_block.pos().x()+6}, Pos_y: {path_item.to_block.pos().y()}")
                            if path_info['to_circle_type'] == 'in':
                                waypoints[-1] = (path_item.to_block.pos().x()+6, path_item.to_block.pos().y() + (25 * ((path_item.to_block.height / 25) - 1)))
                            #print(f" → Found waypoints for path {path_id}: {waypoints}")
                            path_item.draw_path(waypoints)
            elif path_item.from_block == widget:
                #print(f"Updating from block path: {path_id}")
                if self.canvas.reference == 'function':
                    for f_id, f_info in Utils.functions.items():
                        if self.canvas == f_info.get('canvas'):
                            for path_id, path_info in Utils.functions[f_id]['paths'].items():
                                if path_id == path_item.path_id:
                                    waypoints = path_info['waypoints']
                                    #print(f"    Pos_x: {path_item.from_block.pos().x()+6}, Pos_y: {path_item.from_block.pos().y()}")
                                    if path_info['from_circle_type'].startswith('out'):
                                        #print(f"    Detected output circle type: {path_info['from_circle_type']}")
                                        for block_id, block_info in f_info['blocks'].items():
                                            if block_info.get('widget') == path_item.from_block:
                                                i = block_info['outputs']
                                                break
                                        j = int(path_info['from_circle_type'].split('_')[1])
                                        y_offset = j * 25
                                    
                                        waypoints[0] = (
                                            path_item.from_block.pos().x() + path_item.from_block.width + 6,
                                            path_item.from_block.pos().y() + y_offset
                                        )
                                        #print(f" → Found waypoints for path {path_id}: {waypoints}")
                                        path_item.draw_path(waypoints)
                elif self.canvas.reference == 'canvas':
                    for path_id, path_info in Utils.main_canvas['paths'].items():
                        if path_id == path_item.path_id:
                            waypoints = path_info['waypoints']
                            #print(f"    Pos_x: {path_item.from_block.pos().x()+6}, Pos_y: {path_item.from_block.pos().y()}")
                            if path_info['from_circle_type'].startswith('out'):
                                #print(f"    Detected output circle type: {path_info['from_circle_type']}")
                                for block_id, block_info in Utils.main_canvas['blocks'].items():
                                    if block_info.get('widget') == path_item.from_block:
                                        i = block_info['outputs']
                                        break
                                j = int(path_info['from_circle_type'].split('_')[1])
                                y_offset = j * 25
                                waypoints[0] = (
                                    path_item.from_block.pos().x() + path_item.from_block.width + 6,
                                    path_item.from_block.pos().y() + y_offset
                                )
                            #print(f" → Found waypoints for path {path_id}: {waypoints}")
                            path_item.draw_path(waypoints)
    
    def remove_paths_for_block(self, block_id):
        """Remove all paths connected to a block"""
        #print(f"✓ PathManager.remove_paths_for_block: {block_id}")
        
        paths_to_remove = []
        
        # Find all connected paths
        for path_id, path_item in list(Utils.scene_paths.items()):
            if path_item.from_block.block_id == block_id or path_item.to_block.block_id == block_id:
                self.canvas.scene.removeItem(path_item)
                paths_to_remove.append(path_id)
        
        # Remove from dictionaries
        for path_id in paths_to_remove:
            if path_id in Utils.paths:
                del Utils.paths[path_id]
            if path_id in Utils.scene_paths:
                del Utils.scene_paths[path_id]
    
    def remove_path(self, path_id):
        """Remove a specific path"""
        if path_id in Utils.scene_paths:
            path_item = Utils.scene_paths[path_id]
            self.canvas.scene.removeItem(path_item)
            del Utils.scene_paths[path_id]
        
        if path_id in Utils.paths:
            del Utils.paths[path_id]
    
    def clear_all_paths(self):
        """Clear all paths"""
        for path_id in list(Utils.scene_paths.keys()):
            self.remove_path(path_id)
        Utils.paths.clear()
        