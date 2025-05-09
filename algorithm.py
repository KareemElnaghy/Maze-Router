import numpy as np
from collections import deque

def lee_router(grid, pins):
    if len(pins) <= 1: # base case if we only have one pin or no pins
        return []

    rows, cols = len(grid), len(grid[0])
    routing_tree = {pins[0]}
    all_paths = []
    unrouted_pins = set(pins[1:])

    while unrouted_pins:
        closest_pin = None
        min_distance = float('inf')
        best_path = None

        for target in unrouted_pins:
            distance = np.full((rows, cols), -2, dtype=int)

            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] != 0 and (r, c) not in pins:
                        distance[r, c] = -1

            queue = deque()
            for cell in routing_tree:
                distance[cell] = 0
                queue.append(cell)

            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            target_found = False

            while queue and not target_found:
                current = queue.popleft()
                r, c = current

                for dr, dc in directions:
                    nr, nc = r + dr, c + dc

                    if (0 <= nr < rows and 0 <= nc < cols and
                            distance[nr, nc] == -2):

                        distance[nr, nc] = distance[r, c] + 1
                        queue.append((nr, nc))

                        if (nr, nc) == target:
                            target_found = True
                            break

            if target_found and distance[target] < min_distance:
                min_distance = distance[target]
                closest_pin = target
                path = [target]
                current = target

                while distance[current] != 0:
                    r, c = current
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc

                        if (0 <= nr < rows and 0 <= nc < cols and
                                distance[nr, nc] == distance[r, c] - 1):
                            path.append((nr, nc))
                            current = (nr, nc)
                            break

                path.reverse()
                best_path = path

        if closest_pin is None:
            return list(routing_tree) if routing_tree else []

        all_paths.extend(best_path)

        for cell in best_path:
            routing_tree.add(cell)

        for r, c in best_path:
            if (r, c) not in pins:
                grid[r][c] = 1

        unrouted_pins.remove(closest_pin)

    return all_paths

def main():
    grid = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    pins = [(1, 1), (2, 4), (5, 2)]

    routing_tree = lee_router(grid, pins)
    print("Routing tree:", routing_tree)

if __name__ == "__main__":
    main()