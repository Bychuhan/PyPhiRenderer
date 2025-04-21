import pygame, subprocess, win32gui, err_hook, time
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

TIP_TEXT_SCALE = 0.5

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
max_page = 2

open_render = False

font = pygame.font.Font(".\\Resources\\fonts\\font.ttf", 75)

clock = pygame.time.Clock()

chart_path = ""
music_path = ""
ill_path = ""

class Button:
    def __init__(self,x,y,width,height,func,anchor):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.func = func
        self.anchor = anchor

    def update(self):
        self.draw()

    def click(self, x, y):
        if x > self.x-self.width * self.anchor[0] and x < self.x+self.width * (1 - self.anchor[0]) and y<self.y+self.height * (1 - self.anchor[1]) and y > self.y-self.height * self.anchor[1]:
            self.func()

    def draw(self):
        draw_rect(self.x, self.y, self.width+6, self.height+6, 0, 1, self.anchor, (0, 0, 0))
        draw_rect(self.x, self.y, self.width, self.height, 0, 1, self.anchor, (1, 1, 1))

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

    def update(self):
        self.draw()

    def click(self, x, y):
        if x > self.x-self.width * self.anchor[0] and x < self.x+self.width * (1 - self.anchor[0]) and y<self.y+self.height * (1 - self.anchor[1]) and y > self.y-self.height * self.anchor[1]:
            self.select = True
        else:
            self.select = False

    def input(self, text):
        if self.select:
            TEXT[self.text_page][self.text_index][0].change_text(f"{TEXT[self.text_page][self.text_index][0].text}{text}")
            self.s_width()

    def s_width(self):
        if TEXT[self.text_page][self.text_index][0].w * TEXT[self.text_page][self.text_index][2] > self.xmax:
            self.width = self.xmax + 5
        else:
            if TEXT[self.text_page][self.text_index][0].w * TEXT[self.text_page][self.text_index][2] < self.xmin:
                self.width = self.xmin
            else:
                self.width = TEXT[self.text_page][self.text_index][0].w * TEXT[self.text_page][self.text_index][2] + 5

    def draw(self):
        draw_rect(self.x+3, self.y, self.width, self.height, 0, 1, self.anchor, (1, 1, 1))

    def back(self):
        if self.select:
            TEXT[self.text_page][self.text_index][0].change_text(TEXT[self.text_page][self.text_index][0].text[:-1])
            self.s_width()

    def get(self):
        return TEXT[self.text_page][self.text_index][0].text

    def set(self, text):
        TEXT[self.text_page][self.text_index][0].change_text(text)
        self.s_width()

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
        self.height = 50
        self.x_offset = self.width + 10
        self.alpha = alpha

    def update(self):
        if 890 - self.id * (self.height + 20) + self.height / 2 < 0:
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

    def render(self):
        draw_rect(1190 + self.x_offset, 890 - self.id * (self.height + 20), self.width, self.height, 0, self.alpha, (1, 1), self.color)
        self.text.render(1190 - 7.5 + self.x_offset, 890 - self.height * (0.5) - self.id * (self.height + 20), TIP_TEXT_SCALE, TIP_TEXT_SCALE, 0, 1, (1, 0.5), self.tcolor)
        draw_rect(1190 + self.x_offset - self.width, 890 - self.height - self.id * (self.height + 20), self.width * (max(min((self.timer - 1) / self.time, 1), 0)), self.height * 0.15, 0, 1, (0, 0), self.timecolor)

def import_chart():
    global chart_path
    chart_path = askopenfilename()
    TEXT[1][3][0].change_text(chart_path)
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
    music_path = askopenfilename()
    TEXT[1][6][0].change_text(music_path)

def import_ill():
    global ill_path
    ill_path = askopenfilename()
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
    cmd=f"python main.py --chart \"{chart_path}\" --music \"{music_path}\" --illustration \"{ill_path}\" --name \"{name}\" --level \"{level}\" --composer \"{composer}\" --charter \"{charter}\" --illustrator \"{illustrator}\"{f" --width {w}" if w.isdigit() else ""}{f" --height {h}" if h.isdigit() else ""}{f" --render{f" --fps {fps}" if fps.isdigit() else ""}{f" --bitrate {bitrate}" if bitrate.isdigit() else ""}" if open_render else ""} {argv}"
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
        tips.append(Tip("已经是最后一页",(0.2,1,0.2),(1,1,1),(0.2,1,0.2),2,0.6))
    TEXT[0][0][0].change_text(f"{page} / {max_page}")

def previous_page():
    global page
    if page > 1:
        page-=1
    else:
        tips.append(Tip("已经是第一页",(0.2,1,0.2),(1,1,1),(0.2,1,0.2),2,0.6))
    TEXT[0][0][0].change_text(f"{page} / {max_page}")

def switch_render():
    global open_render
    open_render = not open_render
    TEXT[2][6][0].change_text("√" if open_render else "")

TEXT = (
    (#0
        (Text(f"{page} / {max_page}",font), (600, 20), 0.35, (0.5, 0.5), (1, 1, 1), "1"),
        (Text(f"→",font), (1160, 40), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text(f"←",font), (1095, 40), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text("启动",font), (40, 35), 0.5, (0, 0.5), (0, 0, 0), "1"),
    ),
    (#1
        (Text("基本设置",font), (LAUNCHER_WIDTH / 2, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text("谱面",font), (40, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("点击选择谱面",font), (250, 750), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text("未选择",font,800), (385, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("音乐",font), (40, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("点击选择音乐",font), (250, 685), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text("未选择",font,800), (385, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("曲绘",font), (40, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("点击选择曲绘",font), (250, 620), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
        (Text("未选择",font,800), (385, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("曲名",font), (40, 555), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",font,1050), (130, 555), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("难度",font), (40, 490), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",font,1050), (130, 490), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("窗口宽度",font), (40, 230), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("窗口高度",font), (40, 165), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("1200",font,975), (205, 230), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("900",font,975), (205, 165), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("曲师",font), (40, 425), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",font,1050), (130, 425), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("谱师",font), (40, 360), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",font,1050), (130, 360), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("画师",font), (40, 295), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("null",font,1050), (130, 295), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("其他参数",font), (40, 100), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("",font,975), (205, 100), 0.5, (0, 0.5), (0, 0, 0), "1"),
    ),
    (#2
        (Text("渲染设置",font), (LAUNCHER_WIDTH / 2, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text("启用渲染",font), (100, 750), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("帧数",font), (40, 685), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("60",font,1050), (130, 685), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("码率",font), (40, 620), 0.5, (0, 0.5), (1, 1, 1), "1"),
        (Text("15000",font,1050), (130, 620), 0.5, (0, 0.5), (0, 0, 0), "1"),
        (Text("",font), (64.5, 750), 0.5, (0.5, 0.5), (0, 0, 0), "1"),
    ),
    (#3
        (Text("UI设置",font), (LAUNCHER_WIDTH / 2, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text("空空如也",font), (LAUNCHER_WIDTH / 2, 780), 0.4, (0.5, 0.5), (1, 1, 1), "1"),
    ),
    (#4
        (Text("其他设置",font), (LAUNCHER_WIDTH / 2, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
        (Text("空空如也",font), (LAUNCHER_WIDTH / 2, 780), 0.4, (0.5, 0.5), (1, 1, 1), "1"),
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
        
    ),
    (#4
        
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
        
    ),
    (#4
        
    ),
)

def draw_ui():
    for button in BUTTON[0] + BUTTON[page]:
        button.draw()
    for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
        inputboard.draw()
    for text in TEXT[0] + TEXT[page]:
        text[0].render(text[1][0],text[1][1],text[2],text[2],0,1,text[3],text[4])
    for i in tips.copy():
        if i.update():
            tips.remove(i)

tips: list[Tip] = []
tip_id: list[int] = []

while True:
    clock.tick()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in BUTTON[0] + BUTTON[page]:
                button.click(event.pos[0], LAUNCHER_HEIGHT-event.pos[1])
            for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                inputboard.click(event.pos[0], LAUNCHER_HEIGHT-event.pos[1])
        if event.type == pygame.TEXTINPUT:
            for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                inputboard.input(event.text)
        if event.type == pygame.KEYDOWN:
            if event.unicode == "\x08":
                for inputboard in INPUTBOARD[0] + INPUTBOARD[page]:
                    inputboard.back()


    glClear(GL_COLOR_BUFFER_BIT)

    draw_texture(bg, LAUNCHER_WIDTH / 2, LAUNCHER_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1))

    draw_ui()

    pygame.display.flip()