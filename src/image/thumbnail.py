import os
from PIL import Image, ImageDraw, ImageFont
from enum import Enum

class Position(Enum):
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


def add_text_to_image(image_path,
                      text,
                      font_path=None,
                      font_size=25,
                      font_color=(0, 0, 0),
                      position=Position.BOTTOM_RIGHT):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)

        width, height = img.size

        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()

        textwidth, textheight = draw.textsize(text, font)

        # calculate x,y position
        if position == Position.TOP_LEFT:
            x, y = 0, 0
        elif position == Position.TOP_CENTER:
            x, y = (width - textwidth) / 2, 0
        elif position == Position.TOP_RIGHT:
            x, y = width - textwidth, 0
        elif position == Position.CENTER_LEFT:
            x, y = 0, (height - textheight) / 2
        elif position == Position.CENTER:
            x, y = (width - textwidth) / 2, (height - textheight) / 2
        elif position == Position.CENTER_RIGHT:
            x, y = width - textwidth, (height - textheight) / 2
        elif position == Position.BOTTOM_LEFT:
            x, y = 0, height - textheight
        elif position == Position.BOTTOM_CENTER:
            x, y = (width - textwidth) / 2, height - textheight
        elif position == Position.BOTTOM_RIGHT:
            x, y = width - textwidth, height - textheight

        draw.text((x, y), text, font_color, font=font)
        img.save(os.path.splitext(image_path)[0] + "_with_text.png")