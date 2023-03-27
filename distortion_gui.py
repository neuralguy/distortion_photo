import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog
import numpy as np
from PIL import Image


def quad_as_rect(quad):
    if quad[0] != quad[2]: return False
    if quad[1] != quad[7]: return False
    if quad[4] != quad[6]: return False
    if quad[3] != quad[5]: return False
    return True


def quad_to_rect(quad):
    assert(len(quad) == 8)
    assert(quad_as_rect(quad))
    return (quad[0], quad[1], quad[4], quad[3])


def rect_to_quad(rect):
    assert(len(rect) == 4)
    return (rect[0], rect[1], rect[0], rect[3], rect[2], rect[3], rect[2], rect[1])


def shape_to_rect(shape):
    assert(len(shape) == 2)
    return (0, 0, shape[0], shape[1])


def griddify(rect, w_div, h_div):
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x_step = w / float(w_div)
    y_step = h / float(h_div)
    y = rect[1]
    grid_vertex_matrix = []
    for _ in range(h_div + 1):
        grid_vertex_matrix.append([])
        x = rect[0]
        for _ in range(w_div + 1):
            grid_vertex_matrix[-1].append([int(x), int(y)])
            x += x_step
        y += y_step
    grid = np.array(grid_vertex_matrix)
    return grid


def distort_grid(org_grid, max_shift):
    new_grid = np.copy(org_grid)
    x_min = np.min(new_grid[:, :, 0])
    y_min = np.min(new_grid[:, :, 1])
    x_max = np.max(new_grid[:, :, 0])
    y_max = np.max(new_grid[:, :, 1])
    new_grid += np.random.randint(- max_shift, max_shift + 1, new_grid.shape)
    new_grid[:, :, 0] = np.maximum(x_min, new_grid[:, :, 0])
    new_grid[:, :, 1] = np.maximum(y_min, new_grid[:, :, 1])
    new_grid[:, :, 0] = np.minimum(x_max, new_grid[:, :, 0])
    new_grid[:, :, 1] = np.minimum(y_max, new_grid[:, :, 1])
    return new_grid


def grid_to_mesh(src_grid, dst_grid):
    assert(src_grid.shape == dst_grid.shape)
    mesh = []
    for i in range(src_grid.shape[0] - 1):
        for j in range(src_grid.shape[1] - 1):
            src_quad = [src_grid[i    , j    , 0], src_grid[i    , j    , 1],
                        src_grid[i + 1, j    , 0], src_grid[i + 1, j    , 1],
                        src_grid[i + 1, j + 1, 0], src_grid[i + 1, j + 1, 1],
                        src_grid[i    , j + 1, 0], src_grid[i    , j + 1, 1]]
            dst_quad = [dst_grid[i    , j    , 0], dst_grid[i    , j    , 1],
                        dst_grid[i + 1, j    , 0], dst_grid[i + 1, j    , 1],
                        dst_grid[i + 1, j + 1, 0], dst_grid[i + 1, j + 1, 1],
                        dst_grid[i    , j + 1, 0], dst_grid[i    , j + 1, 1]]
            dst_rect = quad_to_rect(dst_quad)
            mesh.append([dst_rect, src_quad])
    return mesh


def main(path, output, factor, count):
    im = Image.open(path)
    dst_grid = griddify(shape_to_rect(im.size), count, count)
    src_grid = distort_grid(dst_grid, factor)
    mesh = grid_to_mesh(src_grid, dst_grid)
    im = im.transform(im.size, Image.MESH, mesh)
    if output[-3:] == "jpg" or output[-3:] == "png":
        im.save(output)
    else:
        im.save(f"{output}.jpg")


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Image Distorter'
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 300
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Source image path field
        self.src_label = QLabel('Source Image Path', self)
        self.src_label.move(20, 20)
        self.src_field = QLineEdit(self)
        self.src_field.move(150, 20)
        self.src_field.resize(200, 25)

        # Output field
        self.out_label = QLabel('Output file name', self)
        self.out_label.move(20, 60)
        self.out_field = QLineEdit(self)
        self.out_field.move(150, 60)
        self.out_field.resize(200, 25)

        # Factor field
        self.factor_label = QLabel('Factor', self)
        self.factor_label.move(20, 100)
        self.factor_field = QLineEdit(self)
        self.factor_field.move(150, 100)
        self.factor_field.resize(100, 25)

        # Frequency field
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.move(20, 140)
        self.freq_field = QLineEdit(self)
        self.freq_field.move(150, 140)
        self.freq_field.resize(100, 25)

        # Start button
        self.start_button = QPushButton('Start', self)
        self.start_button.move(150, 200)
        self.start_button.clicked.connect(self.start_button_clicked)

        # File dialog button
        self.file_button = QPushButton('Choose File', self)
        self.file_button.move(20, 200)
        self.file_button.clicked.connect(self.file_button_clicked)

        self.show()

    def start_button_clicked(self):
        try:
            path = self.src_field.text()
            out_path = self.out_field.text()
            factor = int(self.factor_field.text())
            freq = int(self.freq_field.text())
            main(path, out_path, factor, freq)
        except:
            pass

    def file_button_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', '/')
        self.src_field.setText(file_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
