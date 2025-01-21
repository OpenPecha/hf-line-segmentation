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


image_path = "/Users/tenkal/OpenPecha/hf-line-segmentation/data/openpecha_data/images/esukhia_data/0007_image0004a.jpg"
coordinates = "422,304 526,301 630,299 734,298 838,296 942,296 1046,295 1150,295 1254,294 1358,293 1462,293 1566,293 1670,292 1774,290 1878,290 1982,289 2086,287 2190,284 2294,281 2398,279 2502,275 2502,242 2398,246 2294,248 2190,251 2086,254 1982,256 1878,257 1774,257 1670,259 1566,260 1462,260 1358,260 1254,261 1150,262 1046,262 942,263 838,263 734,265 630,266 526,268 422,271"
plot_polygon_on_image(image_path, coordinates)
