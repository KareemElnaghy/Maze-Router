def input_file(filename):
    obs = []
    nets = []
    multiLayer = True

    with open(filename, "r") as file:
        lines = file.readlines()

    rows, cols = map(int, lines[0].strip().lower().split('x'))

    # Extract obstacles
    for x in lines[1:]:
        if x.upper().startswith("OBS"):
            y = x.strip().split('OBS')[-1]
            tup = eval(y)

            obs.append((tup[1], tup[0]))

    # Extract nets
    for z in lines[1:]:
        if z.lower().startswith('net'):
            z = z.strip()
            tuples = z.split(' ', 1)
            sub_net = tuples[1]
            # Parse as (layer, x, y) and convert to (layer, y, x)
            raw_tuples = eval(f'[{sub_net}]')
            list_of_tuples = [(t[0], t[2], t[1]) for t in raw_tuples]  # (layer, y, x)
            nets.append(list_of_tuples)

    grids = []
    num_grids = 2 if multiLayer else 1

    for _ in range(num_grids):
        grids.append([[0] * cols for _ in range(rows)])

    if num_grids == 2:
        for y, x in obs:
            grids[0][y][x] = -1
            grids[1][y][x] = -1
    elif num_grids == 1:
        for x, y in obs:
            grids[0][y][x] = -1

    return grids, nets
