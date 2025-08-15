import sys, pygame, locale, os
from json import loads
pygame.init()

def get_value(name, default):
    try:
        index = sys.argv.index(f"--{name}")
        return sys.argv[index+1]
    except ValueError:
        return default

def get(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

VERSION = '0.0.2'
SCRAEEN_SCALE = pygame.display.get_desktop_sizes()[0][0] / 1920
ASPECT_RATIO = [int(i) for i in (get_value("aspectratio", "16:9")).split(":")]
REAL_WIDTH = int(get_value("width", 1200 * SCRAEEN_SCALE))
REAL_HEIGHT = int(get_value("height", 900 * SCRAEEN_SCALE))
W_LIMIT = (REAL_WIDTH/REAL_HEIGHT) > (ASPECT_RATIO[0]/ASPECT_RATIO[1])
WINDOW_WIDTH = (REAL_HEIGHT*(ASPECT_RATIO[0]/ASPECT_RATIO[1]) if W_LIMIT else REAL_WIDTH)
WINDOW_HEIGHT = REAL_HEIGHT
RESOURCE_PATH = get_value("resource", ".\\Resources")
X_OFFSET = ((REAL_WIDTH-WINDOW_WIDTH)/2 if W_LIMIT else 0)
LINE_WIDTH = 5.76 * WINDOW_HEIGHT
LINE_HEIGHT = 0.0075 * WINDOW_HEIGHT
X = WINDOW_WIDTH * 0.05625
Y = WINDOW_HEIGHT * 0.6
NOTE_WIDTH = WINDOW_WIDTH * 0.123
NOTE_SCALE = NOTE_WIDTH / 989
HOLD_YSCALE = 1 / 1900
HOLD_HL_YSCALE = 1 / 1854
HOLD_HL_SCALE = NOTE_WIDTH / 966
LINE_COLOR = (0.996, 1, 0.663)
HIT_COLOR = (1, 0.925, 0.627)
HIT_COLOR_GOOD = (0.7059, 0.882, 1)
HIT_WIDTH = NOTE_WIDTH * 1.576
HIT_SCALE = HIT_WIDTH / 256
PARTICLE_COLOR = HIT_COLOR
WIDTH_SCALE = WINDOW_WIDTH / 800
HEIGHT_SCALE = WINDOW_HEIGHT / 600
PARTICLE_SIZE = 17.5 * WIDTH_SCALE
RPE_LINE_WIDTH = WINDOW_WIDTH * (4000 / 1350)
RPE_LINE_HEIGHT = WINDOW_HEIGHT * (5 / 900)
LINE_COLOR_GOOD = (0.6353, 0.9333, 1)
FONT_SIZE = 75
FONT = pygame.font.Font(f"{RESOURCE_PATH}\\fonts\\font.ttf", FONT_SIZE)
try:
    EMOJI_FONT = pygame.font.SysFont("segoeuiemoji", FONT_SIZE)
except:
    EMOJI_FONT = FONT
TEXT_HEIGHT = WINDOW_HEIGHT * 0.0484#0.0555
TEXT_SCALE = TEXT_HEIGHT / FONT_SIZE
if "--render" in sys.argv:
    PAINT_SPACE = 0
else:
    PAINT_SPACE = 0.02
LINE_TEXTURE_SCALE = WINDOW_WIDTH / 1350
RPE_TEXTURE_COLOR = [1, 1, 1]
RPE_TEXT_COLOR = [1, 1, 1]
CAPTION = "PyPhiRenderer"
LAUNCHER_WIDTH = int(get_value("width", 1200 * SCRAEEN_SCALE))
LAUNCHER_HEIGHT = int(get_value("height", 900 * SCRAEEN_SCALE))
LANGUAGE = ("zh_CN" if locale.getdefaultlocale()[0] not in os.listdir(".\\locales\\") else locale.getdefaultlocale()[0])
_locales = {}
for i in os.listdir(f".\\locales\\{LANGUAGE}\\"):
    _locales[i.split(".")[0]] = loads(get(f".\\locales\\{LANGUAGE}\\{i}"))
LOCALES = _locales
AUTOPLAY = not ("--noautoplay" in sys.argv)