def input_file(filename):
    obs = []
    nets = []

    with open (filename,"r") as file:
        lines = file.readlines()  # Read all lines at once

    # extract grid size 
    line = lines[0].strip()

    # obstacles 
    for x in lines[1:]:  
        if x.upper().startswith("OBS"):
            y = x.strip().split('OBS')[-1]
            tup = eval(y)
            obs.append(tup)

    # nets
    for z in lines[1:]: 
        if z.lower().startswith('net'):
            z = z.strip()
            tuples = z.split(' ', 1)
            sub_net = tuples[1]
            list_of_tuples = eval(f'[{sub_net}]')
            nets.append(list_of_tuples)

    # extract grid size
    rows, cols = map(int, line.lower().split('x'))

    # initialize grid
    grid = [[0] * cols for _ in range(rows)]

    # place obstacles
    for x, y in obs:
        grid[x][y] = -1
    return grid, nets