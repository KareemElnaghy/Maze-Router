import numpy as np
import algorithm
from algorithm import lee_router

import file_handling
from file_handling import input_file
import sys

class FunctionalityWrapper:
    pins = []
    grid = []
    nets = []
    vias = []
    previous_paths = []
    previous_pins = []

    current_testcase = 0
    multiLayer = False
    current_layer_displayed = 0

    #def get_via_locations:

    def update_grid_3d(self):
        self.pins = []
        self.vias = []
        visual_grid_3d = np.array(self.grid, np.float32)
        logical_grid_3d = np.array(self.grid, np.float32)

        for net in self.nets:
            all_paths, all_vias = lee_router(logical_grid_3d, net)
            #print(all_vias)
            print("PATH")
            print(all_paths)

            print("VIAS")
            print(all_vias)
            path = np.array(all_paths, np.float32)
            vias = np.array(all_vias, np.float32)


            # obstacles
            visual_grid_3d[visual_grid_3d == -1] = 64

            # path
            for x, y, z in path.astype(int):
                visual_grid_3d[x, y, z] = 320
                logical_grid_3d[x, y, z] = -1

            # pins
            for x, y, z in net:
                logical_grid_3d[x, y, z] = -1
                visual_grid_3d[x, y, z] = 512
                self.pins.append((x, y, z))

            # vias
            via_direction = 0
            for x,y in vias.astype(int):
                visual_grid_3d[1,x,y] = 420
                visual_grid_3d[0,x,y] = 420
                self.vias.append((x, y))




            print("VISGIRD")
            print(visual_grid_3d)


        return visual_grid_3d

    def update_grid(self):
        visual_grid_3d = np.array(self.grid, np.float32)
        logical_grid_3d = np.array(self.grid, np.float32)

        visual_grid = visual_grid_3d[self.current_layer_displayed]
        logical_grid = logical_grid_3d[self.current_layer_displayed]
        filtered_nets = self.filter_nets_by_layer()

        for net in filtered_nets:
            path = np.array(lee_router(logical_grid, net), np.float32)

            #obstacles
            visual_grid[visual_grid == -1] = 64

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

    # BONUS
    def net_reordering(self):
        # Reorder nets based on the number of pins within their bounding box
        net_pin_counts = []
        all_pins = [pin for net in self.nets for pin in net]

        for net in self.nets:
            min_x = min(pin[1] for pin in net)
            max_x = max(pin[1] for pin in net)
            min_y = min(pin[2] for pin in net)
            max_y = max(pin[2] for pin in net)

            count = 0
            for pin in all_pins:
                x, y = pin[1], pin[2]
                if min_x < x < max_x and min_y < y < max_y:
                    count += 1

            net_pin_counts.append((net, count))

        net_pin_counts.sort(key=lambda x: x[1])

        self.nets = [net for net, count in net_pin_counts]

    def init_testcase(self):
        self.pins = []

        match self.current_testcase:
            case 0:
                self.grid, self.nets = input_file('Testcases/case0.txt')
                self.multiLayer = False
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}"  
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")                
            case 1:
                self.grid, self.nets = input_file('Testcases/case1.txt')
                self.multiLayer = False
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}"  
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")                
            case 2:
                self.grid, self.nets = input_file('Testcases/case2.txt')
                self.multiLayer = False
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}"  
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")               
            case 3:
                self.grid, self.nets = input_file('Testcases/case3.txt')
                self.multiLayer = False
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}" 
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")
            case 4:
                self.grid, self.nets = input_file('Testcases/case4.txt')
                self.multiLayer = True
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}"  
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")


            # 1000x1000 random Grid testcase
            case 5:
                self.nets = []
                grid_layer_0 = np.zeros((1000, 1000), dtype=int)
                grid_layer_1 = np.zeros((1000, 1000), dtype=int)

                num_obstacles = int(0.10 * 1000 * 1000)
                obstacle_indices = np.random.choice(1000*1000, num_obstacles, replace=False)

                for idx in obstacle_indices:
                    r, c = divmod(idx, 1000)
                    grid_layer_0[r, c] = -1

                rand_pins = []

                # generate 2 nets of 5 random pins on grid layer 0
                while len(self.nets) < 2:
                    while len(rand_pins) < 5:
                        r = np.random.randint(0, 999)
                        c = np.random.randint(0, 999)
                        if grid_layer_0[r, c] == 0 and grid_layer_1[r,c] == 0:
                            rand_pins.append((0, r, c))
                    self.nets.append(rand_pins)
                    rand_pins = []

                self.grid = [grid_layer_0, grid_layer_1]

            case -1:
                if len(sys.argv) > 1:
                    user_file = sys.argv[1]
                    multi =  sys.argv[2]
                    self.grid, self.nets = input_file(user_file)
                    self.multiLayer = multi
                else:
                    self.grid, self.nets = input_file('Testcases/case0.txt')
                    self.multiLayer = False
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}"  
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")



            case _:
                self.grid, self.nets = input_file('Testcases/case4.txt')
                self.multiLayer = True
                with open(f"output_case{self.current_testcase}.txt", "w") as f:
                    for i, net in enumerate(self.nets):
                        line = f"net{i+1}"  
                        for pin in net:
                            line += f" ({pin[0]}, {pin[1]}, {pin[2]})"
                        f.write(line + "\n")


        # call net reordering heuristic after loading the test case
        self.net_reordering()
