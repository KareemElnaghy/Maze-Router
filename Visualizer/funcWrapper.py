import numpy as np
import algorithm
from algorithm import lee_router

class FunctionalityWrapper:
    pins = []
    grid = []
    nets = []
    previous_paths = []
    previous_pins = []

    current_testcase = 0
    multiLayer = False
    current_layer_displayed = 0

    def update_grid(self):
        visual_grid_3d = np.array(self.grid, np.float32)
        logical_grid_3d = np.array(self.grid, np.float32)

        visual_grid = visual_grid_3d[self.current_layer_displayed]
        logical_grid = logical_grid_3d[self.current_layer_displayed]
        filtered_nets = self.filter_nets_by_layer()

        for net in filtered_nets:
                path = np.array(lee_router(logical_grid, net), np.float32)

                #obstacles
                visual_grid[visual_grid == -1] = 50

                #path
                for x, y in path.astype(int):
                    visual_grid[x, y] = 320
                    logical_grid[x,y] = -1

                # pins
                for x, y in net:
                    logical_grid[x,y] = -1
                    visual_grid[x, y] = 512
                    self.pins.append((x,y))

        return visual_grid

    def filter_nets_by_layer(self):
        result = []

        for net in self.nets:
            # filter tuples in this net to only include those from the specified layer
            # and remove the layer index from each tuple
            filtered_net = [(tup[1], tup[2]) for tup in net if tup[0] == self.current_layer_displayed]

            if filtered_net:
                result.append(filtered_net)

        return result

    def init_testcase(self):
        self.pins = []
        match self.current_testcase:
            case 0:
                self.grid = [[
                [0, 0, -1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, -1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, -1, 0, 0, -1, 0, 0, 0, 0],
                [0, 0, 0, 0, -1, -1, -1, 0, 0, 0],
                [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, -1, -1, -1, -1],
                [0, 0, 0, 0, 0, 0, -1, 0, 0, 0],
                [0, -1, -1, -1, 0, 0, -1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]]
                self.multiLayer = False
                self.nets = [
                [(0, 2, 1), (0, 1, 3), (0, 7, 1), (0, 8, 4), (0, 4, 6), (0, 7, 8)],
                [(0, 0,5), (0, 3,8)],
                ]

            case 1:
                self.grid = [[
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0],
                [0, 0, 0, 0, 0, 0, -1, 0, -1, -1, -1, 0, -1, 0, 0],
                [0, 0, 0, 0, 0, -1, -1, 0, -1, -1, -1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, -1, -1, 0, -1, -1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, -1, -1, 0, 0, 0, -1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, -1, -1, -1, 0, -1, -1, 0, 0, 0, 0],
                [0, -1, 0, 0, -1, 0, -1, -1, 0, -1, 0, 0, 0, 0, 0],
                [0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, -1, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]]
                self.multiLayer = False

                self.nets = [[(0, 2, 1), (0, 6, 2), (0, 12, 2), (0, 6, 10), (0, 2, 14), (0, 12, 12)]]

            case 2:
                self.grid = [[
                    [0, -1, 0, 0, 0, 0],
                    [0, -1, 0, -1, 0, 0],
                    [0, 0, 0, 0, -1, -1],
                    [0, 0, -1, 0, 0, 0],
                    [-1, -1, -1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                ]]
                self.multiLayer = False
                self.nets = [[(0, 0, 0), (0, 3, 1), (0, 5, 0), (0, 4, 4), (0, 1, 4)]]

            case 3:
                self.grid = [np.zeros((6,6), dtype=int)]
                self.multiLayer = False
                self.nets = [[(0, 0,4), (0, 4,0)]]

            case _:
                # self.grid = np.zeros((1000, 1000), dtype=int)

                # num_obstacles = int(0.10 * 1000 * 1000)
                # obstacle_indices = random.sample(range(1000 * 1000), num_obstacles)
                # for idx in obstacle_indices:
                #     r, c = divmod(idx, 1000)
                #     self.grid[r, c] = -1

                #     self.pins = []

                # while len(self.pins) < 5:
                #     r = random.randint(0, 999)
                #     c = random.randint(0, 999)
                #     if self.grid[r, c] == 0:
                #         self.pins.append((r, c))

                # self.nets = [self.pins]
                self.grid =  [
                    [
                        [0, 0, 0, 0, 0, 0],
                        [0, 0, -1, 0, 0, 0],
                        [0, 0, -1, -1, 0, 0],
                        [0, 0, 0, -1, 0, 0],
                        [0, 0, 0, -1, 0, 0],
                        [0, 0, 0, 0, 0, 0],
                    ],
                    [
                        [0, 0, 0, 0, 0, 0],
                        [0, 0, -1, 0, 0, 0],
                        [0, 0, -1, 0, 0, 0],
                        [0, 0, -1, -1, -1, 0],
                        [0, 0, 0, 0, -1, 0],
                        [0, 0, 0, 0, 0, 0],
                    ]
                ]

                self.multiLayer = True
                self.nets = [
                    [(0,5,5), (0, 0,3), (0, 2, 1)],
                    [(1,4,3), (1,4,0)]
                ]
