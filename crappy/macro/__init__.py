
import os

if 'DISPLAY' in os.environ:
    from .macro import MACRO
    from .pc_macro import PC_MACRO
else:
    pass

