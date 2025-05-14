import numpy as np
import heapq

# selects the source pin based on distance from the corner (x and y distance following manhattan routing)
def get_source_pin(pins, rows, cols):
    corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
    closest_pin = pins[0]
    min_distance = float('inf')
    for pin in pins:
        for corner in corners:
            distance = abs(pin[0] - corner[0]) + abs(pin[1] - corner[1])
            if distance < min_distance:
                min_distance = distance
                closest_pin = pin
    return closest_pin

# runs dijkstra's algorithm
def dijkstra(grid, routing_tree, target, preferred_direction, direction_cost):
    rows, cols = grid.shape
    cost_grid = np.full((rows, cols), np.inf)
    path = {}
    direction_grid = np.full((rows, cols), None)
    pq = []
    
    
    moves = [
        ((0, 1), 'H'),   # right
        ((0, -1), 'H'),  # left
        ((1, 0), 'V'),   # down
        ((-1, 0), 'V')   # up
    ]
    
    # initialize the pq
    for cell in routing_tree:
        cost_grid[cell] = 0
        direction_grid[cell] = None
        heapq.heappush(pq, (0, cell, None))

    found = False
    while pq and not found:
        current_cost, current, prev_dir = heapq.heappop(pq)
        r, c = current
        if current == target:
            found = True
            break
        if current_cost > cost_grid[r, c]:
            continue
            
        # check all possible moves for neighbors
        for (dr, dc), move_dir in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr, nc] == -1:
                    continue
                
                if move_dir == preferred_direction:
                    move_cost = 1
                else:
                    move_cost = direction_cost

                direction_change = prev_dir is not None and move_dir != prev_dir
                                
                # considering penalty for direction change
                new_cost = current_cost + move_cost + (direction_cost if direction_change else 0)
                
                if cost_grid[nr, nc] > new_cost:
                    cost_grid[nr, nc] = new_cost
                    path[(nr, nc)] = (r, c)
                    direction_grid[nr, nc] = move_dir
                    heapq.heappush(pq, (new_cost, (nr, nc), move_dir))

    if found:
        # traceback the path from the target to the routing tree and return the cost of taking this path
        path = [target]
        current = target
        while current in path:
            current = path[current]
            path.append(current)
        path.reverse()
        return path, cost_grid[target]
    else:
        return [], np.inf

def lee_router(grid, pins):
    """
    Lee router algorithm implementation
    Function receives the initialized grid and the pins to be routed as input parameters
    Router takes into consideration the preferred direction for each layer and using heuristics to determine the source pin
    """

    if len(pins) <= 1:
        return []

    grid = np.array(grid)
    rows, cols = grid.shape

    source_pin = get_source_pin(pins, rows, cols)
    routing_tree = set([source_pin])
    all_paths = []
    unrouted_pins = set(pins) - {source_pin}
    preferred_direction='H'
    direction_cost=3 # TODO: using large cost for smaller grids causes errors

    # validate pins
    for pin in pins:
        r, c = pin
        if not (0 <= r < rows and 0 <= c < cols) or grid[r, c] == -1:
            raise ValueError(f"Pin {pin} is on an obstacle or outside the grid.")

    while unrouted_pins:
        closest_pin = None
        min_cost = float('inf')
        best_path = None
        
        # for every unrouted pin we perform dijkstras from the routing tree to this potential target
        for target in unrouted_pins:
            path, total_cost = dijkstra(grid, routing_tree, target, preferred_direction, direction_cost)
            if path and total_cost < min_cost:
                min_cost = total_cost
                closest_pin = target
                best_path = path

        if closest_pin is None:
            return all_paths if all_paths else []

        # add the best path and update the routing tree
        all_paths.extend([cell for cell in best_path if cell not in routing_tree])
        for cell in best_path:
            routing_tree.add(cell)
        for r, c in best_path:
            if (r, c) not in pins:
                grid[r, c] = 1
        unrouted_pins.remove(closest_pin)

    return all_paths