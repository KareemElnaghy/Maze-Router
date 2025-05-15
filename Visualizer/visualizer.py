import numpy as np
from PyQt6 import QtWidgets
import random

from vispy.scene import SceneCanvas, visuals
from vispy.app import use_app

import algorithm
from algorithm import lee_router

CANVAS_SIZE = (1000, 1000)  # (width, height)
IMAGE_SHAPE = (1000, 1000)

COLORMAP_CHOICES = ["viridis", "hot", "grays", "reds", "blues"]
LAYER_CHOICES = ["Layer 0", "Layer 1", "Combined"]
TESTCASE_CHOICES = ["0", "1", "2", "3", "4"]

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
        self._connect_canvas()

    def _connect_canvas(self):
        self._canvas_wrapper.canvas.events.mouse_move.connect(
            lambda event: self._canvas_wrapper.on_mouse_move(event, self._controls.coord_label)
        )
        self._canvas_wrapper.canvas.events.mouse_press.connect(self._canvas_wrapper.on_mouse_press)

    def _connect_controls(self):
        self._controls.colormap_chooser.currentTextChanged.connect(self._canvas_wrapper.set_image_colormap)
        self._controls.testcase_chooser.currentTextChanged.connect(self._canvas_wrapper.set_testcase_and_redraw)
        self._controls.layer_chooser.currentTextChanged.connect(self._canvas_wrapper.set_active_layer_and_redraw)

class Controls(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        self.colormap_label = QtWidgets.QLabel("Image Colormap:")
        layout.addWidget(self.colormap_label)
        self.colormap_chooser = QtWidgets.QComboBox()
        self.colormap_chooser.addItems(COLORMAP_CHOICES)
        layout.addWidget(self.colormap_chooser)

        self.testcase_label = QtWidgets.QLabel("Testcase Choice:")
        layout.addWidget(self.testcase_label)
        self.testcase_chooser = QtWidgets.QComboBox()
        self.testcase_chooser.addItems(TESTCASE_CHOICES)
        layout.addWidget(self.testcase_chooser)

        self.layer_label = QtWidgets.QLabel("Layer View:")
        layout.addWidget(self.layer_label)
        self.layer_chooser = QtWidgets.QComboBox()
        self.layer_chooser.addItems(LAYER_CHOICES)
        layout.addWidget(self.layer_chooser)

        self.coord_label = QtWidgets.QLabel()
        layout.addWidget(self.coord_label)

        layout.addStretch(1)
        self.setLayout(layout)

class CanvasWrapper:
    _is_choosing_pin = False
    _active_layer = "Layer 0"  # Default active layer

    def __init__(self):
        self.canvas = SceneCanvas(size=CANVAS_SIZE)
        self.grid = self.canvas.central_widget.add_grid()
        self.view_top = self.grid.add_view(0, 0, bgcolor='gray')

        self.funcWrapper = FunctionalityWrapper()

        initial_data = np.zeros((1, 1), dtype=np.float32) # placeholder
        self.image = visuals.Image(
            initial_data,
            texture_format="auto",
            interpolation="nearest",
            cmap=COLORMAP_CHOICES[0],
            parent=self.view_top.scene,
        )
        self._pin_text_visuals = []

        self.funcWrapper.current_testcase = 0
        self.update_image()

    def update_image(self):
        self.funcWrapper.init_testcase()
        image_data = self.funcWrapper.update_grid(self._active_layer)
        pins = self.funcWrapper.pins
        IMAGE_SHAPE = image_data.shape
        self.image.set_data(image_data)

        for visual in self._pin_text_visuals:
            visual.parent = None
        self._pin_text_visuals = []

        for i, pin in enumerate(pins):
            # Handle both 2D and 3D pins for visualization
            if len(pin) == 3:  # 3D pin (layer, row, col)
                l, r, c = pin
                # Only show pins for the active layer or all pins in combined view
                if self._active_layer == "Combined" or self._active_layer == f"Layer {l}":
                    pin_text = visuals.Text(f'P{i+1}', pos=(c+0.5, r+0.5), color='black',
                                        font_size=8, anchor_x='center', anchor_y='center',
                                        parent=self.view_top.scene)
                    self._pin_text_visuals.append(pin_text)
            else:  # 2D pin (row, col)
                r, c = pin
                pin_text = visuals.Text(f'P{i+1}', pos=(c+0.5, r+0.5), color='black',
                                    font_size=8, anchor_x='center', anchor_y='center',
                                    parent=self.view_top.scene)
                self._pin_text_visuals.append(pin_text)

        self.view_top.camera = "panzoom"
        self.view_top.camera.set_range(x=(0, IMAGE_SHAPE[1]), y=(0, IMAGE_SHAPE[0]), margin=0)

    def set_image_colormap(self, cmap_name: str):
        print(f"Changing image colormap to {cmap_name}")
        self.image.cmap = cmap_name

    def set_testcase_and_redraw(self, testcase_no: str):
        print(f"Changing test case to {testcase_no}")
        self.funcWrapper.current_testcase = int(testcase_no)
        self.update_image()

    def set_active_layer_and_redraw(self, layer_name: str):
        print(f"Changing active layer to {layer_name}")
        self._active_layer = layer_name
        self.update_image()

    def on_mouse_move(self, event, label):
        scene_coords = self.view_top.scene.transform.imap(event.pos)
        x, y = scene_coords[:2]

        # convert scenecoords to grid coords
        grid_x = int(y)
        grid_y = int(x)

        # Add layer info to display
        layer_info = ""
        if self._active_layer == "Layer 0":
            layer_info = " (Layer 0)"
        elif self._active_layer == "Layer 1":
            layer_info = " (Layer 1)"

        label.setText(f"Grid X: {grid_x}, Grid Y: {grid_y}{layer_info}")

    def on_mouse_press(self, event):
        scene_coords = self.view_top.scene.transform.imap(event.pos)
        x, y = scene_coords[:2]
        # Here you could implement adding pins with layer info


class FunctionalityWrapper:
    pins = []
    grid = []
    nets = []
    previous_paths = []
    previous_pins = []

    current_testcase = 0



    def init_testcase(self):
        self.pins = []
        match self.current_testcase:
            case 0:
                self.grid = [
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
                ]

                self.nets = [
                [(2, 1), (1, 3), (7, 1), (8, 4), (4, 6), (7, 8)],
                [(0,5), (3,8)],
                ]

            case 1:
                self.grid = [
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

                self.nets = [[(2, 1), (6, 2), (12, 2), (6, 10), (2, 14), (12, 12)]]

            case 2:
                self.grid = [
                    [0, -1, 0, 0, 0, 0],
                    [0, -1, 0, -1, 0, 0],
                    [0, 0, 0, 0, -1, -1],
                    [0, 0, -1, 0, 0, 0],
                    [-1, -1, -1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                ]
                self.nets = [[(0, 0), (3, 1), (5, 0), (4, 4), (1, 4)]]

            case 3:
                self.grid = np.zeros((6,6), dtype=int)
                self.nets = [[(0,4), (4,0)]]

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

                self.nets = [[(0,5,5), (0, 0,3), (0, 2, 1)], [(1,4,3)]]





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
