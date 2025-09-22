from enum import Enum


class ReferenceMode(Enum):
    WINNER = 1
    ME = 2


class SelectionMode(Enum):
    ALL = -1
    FIVE = 5
    SEVEN = 7
    NINE = 9


class DeltaOptions:

    def __init__(self, maxSeconds: int, showRealName: bool, showDiscDisq: bool, referenceMode: ReferenceMode, selectionMode: SelectionMode):
        self.maxSeconds = maxSeconds
        self.showRealName = showRealName
        self.showDiscDisq = showDiscDisq
        self.referenceMode = referenceMode
        self.selectionMode = selectionMode
        # selection mode - enter driver numbers for selection instead?
        # reference mode - number based?
