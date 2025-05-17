import numpy as np
import cProfile, pstats, io
from pstats import SortKey
from collections import deque
import heapq

direction_cost=10
via_cost=2

# selects the source pin based on distance from the corner (x and y distance following manhattan routing)
# starts from the first metal layer
def get_source_pin(pins, rows, cols):
    """Find starting pin closest to any corner"""
    corners = [(0, 0, 0), (0,0, cols-1), (0,rows-1, 0), (0,rows-1, cols-1),
               (1, 0, 0), (1,0, cols-1), (1,rows-1, 0), (1,rows-1, cols-1)]
    closest_pin = pins[0]
    min_distance = float('inf')

    for pin in pins:
        for corner in corners:
            # Manhattan distance to corner (ignoring layer)
            distance = abs(pin[1] - corner[1]) + abs(pin[2] - corner[2])
            if distance < min_distance:
                min_distance = distance
                closest_pin = pin
    return closest_pin

# runs dijkstra's algorithm
def dijkstra(grid, routing_tree, target, preferred_directions, direction_cost, via_cost):
    """Dijkstra for 3D grid with layers"""
    layers, rows, cols = grid.shape
    cost_grid = np.full((layers, rows, cols), np.inf)
    path = {}
    direction_grid = np.full((layers, rows, cols), None)
    pq = []

    planar_moves = [
        ((0, 0, 1), 'H'),   # right
        ((0, 0, -1), 'H'),  # left
        ((0, 1, 0), 'V'),   # down
        ((0, -1, 0), 'V')   # up
    ]
    
    # Initialize pq
    for cell in routing_tree:
        cost_grid[cell] = 0
        direction_grid[cell] = None
        heapq.heappush(pq, (0, cell, None))

    found = False
    

    while pq and not found:
        current_cost, current, prev_dir = heapq.heappop(pq)
        l, r, c = current
        
        if current == target:
            found = True
            break
            
        if current_cost > cost_grid[l, r, c]:
            continue
        
        for (dl, dr, dc), move_dir in planar_moves:
            nl, nr, nc = l + dl, r + dr, c + dc
            
            if 0 <= nl < layers and 0 <= nr < rows and 0 <= nc < cols:
                if grid[nl, nr, nc] == -1: 
                    continue
                
                preferred = preferred_directions[l]
                move_cost = 1 if move_dir == preferred else direction_cost
                
                direction_change = prev_dir is not None and move_dir != prev_dir
                bend_cost = direction_cost if direction_change else 0
                
                new_cost = current_cost + move_cost + bend_cost
                
                if cost_grid[nl, nr, nc] > new_cost:
                    cost_grid[nl, nr, nc] = new_cost
                    path[(nl, nr, nc)] = (l, r, c)
                    direction_grid[nl, nr, nc] = move_dir
                    heapq.heappush(pq, (new_cost, (nl, nr, nc), move_dir))
        
        for dl in [-1, 1]: 
            nl = l + dl
            if 0 <= nl < layers:
                if grid[nl, r, c] == -1: 
                    continue
        
                # Add a small bias to via cost to break ties in favor of non-preferred direction
                new_cost = current_cost + via_cost + 0.1
        
                if cost_grid[nl, r, c] > new_cost:
                    cost_grid[nl, r, c] = new_cost
                    path[(nl, r, c)] = (l, r, c)
                    direction_grid[nl, r, c] = 'Via'
                    heapq.heappush(pq, (new_cost, (nl, r, c), None))
    
    if found:
        # Reconstruct path
        path_copy = [target]
        via_locations = [] 
        current = target
        while current in path:
            prev = path[current]

            if current[0] != prev[0]:
                via_locations.append((current[1], current[2]))
            current = prev
            path_copy.append(current)
        path_copy.reverse()
        via_locations.reverse()  # Reverse to maintain order from source to target
        return path_copy, cost_grid[target], via_locations
    else:
        return [], np.inf, []

def lee_router_multi(grid, pins, direction_cost=3, via_cost=5):
    """Multi-layer Lee router implementation"""
    if len(pins) <= 1:
        return []

    grid = np.array(grid)
    
    if len(grid.shape) == 2:
        rows, cols = grid.shape
        grid_3d = np.zeros((2, rows, cols))
        grid_3d[0] = grid.copy()
        grid_3d[1] = grid.copy()
        grid = grid_3d
    
    layers, rows, cols = grid.shape
    
    # Convert 2D pins to 3D if needed
    if len(pins[0]) == 2:
        pins = [(0, r, c) for r, c in pins]
    
    # Define preferred direction for each layer (alternating)
    preferred_directions = []
    for l in range(layers):
        if l == 0:
            preferred_directions.append('H')  # Layer 0: Horizontal
        elif l == 1:
            preferred_directions.append('V')  # Layer 1: Vertical
    
    # Validate pins - FIXED THIS PART
    for pin in pins:
        l, r, c = pin
        # Check if pin is within bounds
        if not (0 <= l < layers and 0 <= r < rows and 0 <= c < cols):
            print(f"Warning: Pin {pin} is out of bounds. Grid shape: {grid.shape}")
            raise ValueError(f"Pin {pin} is outside valid grid range ({layers}×{rows}×{cols})")
            
        if grid[l, r, c] == -1:
            print(f"Warning: Pin {pin} is on an obstacle")
            raise ValueError(f"Pin {pin} is on an obstacle")
    
    source_pin = get_source_pin(pins, rows, cols)
    routing_tree = set([source_pin])
    all_paths = []
    all_vias = []
    unrouted_pins = set(pins) - {source_pin}

    # Validate pins
    for pin in pins:
        l, r, c = pin
        if not (0 <= l < layers and 0 <= r < rows and 0 <= c < cols) or grid[l, r, c] == -1:
            raise ValueError(f"Pin {pin} is invalid or on an obstacle.")

    while unrouted_pins:
        closest_pin = None
        min_cost = float('inf')
        best_path = None
        
        for target in unrouted_pins:
            path, total_cost, vias = dijkstra(grid, routing_tree, target, 
                                         preferred_directions, direction_cost, via_cost)
            if path and total_cost < min_cost:
                min_cost = total_cost
                closest_pin = target
                best_path = path
                best_vias = vias

        if closest_pin is None:
            return all_paths if all_paths else [], all_vias

        all_paths.extend([cell for cell in best_path if cell not in routing_tree])
        all_vias.extend(best_vias)

        for idx, cell in enumerate(best_path):
            routing_tree.add(cell)
            l, r, c = cell
            # Only mark wire on the upper layer (layer 1) if the path is routed there
            if l == 1 and (l, r, c) not in pins:
                grid[l, r, c] = 1
        unrouted_pins.remove(closest_pin)
    # print(all_vias)
    return all_paths, all_vias

def lee_router(grid, pins):
    """Wrapper for backward compatibility"""
    grid = np.array(grid)
    
    if len(grid.shape) == 3:
        if len(pins[0]) == 3:

            return lee_router_multi(grid, pins, direction_cost, via_cost)
        else:
            pins_3d = [(0, r, c) for r, c in pins]
            paths_3d, vias = lee_router_multi(grid, pins_3d, direction_cost, via_cost)
            return [(r, c) for l, r, c in paths_3d]
    else:
        pins_3d = [(0, r, c) for r, c in pins]
        paths_3d, vias = lee_router_multi(grid, pins_3d, direction_cost, via_cost)
        return [(r, c) for l, r, c in paths_3d]
    
    