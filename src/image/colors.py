import colorgram
import requests
from colorgram.colorgram import Rgb


def get_image_main_colors(image, number_of_colors=10):
    colors = colorgram.extract(image, number_of_colors)  # Extract 10 colors from the image
    main_colors = [color.rgb for color in colors]  # Get the RGB values of the extracted colors
    print(f"Top {number_of_colors} image colors: {main_colors}")
    return main_colors


def map_color_to_category(color: Rgb):
    r, g, b = color.r, color.g, color.b
    if r >= 220 and g >= 220 and b >= 220:
        return "White"
    elif r >= 190 and g <= 50 and b <= 50:
        return "Red"
    elif r <= 50 and g >= 190 and b <= 50:
        return "Green"
    elif r >= 220 and g >= 220 and b <= 50:
        return "Yellow"
    elif r >= 120 and r <= 190 and g >= 120 and g <= 190 and b >= 120 and b <= 190:
        return "Grey"
    elif r >= 90 and r <= 190 and g >= 40 and g <= 90 and b <= 40:
        return "Brown"
    elif r >= 220 and g >= 100 and g <= 180 and b <= 50:
        return "Orange"
    elif r >= 180 and r <= 255 and g >= 120 and g <= 180 and b <= 50:
        return "Gold"
    elif r >= 160 and r <= 190 and g >= 160 and g <= 190 and b >= 160 and b <= 190:
        return "Silver"
    elif r <= 50 and g <= 50 and b <= 50:
        return "Black"
    elif r >= 170 and r <= 220 and g == 255 and b >= 170 and b <= 220:
        return "Mint"
    elif r <= 50 and g <= 50 and b >= 190:
        return "Blue"
    elif r >= 90 and r <= 190 and g <= 40 and b >= 90 and b <= 190:
        return "Purple"
    elif r <= 50 and g >= 190 and b >= 190:
        return "Cyan"
    elif r >= 190 and g <= 50 and b >= 190:
        return "Magenta"
    else:
        return "Other"


if __name__ == '__main__':
    colors = get_image_main_colors(requests.get('http://images.cocodataset.org/val2017/000000039769.jpg', stream=True).raw)

    for color in colors:
        category = map_color_to_category(color)
        print(category)
