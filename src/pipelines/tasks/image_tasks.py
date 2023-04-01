import os
import random

from config import CONFIG
from image.colors import get_image_main_colors
from image.thumbnail import add_text_to_image, TextPosition
from pipelines.tasks import DEFAULT_ORIENTATION


class ImageTasks:
    def __init__(
            self,
            thumbnail_background_colors,
            thumbnail_fonts_dir,
            results_dir=None
    ):
        self.thumbnail_background_colors = thumbnail_background_colors
        self.thumbnail_fonts_dir = thumbnail_fonts_dir
        self.results_dir = results_dir

    def create_thumbnail(self, title: str):
        image_path = self.find_matching_image()
        result_image = os.path.join(self.results_dir, f"5_thumbnail.jpg")
        all_groups = split_string_into_three_groups_max(title)

        fonts = [os.path.join(self.thumbnail_fonts_dir, f) for f in os.listdir(self.thumbnail_fonts_dir) if f.endswith('.ttf')]
        font = fonts[random.randint(0, len(fonts) - 1)]

        if len(all_groups) == 2:
            add_text_to_image(
                image_path,
                result_image,
                text=all_groups[0],
                font_path=font,
                font_size=300 if len(all_groups[0]) < 12 else 200,
                font_color=(255, 255, 255),
                position=TextPosition.TOP_CENTER
            )
            add_text_to_image(
                result_image,
                result_image,
                text=all_groups[1],
                font_path=font,
                font_size=300 if len(all_groups[1]) < 12 else 200,
                font_color=(255, 255, 255),
                position=TextPosition.BOTTOM_CENTER
            )
        elif len(all_groups) == 3:
            add_text_to_image(
                image_path,
                result_image,
                text=all_groups[0],
                font_path=font,
                font_size=250 if len(all_groups[0]) < 12 else 180,
                font_color=(255, 255, 255),
                position=TextPosition.TOP_CENTER
            )
            add_text_to_image(
                result_image,
                result_image,
                text=all_groups[1],
                font_path=font,
                font_size=250 if len(all_groups[1]) < 12 else 180,
                font_color=(255, 255, 255),
                position=TextPosition.CENTER
            )
            add_text_to_image(
                result_image,
                result_image,
                text=all_groups[2],
                font_path=font,
                font_size=250 if len(all_groups[2]) < 12 else 180,
                font_color=(255, 255, 255),
                position=TextPosition.BOTTOM_CENTER
            )
        return result_image

    def find_matching_image(self):
        photo_dir = os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'), 'PHOTO', DEFAULT_ORIENTATION, 'large2x')
        photos = [os.path.join(photo_dir, f) for f in os.listdir(photo_dir) if f.endswith('.jpg')]
        while True:
            random_photo = photos[random.randint(0, len(photos) - 1)]
            colors = get_image_main_colors(raw_image=random_photo, number_of_colors=6)
            if any(color in ['white', 'silver', 'gray'] for color in colors):
                continue
            if any(color in self.thumbnail_background_colors for color in colors):
                return random_photo

def split_string_into_three_groups_max(s):
    words = s.split()
    n = len(words)
    if n <= 3:
        return words
    avg = n // 3
    remainder = n % 3
    groups = []
    i = 0
    while i < n:
        group_size = avg + (1 if remainder > 0 else 0)
        groups.append(" ".join(words[i:i+group_size]))
        i += group_size
        remainder -= 1
    return groups


if __name__ == '__main__':
    print(split_string_into_three_groups_max("small test sss ewrewr qw w"))