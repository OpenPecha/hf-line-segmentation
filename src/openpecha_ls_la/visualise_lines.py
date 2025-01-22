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


image_path = "/Users/tenkal/Downloads/Image00009_a.jpg"
coordinates = "152,764 179,765 206,769 233,772 260,775 287,773 314,767 314,725 287,731 260,733 233,730 206,727 179,723 152,722"
plot_polygon_on_image(image_path, coordinates)
