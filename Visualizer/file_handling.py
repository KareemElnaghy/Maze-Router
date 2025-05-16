def input_file(filename):
    obs = []
    nets = []

    with open(filename, "r") as file:
        lines = file.readlines()

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

    # initialize two grids
    grid1 = [[0] * cols for _ in range(rows)]
    grid2 = [[0] * cols for _ in range(rows)]

    # split obstacles
    half = len(obs) // 2
    obs1 = obs[:half]
    obs2 = obs[half:]

    # place obstacles in grid1
    for x, y in obs1:
        grid1[x][y] = -1

    # place obstacles in grid2
    for x, y in obs2:
        grid2[x][y] = -1

    # return as list of grids
    return [grid1, grid2], nets
