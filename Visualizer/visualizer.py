import numpy as np
from PyQt6 import QtWidgets
import random

from vispy.scene import SceneCanvas, visuals
from vispy.app import use_app

import algorithm
from algorithm import lee_router

CANVAS_SIZE = (800, 950)  # (width, height)

GRID1 = np.linspace(0, 128, num=10*10, dtype=np.float32).reshape((10, 10))
GRID2 = np.linspace(255, 0, num=10*10, dtype=np.float32).reshape((10, 10))
IMAGE_SHAPE = GRID1.shape

COLORMAP_CHOICES = ["grays", "reds", "blues", "viridis"]
LAYER_CHOICES = ["1", "2"]

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        self._controls = Controls()
        main_layout.addWidget(self._controls)
        self._canvas_wrapper = CanvasWrapper()
        main_layout.addWidget(self._canvas_wrapper.canvas.native)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self._connect_controls()

    def _connect_controls(self):
        self._controls.colormap_chooser.currentTextChanged.connect(self._canvas_wrapper.set_image_colormap)
        self._canvas_wrapper.canvas.events.mouse_move.connect(
            lambda event: self._canvas_wrapper.on_mouse_move(event, self._controls.coord_label)
        )


class Controls(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.colormap_label = QtWidgets.QLabel("Image Colormap:")
        layout.addWidget(self.colormap_label)
        self.colormap_chooser = QtWidgets.QComboBox()
        self.colormap_chooser.addItems(COLORMAP_CHOICES)
        layout.addWidget(self.colormap_chooser)

        self.layer_label = QtWidgets.QLabel("Layer Choice:")
        layout.addWidget(self.layer_label)
        self.layer_chooser = QtWidgets.QComboBox()
        self.layer_chooser.addItems(LAYER_CHOICES)
        layout.addWidget(self.layer_chooser)

        self.coord_label = QtWidgets.QLabel()
        layout.addWidget(self.coord_label)

        layout.addStretch(1)
        self.setLayout(layout)

class CanvasWrapper:
    def __init__(self):
        self.canvas = SceneCanvas(size=CANVAS_SIZE)
        self.grid = self.canvas.central_widget.add_grid()

        self.view_top = self.grid.add_view(0, 0, bgcolor='gray')
        #image_data = _generate_grid(IMAGE_SHAPE)
        image_data = _get_lee_router_path()
        IMAGE_SHAPE = image_data.shape
        self.image = visuals.Image(
            image_data,
            texture_format="auto",
            cmap=COLORMAP_CHOICES[0],
            parent=self.view_top.scene,
        )
        self.view_top.camera = "panzoom"
        self.view_top.camera.set_range(x=(0, IMAGE_SHAPE[1]), y=(0, IMAGE_SHAPE[0]), margin=0)

    def set_image_colormap(self, cmap_name: str):
        print(f"Changing image colormap to {cmap_name}")
        self.image.cmap = cmap_name

    def on_mouse_move(self, event, label):
        scene_coords = self.view_top.scene.transform.imap(event.pos)
        x, y = scene_coords[:2]

        # check if the coordinates are within the image bounds
        grid_x = int(y)
        grid_y = int(x)
        label.setText(f"Grid X: {grid_x}, Grid Y: {grid_y}")


def _get_lee_router_path():
    # ======= TEST 1 =======
    # grid = [
    #     [0, 0, 0, -1, 0],
    #     [0, 0, 0, -1, 0],
    #     [0, 0, 0, -1, 0],
    #     [0, -1, 0, 0, 0],
    #     [0, -1, -1, 0, 0],
    # ]

    # pins = [(0,4), (4,0)]

        # ======= TEST 2 =======
    # grid = [
    #     [0, 0, -1, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, -1, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, -1, 0, 0, -1, 0, 0, 0, 0],
    #     [0, 0, 0, 0, -1, -1, -1, 0, 0, 0],
    #     [0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, -1, -1, -1, -1],
    #     [0, 0, 0, 0, 0, 0, -1, 0, 0, 0],
    #     [0, -1, -1, -1, 0, 0, -1, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    # ]

    # pins = [(2, 1), (1, 3), (7, 1), (8, 4), (4, 6), (7, 8)]

    # ======= TEST 3 =======
    grid = [
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
    ]

    pins = [(2, 1), (6, 2), (12, 2), (6, 10), (2, 14), (12, 12)]

    # # ======= TEST 4 =======
    # grid = [
    #     [0, -1, 0, 0, 0, 0],
    #     [0, -1, 0, -1, 0, 0],
    #     [0, 0, 0, 0, -1, -1],
    #     [0, 0, -1, 0, 0, 0],
    #     [-1, -1, -1, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0],
    # ]

    # pins = [(0, 0), (3, 1), (5, 0), (4, 4), (1, 4)]
    # ======= TEST 5 =======
    # grid = np.zeros((1000, 1000), dtype=int)

    # num_obstacles = int(0.10 * 1000 * 1000)
    # obstacle_indices = random.sample(range(1000 * 1000), num_obstacles)
    # for idx in obstacle_indices:
    #     r, c = divmod(idx, 1000)
    #     grid[r, c] = -1

    # pins = []
    # while len(pins) < 5:
    #     r = random.randint(0, 999)
    #     c = random.randint(0, 999)
    #     if grid[r, c] == 0:
    #         pins.append((r, c))


    path = np.array(lee_router(grid, pins), np.float32)
    print(path)
    gridnp = np.array(grid, np.float32)

    gridnp[gridnp == -1] = 128 # Obstacles
    for x, y in path.astype(int):
        gridnp[x, y] = 255

    return gridnp

def _get_lee_router_path_st():
    grid = [[0]*1000]*1000
    pins = [(1,1), (999,100), (999,999), (500,0), (500,999)]
    path = np.array(lee_router(grid, pins), np.float32)
    gridnp = np.array(grid, np.float32)
    for y, x in path.astype(int):
        gridnp[y, x] = 255

    IMAGE_SHAPE = gridnp.shape
    return gridnp


def _generate_random_image_data(shape, dtype=np.float32):
    rng = np.random.default_rng()
    data = rng.random(shape, dtype=dtype)
    return data

def _generate_grid(shape, dtype=np.float32):
    return GRID1;

if __name__ == "__main__":
    app = use_app("pyqt6")
    app.create()
    win = MyMainWindow()
    win.show()
    app.run()
