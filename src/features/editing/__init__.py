"""Advanced editing features"""

from .broll_insertion import (
    BRollInserter,
    BRollLibrary,
    BRollClip,
    BRollInsertion,
    insert_broll_auto
)
from .dynamic_editor import (
    DynamicEditor,
    Timeline,
    TimelineClip,
    quick_edit
)
from .post_production import (
    PostProductionPipeline,
    ColorGrade,
    AudioMix,
    quick_post_production
)

__all__ = [
    'BRollInserter',
    'BRollLibrary',
    'BRollClip',
    'BRollInsertion',
    'insert_broll_auto',
    'DynamicEditor',
    'Timeline',
    'TimelineClip',
    'quick_edit',
    'PostProductionPipeline',
    'ColorGrade',
    'AudioMix',
    'quick_post_production'
]
