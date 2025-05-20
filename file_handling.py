def input_file(filename):
    obs = []
    nets = []
    multiLayer = False

    with open(filename, "r") as file:
        lines = file.readlines()

    rows, cols = map(int, lines[0].strip().lower().split('x'))

    # Extract obstacles
    for x in lines[1:]:
        if x.upper().startswith("OBS"):
            y = x.strip().split('OBS')[-1]
            tup = eval(y)

            obs.append(tup)

    # Extract nets
    for z in lines[1:]:
        if z.lower().startswith('net'):
            z = z.strip()
            tuples = z.split(' ', 1)
            sub_net = tuples[1]


            list_of_tuples = eval(f'[{sub_net}]')

            if not multiLayer:
                for tup in list_of_tuples:
                    if tup[0] == 1:
                        multiLayer = True

            nets.append(list_of_tuples)

    grids = []
    num_grids = 2 if multiLayer else 1

    for _ in range(num_grids):
        grids.append([[0] * cols for _ in range(rows)])

    if num_grids == 2:
        half = len(obs) // 2
        obs1 = obs[:half]
        obs2 = obs[half:]

        for x, y in obs1:
            grids[0][x][y] = -1
        for x, y in obs2:
            grids[1][x][y] = -1
    elif num_grids == 1:
        for x, y in obs:
            grids[0][x][y] = -1

    return grids, nets
