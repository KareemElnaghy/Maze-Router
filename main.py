from vispy.app import use_app
from Visualizer.visualizer import MyMainWindow

if __name__ == "__main__":
    app = use_app("pyqt6")
    app.create()
    win = MyMainWindow()
    win.show()
    app.run()
