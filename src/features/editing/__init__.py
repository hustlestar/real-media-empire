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

__all__ = [
    'BRollInserter',
    'BRollLibrary',
    'BRollClip',
    'BRollInsertion',
    'insert_broll_auto',
    'DynamicEditor',
    'Timeline',
    'TimelineClip',
    'quick_edit'
]
