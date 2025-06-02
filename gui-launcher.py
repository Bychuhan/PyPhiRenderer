import pygame, subprocess, win32gui, err_hook, time, requests, os
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
from texture import *
from PIL import Image, ImageFilter, ImageEnhance
from tkinter.filedialog import askopenfilename
from const import *
from func import *
from parse_chart import *
from rpe_easings import *

_wscale = LAUNCHER_WIDTH / 1200
_hscale = LAUNCHER_HEIGHT / 900

TIP_TEXT_SCALE = 0.5 * _hscale

os.environ["SDL_IME_SHOW_UI"] = "1"

pygame.init()
window = pygame.display.set_mode((LAUNCHER_WIDTH, LAUNCHER_HEIGHT), flags = DOUBLEBUF | OPENGL)
icon = pygame.image.load(".\\Resources\\icon.png")
pygame.display.set_caption(f"{CAPTION} | LAUNCHER")
pygame.display.set_icon(icon)
gluOrtho2D(0, LAUNCHER_WIDTH, 0, LAUNCHER_HEIGHT)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

hwnd = win32gui.FindWindow(None, pygame.display.get_caption()[0])

from core import *

bg_path = ".\\Resources\\launcher_bg.jpg"
bg = Image.open(bg_path)
bg = bg.convert("RGBA")
if LAUNCHER_WIDTH / bg.width > LAUNCHER_HEIGHT / bg.height:
    ill_scale = LAUNCHER_WIDTH / bg.width
else:
    ill_scale = LAUNCHER_HEIGHT / bg.height
bg = bg.filter(ImageFilter.GaussianBlur(14))
bg = bg.resize((int(bg.width * ill_scale), int(bg.height * ill_scale)))
bg = ImageEnhance.Brightness(bg).enhance(0.4)
bg = Texture.from_image(bg)

page = 1
max_page = 4

open_render = False
noautoplay = False
acrylic = False
show_bar = False

clock = pygame.time.Clock()

chart_path = ""
music_path = ""
ill_path = ""

### check update
try:
    update = requests.get('https://api.github.com/repos/Bychuhan/PyPhiRenderer/releases/latest', headers={'Accept-Language':'en-US'})
    update = update.text
    update = json.loads(update)
    if f'v{VERSION}' != update['name']:
        _v_l = VERSION.split('.')
        _new_v_l = update['name'][1:].split('.')
        for i in enumerate(_v_l):
            if i[0] < len(_new_v_l):
                _v_l[i[0]] = i[1].zfill(len(_new_v_l[i[0]]))
        for i in enumerate(_new_v_l):
            if i[0] < len(_v_l):
                _new_v_l[i[0]] = i[1].zfill(len(_v_l[i[0]]))
        _v = ''
        for i in _v_l:
            _v += i
        _new_v = ''
        for i in _new_v_l:
            _new_v += i
        if len(_new_v) < len(_v):
            _new_v += '0' * (len(_v) - len(_new_v))
        if len(_v) < len(_new_v):
            _v += '0' * (len(_new_v) - len(_v))
        _u = 1
        if _v < _new_v:
            _u = pygame.display.message_box(LOCALES['update']['check-update'], f'{LOCALES['update']['update-available']}\n\n{LOCALES['update']['new-version']}{update['name']}\n{(LOCALES['update']['no-message'] if update['body'] == '' else update['body'])}', 'info', None, (LOCALES['update']['download'], LOCALES['update']['close']), 0, 1)
        if _u == 0:
            _download = update['assets'][0]['browser_download_url']
            import webbrowser
            webbrowser.open(_download)
except requests.exceptions.SSLError:
    pygame.display.message_box(LOCALES['update']['error'], LOCALES['update']['check-update-failed'], 'error', None, (LOCALES['update']['close'],), 0, 0)
###


class Button:
    def __init__(self,x,y,width,height,func,anchor):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.func = func
        self.anchor = anchor
        self.disable = False

    def update(self):
        self.draw()

    def click(self, x, y):
        if not self.disable:
            if x > self.x-self.width * self.anchor[0] and x < self.x+self.width * (1 - self.anchor[0]) and y<self.y+self.height * (1 - self.anchor[1]) and y > self.y-self.height * self.anchor[1]:
                self.func()

    def draw(self):
        draw_rect(self.x*_hscale, self.y*_hscale, (self.width+6)*_hscale, (self.height+6)*_hscale, 0, 1, self.anchor, (0, 0, 0))
        draw_rect(self.x*_hscale, self.y*_hscale, (self.width)*_hscale, (self.height)*_hscale, 0, (0.5 if self.disable else 1), self.anchor, (1, 1, 1))

    def set_disable(self, d):
        self.disable = d

class InputBoard:
    def __init__(self,x,y,width,height,anchor,text_page,textindex,xmax,xmin):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.select = False
        self.anchor = anchor
        self.text_page = text_page
        self.text_index = textindex
        self.xmax = xmax
        self.xmin = xmin
        self.s = TEXT[self.text_page][self.text_index][2]
        self.disable = False
        self._edit = ''

    def update(self):
        self.draw()

    def click(self, x, y):
        if (x > self.x-self.width * self.anchor[0] and x < self.x+self.width * (1 - self.anchor[0]) and y<self.y+self.height * (1 - self.anchor[1]) and y > self.y-self.height * self.anchor[1]) and not self.disable:
            self.select = True
            pygame.key.start_text_input()
            _rect = pygame.rect.Rect(self.x*_hscale, LAUNCHER_HEIGHT-self.y*_hscale+self.height*_hscale/2, 0, 0)
            pygame.key.set_text_input_rect(_rect)
        else:
            if self.select:
                pygame.key.stop_text_input()
            self.select = False

    def input(self, text):
        if not self.disable:
            if self.select:
                _l = len(TEXT[self.text_page][self.text_index][0].text) - len(self._edit)
                TEXT[self.text_page][self.text_index][0].change_text(f"{TEXT[self.text_page][self.text_index][0].text[0:_l]}{text}")
                self.s_width()
    
    def edit(self, text):
        if not self.disable:
            if self.select:
                _l = len(TEXT[self.text_page][self.text_index][0].text) - len(self._edit)
                TEXT[self.text_page][self.text_index][0].change_text(f"{TEXT[self.text_page][self.text_index][0].text[0:_l]}{text}")
                self._edit = text
                self.s_width()

    def s_width(self):
        if TEXT[self.text_page][self.text_index][0].w * TEXT[self.text_page][self.text_index][2] > self.xmax:
            self.width = self.xmax + 5
        else:
            if TEXT[self.text_page][self.text_index][0].w * TEXT[self.text_page][self.text_index][2] < self.xmin:
                self.width = self.xmin
            else:
                self.width = TEXT[self.text_page][self.text_index][0].w * TEXT[self.text_page][self.text_index][2] + 10

    def draw(self):
        draw_rect(self.x*_hscale, self.y*_hscale, self.width*_hscale, self.height*_hscale, 0, (0.5 if self.disable else 1), self.anchor, (1, 1, 1))

    def back(self):
        if self.select:
            TEXT[self.text_page][self.text_index][0].change_text(TEXT[self.text_page][self.text_index][0].text[:-1])
            self.s_width()

    def get(self):
        return TEXT[self.text_page][self.text_index][0].text

    def set(self, text):
        TEXT[self.text_page][self.text_index][0].change_text(text)
        self.s_width()

    def set_disable(self, d):
        self.disable = d

class Tip:
    def get_id(self):
        for i in range(len(tip_id)):
            if not i in tip_id:
                return i
        return len(tip_id)

    def __init__(self, text, color, textcolor, timecolor, time_, alpha=1):
        self.id = self.get_id()
        tip_id.append(self.id)
        self.text = Text(text, FONT, 999999)
        self.color = color
        self.tcolor = textcolor
        self.timecolor = timecolor
        self.time = time_
        self.timer = 0
        self.start_time = time.time()
        self.width = self.text.w * TIP_TEXT_SCALE + 15
        self.height = 50 * _hscale
        self.x_offset = self.width + 10
        self.alpha = alpha

    def update(self):
        if (890*_hscale) - self.id * (self.height + 20) + self.height / 2 < 0:
            return True
        self.timer = time.time() - self.start_time
        self.x_offset = 0
        if self.timer < 1:
            self.x_offset = (self.width + 10) - ((self.width + 10) * rpe_easings[8](self.timer / 1))
        if self.timer - 2 > self.time:
            for i in tip_id.copy():
                if i == self.id:
                    tip_id.remove(i)
            return True
        if self.timer - 1 > self.time:
            self.x_offset = (self.width + 10) * rpe_easings[9]((self.timer - 1 - self.time) / 1)
        self.render()

    def t_rem(self, r_id):
        if self.id > r_id:
            self.id -= 1

    def render(self):
        draw_rect((LAUNCHER_WIDTH-10) + self.x_offset, (890*_hscale) - self.id * (self.height + 20 * _hscale), self.width, self.height, 0, self.alpha, (1, 1), self.color)
        self.text.render((LAUNCHER_WIDTH-10) - 7.5 + self.x_offset, (890*_hscale) - self.height * (0.5) - self.id * (self.height + 20 * _hscale), TIP_TEXT_SCALE, TIP_TEXT_SCALE, 0, 1, (1, 0.5), self.tcolor)
        draw_rect((LAUNCHER_WIDTH-10) + self.x_offset - self.width, (890*_hscale) - self.height - self.id * (self.height + 20 * _hscale), self.width * (max(min((self.timer - 1) / self.time, 1), 0)), self.height * 0.15, 0, 1, (0, 0), self.timecolor)

def import_chart():
    global chart_path
    chart_path = askopenfilename(title = '请选择谱面文件',filetypes = [('Phiedit Chart File', '.pez .zip .json')])
    TEXT[1][3][0].change_text(chart_path)
    if os.path.splitext(chart_path)[-1] == '.zip' or os.path.splitext(chart_path)[-1] == '.pez':
        BUTTON[1][1].set_disable(True)
        BUTTON[1][2].set_disable(True)
        INPUTBOARD[1][0].set_disable(True)
        INPUTBOARD[1][1].set_disable(True)
        INPUTBOARD[1][4].set_disable(True)
        INPUTBOARD[1][5].set_disable(True)
        INPUTBOARD[1][6].set_disable(True)
    else:
        BUTTON[1][1].set_disable(False)
        BUTTON[1][2].set_disable(False)
        INPUTBOARD[1][0].set_disable(False)
        INPUTBOARD[1][1].set_disable(False)
        INPUTBOARD[1][4].set_disable(False)
        INPUTBOARD[1][5].set_disable(False)
        INPUTBOARD[1][6].set_disable(False)
        format, n, l, m, i, cp, ce, il = get_info(chart_path)
        if format == "rpe":
            INPUTBOARD[1][0].set(n)
            INPUTBOARD[1][1].set(l)
            INPUTBOARD[1][4].set(cp)
            INPUTBOARD[1][5].set(ce)                                                                       
            INPUTBOARD[1][6].set(il)
            if not m is None:
                global music_path
                music_path = m
                TEXT[1][6][0].change_text(m)
            if not i is None:
                global ill_path
                ill_path = i
                TEXT[1][9][0].change_text(i)

def import_music():
    global music_path
    music_path = askopenfilename(title = '请选择音乐文件',filetypes = [('Audio', '.mp3 .wav .ogg')])
    TEXT[1][6][0].change_text(music_path)

def import_ill():
    global ill_path
    ill_path = askopenfilename(title = '请选择曲绘文件',filetypes = [('Image', '.png .jpg .jpeg .gif .webp')])
    TEXT[1][9][0].change_text(ill_path)

def start():
    name=INPUTBOARD[1][0].get()
    level=INPUTBOARD[1][1].get()
    composer=INPUTBOARD[1][4].get()
    charter=INPUTBOARD[1][5].get()
    illustrator=INPUTBOARD[1][6].get()
    w = INPUTBOARD[1][2].get()
    h = INPUTBOARD[1][3].get()
    fps = INPUTBOARD[2][0].get()
    bitrate = INPUTBOARD[2][1].get()
    argv = INPUTBOARD[1][7].get()
    combo_tips = INPUTBOARD[3][0].get()
    aspect_ratio = INPUTBOARD[3][1].get()
    bg_alpha = INPUTBOARD[3][2].get()
    ill_blur = INPUTBOARD[3][3].get()
    if not (":" in aspect_ratio and len([i for i in aspect_ratio.split(":") if i.isdigit()]) == 2):
        aspect_ratio = "16:9"
    if not is_number(bg_alpha):
        bg_alpha = 0.1
    m_type = f"{sys.executable} main.py" if os.path.exists(".\\main.py") else ("main.exe" if os.path.exists(".\\main.exe") else None)
    if m_type is None:
        error("找不到 main.py 或 main.exe")
    else:
        cmd=f"{m_type} --chart \"{chart_path}\" --music \"{music_path}\" --illustration \"{ill_path}\" --name \"{name}\" --level \"{level}\" --composer \"{composer}\" --charter \"{charter}\" --illustrator \"{illustrator}\" --combotips \"{combo_tips}\" --aspectratio \"{aspect_ratio}\" --bgalpha {bg_alpha}{' --showbar' if show_bar else ''}{' --noautoplay' if noautoplay else ''}{f' --illblur {ill_blur}' if ill_blur.isdigit() else ''}{f" --width {w}" if w.isdigit() else ""}{f" --height {h}" if h.isdigit() else ""}{f" --render{f" --fps {fps}" if fps.isdigit() else ""}{f" --bitrate {bitrate}" if bitrate.isdigit() else ""}" if open_render else ""} {argv}"
        print(cmd)
        win32gui.ShowWindow(hwnd, False)
        subprocess.run(cmd)
        win32gui.ShowWindow(hwnd, True)

def next_page():
    global page
    global max_page
    if page < max_page:
        page+=1
    else:
        tips.append(Tip(LOCALES['launcher']['last-page'],(0.2,1,0.2),(1,1,1),(0.2,1,0.2),2,0.6))
    TEXT[0][0][0].change_text(f"{page} / {max_page}")

def previous_page():
    global page
    if page > 1:
        page-=1
    else:
        tips.append(Tip(LOCALES['launcher']['first-page'],(0.2,1,0.2),(1,1,1),(0.2,1,0.2),2,0.6))
    TEXT[0][0][0].change_text(f"{page} / {max_page}")

def switch_render():
    global open_render
    open_render = not open_render
    TEXT[2][6][0].change_text("√" if open_render else "")

def switch_noautoplay():
    global noautoplay
    noautoplay = not noautoplay
    TEXT[4][2][0].change_text("√" if noautoplay else "")

def switch_acrylic():
    global acrylic
    acrylic = not acrylic
    TEXT[3][10][0].change_text("√" if acrylic else "")

def switch_showbar():
    global show_bar
    show_bar = not show_bar
    TEXT[3][12][0].change_text("√" if show_bar else "")

TEXT = (
    (#0
        (Text(f"{page} / {max_page}",FONT), (600, 20), 0.35, (0.5, 0.5), (1, 1, 1), "1"),
        (Text(f"→",FONT), (1160, 40), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text(f"←",FONT), (1095, 40), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['start'],FONT), (40, 35), 0.5, (0, 0.5), (0, 0, 0), "1"),
    ),
    (#1
        (Text(LOCALES['launcher']['title-1'],FONT), (600, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['chart'],FONT), (40, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("点击选择谱面",FONT), (250, 750), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['not-selected'],FONT,800), (385, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['music'],FONT), (40, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("点击选择音乐",FONT), (250, 685), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['not-selected'],FONT,800), (385, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['illustration'],FONT), (40, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("点击选择曲绘",FONT), (250, 620), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['not-selected'],FONT,800), (385, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['name'],FONT), (40, 555), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",FONT,1050), (130, 555), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['level'],FONT), (40, 490), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",FONT,1050), (130, 490), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['window-width'],FONT), (40, 230), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['window-height'],FONT), (40, 165), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("1200",FONT,975), (205, 230), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("900",FONT,975), (205, 165), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['composer'],FONT), (40, 425), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",FONT,1050), (130, 425), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['charter'],FONT), (40, 360), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",FONT,1050), (130, 360), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['illustrator'],FONT), (40, 295), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",FONT,1050), (130, 295), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['argv'],FONT), (40, 100), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("",FONT,975), (205, 100), 0.5, (0, 0.5), (0, 0, 0), "1"),
    ),
    (#2
        (Text(LOCALES['launcher']['title-2'],FONT), (600, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['enable-render'],FONT), (100, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['fps'],FONT), (40, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("60",FONT,1050), (130, 685), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['bitrate'],FONT), (40, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("15000",FONT,1050), (130, 620), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("",FONT), (64.5, 750), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
    ),
    (#3
        (Text(LOCALES['launcher']['title-3'],FONT), (600, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['combo-tips'],FONT), (40, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("COMBO",FONT,920), (260, 750), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['aspect-ratio'],FONT), (40, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("16:9",FONT,1012.5), (167.5, 685), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['background-alpha'],FONT), (40, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("0.1",FONT,975), (205, 620), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text(LOCALES['launcher']['illustration-blur'],FONT), (40, 555), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("80",FONT,975), (205, 555), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text('在这里加一个炫酷牛逼吊炸天的功能',FONT), (100, 490), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("",FONT), (64.5, 490), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text('显示曲名前竖线',FONT), (100, 425), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("",FONT), (64.5, 425), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
    ),
    (#4
        (Text(LOCALES['launcher']['title-4'],FONT), (600, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text(LOCALES['launcher']['no-autoplay'],FONT), (100, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("",FONT), (64.5, 750), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
    ),
)

BUTTON = (
    (#0
        Button(1160,40,50,50,next_page,(0.5,0.5)),
        Button(1095,40,50,50,previous_page,(0.5,0.5)),
        Button(80,35,80,50,start,(0.5,0.5)),
    ),
    (#1
        Button(250,750,240,50,import_chart,(0.5,0.5)),
        Button(250,685,240,50,import_music,(0.5,0.5)),
        Button(250,620,240,50,import_ill,(0.5,0.5)),
    ),
    (#2
        Button(64.5,750,45,45,switch_render,(0.5,0.5)),
    ),
    (#3
        Button(64.5,490,45,45,switch_acrylic,(0.5,0.5)),
        Button(64.5,425,45,45,switch_showbar,(0.5,0.5)),
    ),
    (#4
        Button(64.5,750,45,45,switch_noautoplay,(0.5,0.5)),
    ),
)

INPUTBOARD = (
    (#0
        
    ),
    (#1
        InputBoard(125,555,240,50,(0,0.5),1,11,1050,240),
        InputBoard(125,490,240,50,(0,0.5),1,13,1050,240),
        InputBoard(200,230,240,50,(0,0.5),1,16,975,240),
        InputBoard(200,165,240,50,(0,0.5),1,17,975,240),
        InputBoard(125,425,240,50,(0,0.5),1,19,1050,240),
        InputBoard(125,360,240,50,(0,0.5),1,21,1050,240),
        InputBoard(125,295,240,50,(0,0.5),1,23,1050,240),
        InputBoard(200,100,240,50,(0,0.5),1,25,975,240),
    ),
    (#2
        InputBoard(125,685,240,50,(0,0.5),2,3,1050,240),
        InputBoard(125,620,240,50,(0,0.5),2,5,1050,240),
    ),
    (#3
        InputBoard(255,750,240,50,(0,0.5),3,2,920,240),
        InputBoard(162.5,685,240,50,(0,0.5),3,4,1012.5,240),
        InputBoard(200,620,240,50,(0,0.5),3,6,1050,240),
        InputBoard(200,555,240,50,(0,0.5),3,8,1050,240),
    ),
    (#4
        #请输入文本
    ),
)

tips: list[Tip] = []
tip_id: list[int] = []

def draw_ui():
    global tip_id
    for button in BUTTON[0] + BUTTON[page]:
        button.draw()
    for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
        inputboard.draw()
    for text in TEXT[0] + TEXT[page]:
        text[0].render(text[1][0]*_hscale,text[1][1]*_hscale,text[2]*_hscale,text[2]*_hscale,0,1,text[3],text[4])
    for i in tips.copy():
        if i.update():
            _id = i.id
            tips.remove(i)
            for t in tips.copy():
                t.t_rem(_id)
            tip_id = [(i-1 if i > _id else i) for i in tip_id]

while True:
    clock.tick()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in BUTTON[0] + BUTTON[page]:
                button.click(event.pos[0]/_hscale, 900-event.pos[1]/_hscale)
            for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                inputboard.click(event.pos[0]/_hscale, 900-event.pos[1]/_hscale)
        if event.type == pygame.TEXTINPUT:
            for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                inputboard.input(event.text)
        if event.type == pygame.TEXTEDITING:
            for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                inputboard.edit(event.text)
        if event.type == pygame.KEYDOWN:
            if event.unicode == "\x08":
                for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                    inputboard.back()

    glClear(GL_COLOR_BUFFER_BIT)

    draw_texture(bg, LAUNCHER_WIDTH / 2, LAUNCHER_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1))

    draw_ui()

    pygame.display.flip()