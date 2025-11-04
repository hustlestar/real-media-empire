import colorgram
import requests
from colorgram.colorgram import Rgb
from PIL import Image
import logging

logger = logging.getLogger(__name__)

color_map = {
    (255, 255, 255): "white",
    (0, 0, 0): "black",
    (255, 0, 0): "red",
    (0, 128, 0): "green",
    (0, 0, 255): "blue",
    (255, 255, 0): "yellow",
    (128, 128, 128): "gray",
    (255, 192, 203): "pink",
    (255, 0, 255): "magenta",
    (255, 215, 0): "gold",
    (192, 192, 192): "silver",
    (189, 252, 201): "mint",
    (255, 165, 0): "orange",
    (165, 42, 42): "brown",
    (0, 255, 255): "cyan",
    (245, 245, 220): "beige",
    (128, 128, 0): "olive",
    (0, 128, 128): "teal",
    (128, 0, 0): "maroon",
    (0, 0, 128): "navy",
    (75, 0, 130): "indigo",
    (255, 218, 185): "peach",
    (255, 127, 80): "coral",
    (64, 224, 208): "turquoise",
}


def get_image_main_colors_raw(image, number_of_colors=6):
    colors = colorgram.extract(image, number_of_colors)  # Extract 10 colors from the image
    main_colors = [color.rgb for color in colors]  # Get the RGB values of the extracted colors
    logger.debug(f"Top {number_of_colors} image colors: {main_colors}")
    return main_colors


def get_image_main_colors_ndarray(image_ndarray, number_of_colors=6):
    main_colors = get_image_main_colors_raw(Image.fromarray(image_ndarray), number_of_colors)
    return [map_rgb_to_human(f) for f in main_colors]


def get_image_main_colors(raw_image=None, image_ndarray=None, number_of_colors=6):
    if raw_image is None and image_ndarray is None:
        raise
    if raw_image:
        image = Image.open(raw_image)
    else:
        image = Image.fromarray(image_ndarray)
    main_colors = get_image_main_colors_raw(image, number_of_colors)
    return [map_rgb_to_human(f) for f in main_colors]


def map_rgb_to_human(color: Rgb):
    # Map each color to a basic color
    rgb = color
    if rgb in color_map:
        return color_map[rgb]
    else:
        # If no exact match is found, choose the closest basic color using Euclidean distance
        closest_color = min(color_map, key=lambda c: ((c[0] - rgb[0]) ** 2 + (c[1] - rgb[1]) ** 2 + (c[2] - rgb[2]) ** 2) ** 0.5)
        return color_map[closest_color]


if __name__ == "__main__":
    colors = get_image_main_colors(requests.get("http://images.cocodataset.org/val2017/000000039769.jpg", stream=True).raw)

    for color in colors:
        category = map_rgb_to_human(color)
        print(category)
