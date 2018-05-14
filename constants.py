# edge
NONE = 'none'
RISING = 'rising'
FALLING = 'falling'
BOTH = 'both'

# value
HIGH = 1
LOW = 0

# direction
INPUT = 'in'
OUTPUT = 'out'


import re
class _sunxi():
    def __getitem__(self, pin):
        rst = re.findall(r"P([A-Z])(\d+)", str(pin))
        if not rst:
            raise RuntimeError('pin name {} not supported!'.format(pin))
        return 32*(ord(rst[0][0])-65) + int(rst[0][1])

# pin mapping
BOARD_SUNXI = _sunxi()

BOARD_NANO_PI = {}

BOARD_ORANGE_PI_PC = {}