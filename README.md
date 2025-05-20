# Maze-Router

## Features
- **Multi-Layer Routing**: Supports single and multi-layer grids for increased flexibility.
- **Pathfinding Algorithms**: Implements Lee's algorithm for guaranteed shortest pathfinding.
- **File Handling**: Parses input files to extract grid dimensions, obstacles, and net connections.
- **Visualization**: Provides an interactive GUI using `vispy` to visualize routing paths and obstacles.

---

## Assumptions
1. Input files are formatted correctly with grid dimensions, obstacles, and net connections.
2. Obstacles and pins are within the bounds of the grid.
3. Multi-layer routing assumes two layers, with alternating horizontal and vertical preferred directions.
4. The grid is rectangular, and dimensions are specified in the format `rows x cols`.
5. Obstacles are static and do not change during routing.

---

## Limitations
1. **Scalability**: Performance may degrade for very large grids or a high number of nets.
2. **Algorithm Constraints**: Lee's algorithm is computationally expensive for large grids due to its exhaustive search nature.
3. **Visualization**: The visualizer may encounter issues on systems with incompatible OpenGL or Wayland configurations.
4. **Input Validation**: Limited error handling for malformed input files.
5. **Multi-Layer Routing**: Currently supports only two layers; additional layers would require further implementation.

---

## Input File Format

The input file should define the grid dimensions, obstacles, and nets in the following format:

1. **Grid Dimensions**: Specified on the first line in the format `rows x cols` (e.g., `5x5`).
2. **Obstacles**: Listed as `OBS(x, y)` for single-layer grids or `OBS(x, y, layer)` for multi-layer grids.
3. **Nets**: Defined as `NET (x1, y1), (x2, y2), ...` to specify the pins to be connected.

### Example Input File
5x5 
OBS(1, 1) 
OBS(2, 2) 
NET (0, 0), (4, 4)
### Explanation
- `5x5`: Defines a grid with 5 rows and 5 columns.
- `OBS(1, 1)`: Places an obstacle at row 1, column 1.
- `OBS(2, 2)`: Places an obstacle at row 2, column 2.
- `NET (0, 0), (4, 4)`: Specifies a net connecting the pins at `(0, 0)` and `(4, 4)`.

For multi-layer grids, obstacles and nets can include a layer index:
5x5 
OBS(1, 1, 0) 
OBS(2, 2, 1) 
NET (0, 0, 0), (4, 4, 1)

### Notes
- Obstacles and pins must be within the grid bounds.
- Multi-layer grids assume two layers by default, with alternating horizontal and vertical preferred directions.
- Input files must be correctly formatted to avoid parsing errors.

## Setting up dev environment


### Making the pre-commit hook executable

Make sure the pre-commit hook is executable by the system
[Check why a pre-commit hook is needed](#pre-commit)

```bash
chmod +x ./.git/hooks/pre-commit
```
> or the equivalent to your system

### Python Virtual Environment
Use python `Python3.10` and above

#### Set up a virtual environemnt for Python at the root of the project
```bash
python -m venv ./venv
```

>[!IMPORTANT]
> Do not rename your venv,
> If you really really need to rename it, add it to the `.gitignore` template

---

#### Source the virtual env to your shell:

**For POSIX complaint Shells:**

to check your current Shell
```bash
echo $0
```
The output will be your shell

Now source your shell according to the required activate script,
refer to [Python Docs on venv](https://docs.python.org/3/library/venv.html) if you cant source your shell.

For bash OR zsh
```bash
source ./venv/bin/activate
```

At the project root install project requirements:
```bash
pip install -r requirements.txt
```

### Visualizer Setup
Currently `vispy` does not query on correct OpenGL version when wayland, nvidia and certain Qt versions are invovled
see [issue 2640 on vispy](https://github.com/vispy/vispy/issues/2640)

**if** you encounter any problems run the visualizer on an xorg session, **or** set the following environment variable:
```bash
export QT_QPA_PLATFORM=xcb
```

---
## Installing or Removing Libraries **(Important)**

Any Libraries you add or remove from the project must be reflected in the `requirements.txt` to avoid errors so we standardize installation of libraries to automatically reflect in `requirements.txt`

To **install** a library use:
```bash
pip install library_to_install && rm requirements.txt && pip freeze > requirements.txt
```

To **remove** a library use:
```bash
pip uninstall library_to_install && rn requirements.txt && pip freeze > requirements.txt
```

To update the `requirements.txt` at any time use:
```bash
rm requirements.txt && python -m pip freeze > requirements.txt
```

Or the equivalent functionality of above commands according to your shell/environment

<a name="pre-commit">
</a>

>[!WARNING]
> Not updating your `requirements.txt` will abort the commit:
> This is done by the pre-commit hook in `.git/hooks/pre-commit`

## Running the Router
There are 4 test cases that are that the user can chose to view on the GUI.
Running using the defualt test cases:
```bash
python3 main.py
```
The user can chose to input any input file by stating the filename and if it is multilayered
```bash
python3 main.py input_file.txt True
```
Or
```bash
python3 main.py input_file.txt False
```

