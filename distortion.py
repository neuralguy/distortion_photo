import numpy as np
from PIL import Image


def quad_as_rect(quad):
    # Проверка, является ли четырёхугольник прямоугольником
    return quad[0] == quad[2] and quad[1] == quad[7] and quad[4] == quad[6] and quad[3] == quad[5]


def quad_to_rect(quad):
    # Преобразование координат четырёхугольника в координаты прямоугольника
    if len(quad) != 8 or not quad_as_rect(quad):
        raise ValueError("Некорректные координаты четырёхугольника")
    return quad[0], quad[1], quad[4], quad[3]


def rect_to_quad(rect):
    # Преобразование координат прямоугольника в координаты четырёхугольника
    if len(rect) != 4:
        raise ValueError("Некорректные координаты прямоугольника")
    return rect[0], rect[1], rect[0], rect[3], rect[2], rect[3], rect[2], rect[1]


def shape_to_rect(shape):
    # Получение координат прямоугольника на основе размеров
    if len(shape) != 2:
        raise ValueError("Некорректные размеры")
    return 0, 0, shape[0], shape[1]


def griddify(rect, w_div, h_div):
    # Создание сетки на основе размеров прямоугольника
    x_step = np.linspace(rect[0], rect[2], w_div + 1)
    y_step = np.linspace(rect[1], rect[3], h_div + 1)
    return np.dstack(np.meshgrid(x_step, y_step)).astype(int)


def distort_grid(org_grid, max_shift):
    # Добавление искажений к сетке
    return np.clip(org_grid + np.random.randint(-max_shift, max_shift + 1, org_grid.shape), np.min(org_grid), np.max(org_grid))


def grid_to_mesh(src_grid, dst_grid):
    if src_grid.shape != dst_grid.shape:
        raise ValueError("Сетки имеют разные размеры")
    
    mesh = []
    for i in range(src_grid.shape[0] - 1):
        for j in range(src_grid.shape[1] - 1):
            src_quad = [src_grid[i, j, 0], src_grid[i, j, 1],
                        src_grid[i + 1, j, 0], src_grid[i + 1, j, 1],
                        src_grid[i + 1, j + 1, 0], src_grid[i + 1, j + 1, 1],
                        src_grid[i, j + 1, 0], src_grid[i, j + 1, 1]]
            
            dst_quad = [dst_grid[i, j, 0], dst_grid[i, j, 1],
                        dst_grid[i + 1, j, 0], dst_grid[i + 1, j, 1],
                        dst_grid[i + 1, j + 1, 0], dst_grid[i + 1, j + 1, 1],
                        dst_grid[i, j + 1, 0], dst_grid[i, j + 1, 1]]
            
            if quad_as_rect(dst_quad):  # Убедимся, что dst_quad это прямоугольник
                dst_rect = quad_to_rect(dst_quad)
                mesh.append([dst_rect, src_quad])
            else:
                raise ValueError("Получившийся четырехугольник не является прямоугольником")
    return mesh


def distorize(path, factor=200, frequency=5, output="result.jpg", seed=None):
    if seed is not None:
        np.random.seed(seed)
    # Искажение изображения
    im = Image.open(path)
    dst_grid = griddify(shape_to_rect(im.size), frequency, frequency)
    src_grid = distort_grid(dst_grid, factor)
    mesh = grid_to_mesh(src_grid, dst_grid)
    im = im.transform(im.size, Image.MESH, mesh)
    output_path = output or path
    im.save(output_path)


if __name__ == "__main__":
    path = "/home/timon/Изображения/My/kate.jpg"
    factor = 100
    frequency = 10
    distorize(path, factor, frequency, seed=69)
