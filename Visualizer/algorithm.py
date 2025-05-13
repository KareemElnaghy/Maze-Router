import numpy as np
from collections import deque

def get_source_pin(pins, rows, cols):
    """
    Function that retrives the source pin from the list of pins
    by selecting the pin closest to the corner of the grid.
    """

    corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]

    closest_pin = pins[0]
    min_distance = float('inf')

    # loop over each pin and keep track of min distance between pin and corner
    for pin in pins:
        for corner in corners:
            distance = abs(pin[0] - corner[0]) + abs(pin[1] - corner[1])
            if distance < min_distance:
                min_distance = distance
                closest_pin = pin

    return closest_pin
    

def lee_router(grid, pins):
    """
    grid: 2D list or np.array, obstacles are -1, empty is 0
    pins: list of (row, col) tuples, first is the source, rest are targets
    Returns: list of (row, col) tuples forming a path passing through all pins in order after propagating and backtracking
    """

    if len(pins) <= 1:  # base case: no pins to route
        return []


    # initialization
    grid = np.array(grid)
    rows, cols = grid.shape
    source_pin = get_source_pin(pins, rows, cols)
    routing_tree = set([source_pin])
    all_paths = []
    unrouted_pins = set(pins[1:])

    # validate pins
    for pin in pins:
        r, c = pin
        if not (0 <= r < rows and 0 <= c < cols) or grid[r, c] == -1:
            print(f"Pin {pin} is on an obstacle or outside the grid.")

    while unrouted_pins:
        closest_pin = None
        min_distance = float('inf')
        best_path = None

        for target in unrouted_pins:
            # distance grid: -2 = unvisited, -1 = obs, >=0 = dist
            distance = np.full((rows, cols), -2, dtype=int)
            for r in range(rows):
                for c in range(cols):
                    if grid[r, c] == -1 and (r, c) not in pins:
                        distance[r, c] = -1

            # perform bfs from all the cells in the routing tree
            queue = deque()
            for cell in routing_tree:
                distance[cell] = 0
                queue.append(cell)

            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            found = False

            while queue and not found:
                current = queue.popleft()
                r, c = current
                for dRow, dCol in directions:
                    nr, nc = r + dRow, c + dCol
                    if (0 <= nr < rows and 0 <= nc < cols and distance[nr, nc] == -2):
                        distance[nr, nc] = distance[r, c] + 1
                        queue.append((nr, nc))
                        if (nr, nc) == target:
                            found = True
                            break

            if found and distance[target] < min_distance:
                min_distance = distance[target]
                closest_pin = target
                # backtrack 
                path = [target]
                current = target
                while distance[current] != 0:
                    r, c = current
                    for dRow, dCol in directions:
                        nr, nc = r + dRow, c + dCol
                        if (0 <= nr < rows and 0 <= nc < cols and
                            distance[nr, nc] == distance[r, c] - 1):
                            path.append((nr, nc))
                            current = (nr, nc)
                            break
                path.reverse()
                best_path = path

        if closest_pin is None:
            # no path found to any remaining pin
            return []

        # add the best path and update the routing tree
        all_paths.extend(best_path)
        for cell in best_path:
            routing_tree.add(cell)
        for r, c in best_path:
            if (r, c) not in pins:
                grid[r, c] = 1  # Mark as routed
        unrouted_pins.remove(closest_pin)

    return all_paths