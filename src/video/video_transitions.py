from typing import List

from moviepy.editor import *
from moviepy.video.compositing.transitions import *


def first_fade_out_second_fade_in(clip1: VideoClip, clip2, duration):
    return concatenate_videoclips(
        [
            clip1.subclip(0, clip1.duration - duration),
            clip1.subclip(clip1.duration - duration).fx(vfx.fadeout, duration),
            clip2.subclip(0, duration).fx(vfx.fadein, duration),
            clip2.subclip(duration),
        ]
    )


def first_fade_out_second_fade_in_all(clips: List[VideoClip], duration):
    result = []
    for i, clip in enumerate(clips):
        if not i:
            result.append(clip.subclip(0, clip.duration - duration))
            result.append(clip.subclip(clip.duration - duration).fx(vfx.fadeout, duration))
        else:
            result.append(clip.subclip(0, duration).fx(vfx.fadein, duration))
            result.append(clip.subclip(duration, clip.duration - duration))
            result.append(clip.subclip(clip.duration - duration).fx(vfx.fadeout, duration))
    return concatenate_videoclips(result)


def first_fade_out_all(clips: List[VideoClip], duration):
    result = []
    for i, clip in enumerate(clips):
        result.append(clip.subclip(0, clip.duration - duration))
        result.append(clip.subclip(clip.duration - duration).fx(vfx.fadeout, duration))
    return concatenate_videoclips(result)


def first_fade_in_all(clips: List[VideoClip], duration):
    result = []
    for i, clip in enumerate(clips):
        result.append(clip.subclip(0, duration).fx(vfx.fadein, duration))
        result.append(clip.subclip(duration))
    return concatenate_videoclips(result)


def first_fade_out(clip1: VideoClip, clip2: VideoClip, duration):
    """
    Fades in clip2 over duration, then fades out clip1 over duration.
    """
    return CompositeVideoClip([clip1.subclip(0, clip1.duration - duration), clip1.subclip(clip1.duration - duration).fadeout(duration), clip2])


def fadeinout(clip1, clip2, duration):
    """
    Fades in clip2 over duration, then fades out clip1 over duration.
    """
    return CompositeVideoClip([fadeout(clip1, duration), fadein(clip2, duration)])


def slide_in_left_all(clips: List[VideoClip], duration=3):
    """
    Slides from right to left over duration to replace clip1.
    """
    return slide_in_to_all(clips, duration)


def slide_in_top_all(clips: List[VideoClip], duration=2):
    """
    Slides from right to left over duration to replace clip1.
    """
    return slide_in_to_all(clips, duration, side="top")


def slide_in_bottom_all(clips: List[VideoClip], duration=2):
    """
    Slides from right to left over duration to replace clip1.
    """
    return slide_in_to_all(clips, duration, side="bottom")


def slide_in_to_all(clips, duration, side="left"):
    slided_clips = []
    for i, clip in enumerate(clips):
        if not i:
            slided_clips.append(clip)
        else:
            slided_clips.append(CompositeVideoClip([clip.fx(transfx.slide_in, duration=duration, side=side)]))
    return concatenate_videoclips(slided_clips, method="compose", padding=-1 * duration)


def slideleft(clip1, clip2, duration):
    """
    Slides clip2 from right to left over duration to replace clip1.
    """

    return CompositeVideoClip([slide_out(clip1, duration, "left"), slide_in(clip2, duration, "right")])


def slideright(clip1, clip2, duration):
    """
    Slides clip2 from left to right over duration to replace clip1.
    """
    return CompositeVideoClip([clip1, clip2.set_position(("left", "top")).slide_in("right", duration)])


def slideup(clip1, clip2, duration):
    """
    Slides clip2 from bottom to top over duration to replace clip1.
    """
    return CompositeVideoClip([clip1, clip2.set_position(("center", "bottom")).slide_in("top", duration)])


def slidedown(clip1, clip2, duration):
    """
    Slides clip2 from top to bottom over duration to replace clip1.
    """
    return CompositeVideoClip([clip1, clip2.set_position(("center", "top")).slide_in("bottom", duration)])


def dissolve(clip1, clip2, duration):
    return DissolveTransition(clip1, clip2, duration=duration)


def diagonal(clip1, clip2, duration):
    return Diagonal(clip1, clip2, duration=duration)


def iris(clip1, clip2, duration):
    return IrisTransition(clip1, clip2, duration=duration)


def mask(clip1, clip2, duration):
    return MaskTransition(clip1, clip2, duration=duration)


def slide(clip1, clip2, duration):
    return SlideTransition(clip1, clip2, duration=duration)


def vslide(clip1, clip2, duration):
    return VerticalSlideTransition(clip1, clip2, duration=duration)


def hslide(clip1, clip2, duration):
    return HorizontalSlideTransition(clip1, clip2, duration=duration)


def circle(clip1, clip2, duration):
    return Circle(clip1, clip2, duration=duration)


def pixelize(clip1, clip2, duration):
    return PixelizeTransition(clip1, clip2, duration=duration)


def rotate(clip1, clip2, duration):
    return Rotate(clip1, clip2, duration=duration)


def zoomin(clip1, clip2, duration):
    return ZoomInTransition(clip1, clip2, duration=duration)


def zoomout(clip1, clip2, duration):
    return ZoomOutTransition(clip1, clip2, duration=duration)


def warp(clip1, clip2, duration):
    return WarpIn(clip1, clip2, duration=duration)


TRANSITIONS_BETWEEN_TWO = {
    "first_fade_out_second_fade_in": first_fade_out_second_fade_in,
    "fadeinout": fadeinout,
    "slideleft": slideleft,
    "slideright": slideright,
    "slideup": slideup,
    "slidedown": slidedown,
    "first_fade_out": first_fade_out,
    # "dissolve": dissolve,
    # "diagonal": diagonal,
    # "iris": iris,
    # "mask": mask,
    # "slide": slide,
    # "vslide": vslide,
    # "hslide": hslide,
    # "circle": circle,
    # "pixelize": pixelize,
    # "rotate": rotate,
    # "zoomin": zoomin,
    # "zoomout": zoomout,
    # "warp": warp
}

TRANSITIONS_FOR_LIST = {
    first_fade_out_second_fade_in_all.__name__: first_fade_out_second_fade_in_all,
    first_fade_out_all.__name__: first_fade_out_all,
    first_fade_in_all.__name__: first_fade_in_all,
    slide_in_left_all.__name__: slide_in_left_all,
    slide_in_top_all.__name__: slide_in_top_all,
    slide_in_bottom_all.__name__: slide_in_bottom_all,
}

DEFAULT_TRANSITION = fadeinout
