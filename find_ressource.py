import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):  # PyInstaller compatibility (not used by Nuitka)
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(sys.argv[0])  # Path to the executable or script
    return os.path.join(base_path, relative_path)