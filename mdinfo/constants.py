"""Constants used by various mdinfo modules"""

import time

APP_NAME = "mdinfo"

# sentinel value to determine if a template did not match a field
NONE_STR_SENTINEL = f"__XYZZY_{APP_NAME}_{time.time()}_TEMPLATE_NONE_XYZZY__"

# default value to use for none string in template
NONE_STR_DEFAULT = "_"

# default values for string manipulation template options
INPLACE_DEFAULT = ","
