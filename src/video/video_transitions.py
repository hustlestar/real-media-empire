from moviepy.video.compositing.transitions import *


def fadeinout(clip1, clip2, duration):
    """
    Fades in clip2 over duration, then fades out clip1 over duration.
    """
    return CompositeVideoClip([clip1.fadeout(duration), clip2.fadein(duration)])


def crossfade(clip1, clip2, duration):
    """
    Cross-fades between clip1 and clip2 over duration.
    """
    return clip1.crossfadein(clip2, duration)


def slideleft(clip1, clip2, duration):
    """
    Slides clip2 from right to left over duration to replace clip1.
    """
    return CompositeVideoClip([clip1, clip2.set_position(("right", "top")).slide_in("left", duration)])


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


TRANSITIONS = {
    "fadeinout": fadeinout,
    "crossfade": crossfade,
    "slideleft": slideleft,
    "slideright": slideright,
    "slideup": slideup,
    "slidedown": slidedown,
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

# Example usage
from moviepy.editor import VideoFileClip

clip1 = VideoFileClip("clip1.mp4")
clip2 = VideoFileClip("clip2.mp4")

# Apply transition between clips
transition = TRANSITIONS["iris"](clip1, clip2, duration=1)
final_clip = clip1.fx(transition)

final_clip.write_videofile("output.mp4")
