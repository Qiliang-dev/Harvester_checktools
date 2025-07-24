import os
import sys
print("System Python path:", sys.base_prefix)
print("Possible tkdnd path:", os.path.join(sys.base_prefix, 'tcl', 'tkdnd2.8'))