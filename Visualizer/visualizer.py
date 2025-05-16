import numpy as np
from PyQt6 import QtWidgets

from Visualizer.funcWrapper import FunctionalityWrapper
from Visualizer.utils import Utils

from vispy.scene import SceneCanvas, visuals
from vispy.visuals.transforms import STTransform

from concurrent.futures import ThreadPoolExecutor
import time

CANVAS_SIZE = (1000, 1000)  # (width, height)
COLORMAP_CHOICES = ["viridis", "hot", "grays", "reds", "blues"]
LAYER_CHOICES = ["Layer 0", "Layer 1", "Combined"]
TESTCASE_CHOICES = ["0", "1", "2", "3", "4", "5", "User Input"]

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
    _active_layer : int = 0
    _overlayed_image = None
    _chosen_cmap = COLORMAP_CHOICES[0]

    _layer_0_vg = None
    _layer_1_vg = None

    executor = ThreadPoolExecutor(max_workers=2)
    _routing_lock = False

    _image_shape = (100,100)

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
            cmap=self._chosen_cmap,
            parent=self.view_top.scene,
        )

        self.view_top.camera = "panzoom"
        self._pin_text_visuals = []

        self.funcWrapper.current_testcase = 0
        self.update_image()

    def show_combined_view(self, pins):
        self._image_shape = self._layer_0_vg.shape
        self.clear_pins_text()
        self.show_pins_text(pins)

        #self.view_top.camera = "panzoom"
        self.view_top.camera.set_range(x=(0, self._image_shape[1]), y=(0, self._image_shape[0]), margin=0)

        self.image.set_data(self._layer_0_vg)
        self.image.order = 0

        self._overlayed_image = visuals.Image(
            self._layer_1_vg,
            texture_format="auto",
            interpolation="nearest",
            cmap=self._chosen_cmap,
            parent=self.view_top.scene,
        )
        self._overlayed_image.order = 1  # draw the overlayed image second

        # configure opengl blend mode for proper compositing
        self._overlayed_image.opacity = 0.8
        self._overlayed_image.set_gl_state('translucent', depth_test=False, cull_face=False, blend=True,
                                          blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_single_view_routing_complete_callback(self, future):
        image_data = future.result()
        self.funcWrapper.current_layer_displayed = self._active_layer
        pins = self.funcWrapper.pins

        self._image_shape = image_data.shape

        self.clear_pins_text()
        self.show_pins_text(pins)

        #self.view_top.camera = "panzoom"
        self.view_top.camera.set_range(x=(0, self._image_shape[1]), y=(0, self._image_shape[0]), margin=0)

        self.image.set_data(image_data)
        self._routing_lock = False

    def on_combined_view_routing_complete_callback(self, future, finish : bool, task_id :str):
        print(task_id)
        if not finish:
            self._layer_0_vg = future.result()
            pins =  self.funcWrapper.pins
        else:
            self._layer_1_vg = future.result()
            pins =  self.funcWrapper.pins
            self.show_combined_view(pins)

        self._routing_lock = False

    def show_single_view(self):
        print("Main application: Submitting single view layer...")
        future = self.executor.submit(self.funcWrapper.update_grid)
        future.add_done_callback(lambda f: self.on_single_view_routing_complete_callback(f))

    def update_image(self):
        if self._overlayed_image is not None:
            self._overlayed_image.parent = None
            self._overlayed_image = None

        # have funcWrapper update its member attributes
        self.funcWrapper.init_testcase()

        # if it is Combined view get the two visual grids of our layers and pass it to show_combined view
        # Do not render if the grid is not multilayer and tries accessing other layer
        # Ideally we should lock the choices in the UI using QT but whatever this is Q&D
        if not self._routing_lock and self.funcWrapper.multiLayer:
            self._routing_lock = True
            if self._active_layer == -1:
                print("Main application: Submitting Layer 0 Task")
                self.funcWrapper.current_layer_displayed = 0
                future_layer_0 = self.executor.submit(self.funcWrapper.update_grid)
                future_layer_0.add_done_callback(lambda f: self.on_combined_view_routing_complete_callback(f, False, "Layer 0 done"))

                print("Main application: Submitting Layer 1 Task")
                self.funcWrapper.current_layer_displayed = 1
                future_layer_1 = self.executor.submit(self.funcWrapper.update_grid)
                future_layer_1.add_done_callback(lambda f: self.on_combined_view_routing_complete_callback(f, True, "Layer 1 done"))
            else:
                print("Main application: Submitting single view layer...")
                self.funcWrapper.current_layer_displayed = self._active_layer
                future = self.executor.submit(self.funcWrapper.update_grid)
                future.add_done_callback(lambda f: self.on_single_view_routing_complete_callback(f))
        elif not self._routing_lock:
            self._routing_lock = True
            print("Main application: Submitting single view layer...")
            future = self.executor.submit(self.funcWrapper.update_grid)
            future.add_done_callback(lambda f: self.on_single_view_routing_complete_callback(f))
            #    return
            #self.show_single_view()

    def clear_pins_text(self):
        for visual in self._pin_text_visuals:
            visual.parent = None
        self._pin_text_visuals = []

    def show_pins_text(self, pins):
        for i, pin in enumerate(pins):
            r, c = pin
            pin_text = visuals.Text(f'P{r},{c}', pos=(c+0.5, r+0.5), color='black',
                                font_size=8, anchor_x='center', anchor_y='center',
                                parent=self.view_top.scene)
            pin_text.order = 1
            self._pin_text_visuals.append(pin_text)

    def set_image_colormap(self, cmap_name: str):
        print(f"Changing image colormap to {cmap_name}")
        self._chosen_cmap = cmap_name
        self.image.cmap = cmap_name
        if self._overlayed_image is not None:
            self._overlayed_image.cmap = cmap_name

    def refresh_images(self):
        self.image.update()
        if self._overlayed_image is not None:
            self._overlayed_image.update()

    def set_testcase_and_redraw(self, testcase_no: str):
        print(f"Changing test case to {testcase_no}")
        self.funcWrapper.current_testcase = Utils.testcase_name_to_int(testcase_no)
        self.update_image()

    def set_active_layer_and_redraw(self, layer_name: str):
        print(f"Changing active layer to {layer_name}")
        self._active_layer = Utils.layer_name_to_int(layer_name)
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
