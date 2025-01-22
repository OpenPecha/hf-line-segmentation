import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.patches import Polygon


def plot_polygon_on_image(image_path, coordinates):
    img = Image.open(image_path)
    width, height = img.size

    points = [tuple(map(int, point.split(','))) for point in coordinates.split()]

    fig, ax = plt.subplots()
    ax.imshow(img)
    polygon = Polygon(points, closed=True, edgecolor='red', fill=False, linewidth=2)
    ax.add_patch(polygon)

    for x, y in points:
        ax.plot(x, y, 'ro')

    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    plt.axis('off')
    plt.show()


image_path = "/Users/tenkal/Downloads/002.png"
coordinates = "1803,56 1804,48 1802,39 1807,26 1819,28 1827,37 1902,35 1910,27 1933,25 1946,34 1968,33 1975,24 1984,25 1988,35 2022,35 2026,24 2038,26 2041,35 2065,35 2064,59 2044,59 2035,73 2028,71 2024,64 1996,67 1986,74 1980,69 1948,71 1931,74 1925,66 1908,66 1847,65 1838,77 1830,65 1810,61"
plot_polygon_on_image(image_path, coordinates)
