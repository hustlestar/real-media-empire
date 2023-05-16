import video.movie as mv
from config import CONFIG

if __name__ == '__main__':
    import moviepy.config as cfg
    cfg.IMAGEMAGICK_BINARY = CONFIG.get("IMAGEMAGICK_BINARY")

    for i in range(50):
        l = "".join(["W" for _ in range(i + 1)])
        print(f"{i} - {l}")
        clip = mv.build_txt_clip(l, 10000, 5000, 1, 50, (0.5, 0.5), 0, "THEBOLDFONT", color='white')

        print(f"{i} - {clip.w}")
