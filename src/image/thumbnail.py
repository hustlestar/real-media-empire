from enum import Enum

from PIL import Image, ImageDraw, ImageFont


class TextPosition(Enum):
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


def calculate_text_position(image_width, image_height, text_width, text_height, position):
    if position == TextPosition.TOP_LEFT:
        x = int(image_width * 0.1)
        y = int(image_height * 0.1)
    elif position == TextPosition.TOP_CENTER:
        x = int((image_width - text_width) / 2)
        y = int(image_height * 0.1)
    elif position == TextPosition.TOP_RIGHT:
        x = int(image_width * 0.9 - text_width)
        y = int(image_height * 0.1)
    elif position == TextPosition.CENTER_LEFT:
        x = int(image_width * 0.1)
        y = int((image_height - text_height) / 2)
    elif position == TextPosition.CENTER:
        x = int((image_width - text_width) / 2)
        y = int((image_height - text_height) / 2)
    elif position == TextPosition.CENTER_RIGHT:
        x = int(image_width * 0.9 - text_width)
        y = int((image_height - text_height) / 2)
    elif position == TextPosition.BOTTOM_LEFT:
        x = int(image_width * 0.1)
        y = int(image_height * 0.9 - text_height)
    elif position == TextPosition.BOTTOM_CENTER:
        x = int((image_width - text_width) / 2)
        y = int(image_height * 0.9 - text_height)
    elif position == TextPosition.BOTTOM_RIGHT:
        x = int(image_width * 0.9 - text_width)
        y = int(image_height * 0.9 - text_height)
    return x, y


def add_text_to_image(input_image_path, output_image_path, text, font_path, font_size, font_color, position):
    with Image.open(input_image_path) as img:
        # calculate text dimensions
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = font.getsize(text)
        # calculate text position
        text_x, text_y = calculate_text_position(img.width, img.height, text_width, text_height, position)
        # add text to image
        draw = ImageDraw.Draw(img)
        draw.text((text_x, text_y), text, font=font, fill=font_color)
        # img.show()
        img.save(output_image_path)


if __name__ == "__main__":
    add_text_to_image(
        "E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\1121477.jpg",
        "E:\MEDIA_GALLERY\\THUMBNAILS\\1121477.jpg",
        "POWER",
        "E:\\MEDIA_GALLERY\\FONTS\\LeagueSpartan-ExtraBold.ttf",
        300,
        (255, 255, 255),
        TextPosition.TOP_CENTER,
    )

    add_text_to_image(
        "E:\MEDIA_GALLERY\\THUMBNAILS\\1121477.jpg",
        "E:\MEDIA_GALLERY\\THUMBNAILS\\1121477.jpg",
        "OF",
        "E:\\MEDIA_GALLERY\\FONTS\\LeagueSpartan-ExtraBold.ttf",
        300,
        (255, 255, 255),
        TextPosition.CENTER,
    )

    add_text_to_image(
        "E:\MEDIA_GALLERY\\THUMBNAILS\\1121477.jpg",
        "E:\MEDIA_GALLERY\\THUMBNAILS\\1121477.jpg",
        "HABIT",
        "E:\\MEDIA_GALLERY\\FONTS\\LeagueSpartan-ExtraBold.ttf",
        300,
        (255, 255, 255),
        TextPosition.BOTTOM_CENTER,
    )
