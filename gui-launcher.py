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

error_and_exit_no_tip("111")

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

font = pygame.font.Font(".\\Resources\\fonts\\font.ttf", 75)

clock = pygame.time.Clock()

chart_path = ""
music_path = ""
ill_path = ""

TEXT = (
    (Text("标题",font), (LAUNCHER_WIDTH / 2, 835), 0.75, (0.5, 0.5), (1, 1, 1), "1"),
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
    (Text("启动",font), (40, 100), 0.5, (0, 0.5), (0, 0, 0), "1"),
)

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
    def __init__(self,x,y,width,height,anchor,textindex,xmax,xmin):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.select = False
        self.anchor = anchor
        self.text_index = textindex
        self.xmax = xmax
        self.xmin = xmin
        self.s = TEXT[self.text_index][2]

    def update(self):
        self.draw()

    def click(self, x, y):
        if x > self.x-self.width * self.anchor[0] and x < self.x+self.width * (1 - self.anchor[0]) and y<self.y+self.height * (1 - self.anchor[1]) and y > self.y-self.height * self.anchor[1]:
            self.select = True
        else:
            self.select = False

    def input(self, text):
        if self.select:
            TEXT[self.text_index][0].change_text(f"{TEXT[self.text_index][0].text}{text}")
            self.s_width()

    def s_width(self):
        if TEXT[self.text_index][0].w * TEXT[self.text_index][2] > self.xmax:
            self.width = self.xmax + 5
        else:
            if TEXT[self.text_index][0].w * TEXT[self.text_index][2] < self.xmin:
                self.width = self.xmin
            else:
                self.width = TEXT[self.text_index][0].w * TEXT[self.text_index][2] + 5

    def draw(self):
        draw_rect(self.x+3, self.y, self.width, self.height, 0, 1, self.anchor, (1, 1, 1))

    def back(self):
        if self.select:
            TEXT[self.text_index][0].change_text(TEXT[self.text_index][0].text[:-1])
            self.s_width()

    def get(self):
        return TEXT[self.text_index][0].text

    def set(self, text):
        TEXT[self.text_index][0].change_text(text)
        self.s_width()

class Tip:
    def get_id(self):
        for i in range(len(tip_id)):
            if not i in tip_id:
                return i
        return len(tip_id)

    def __init__(self, text, color, textcolor, timecolor, time_):
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
        draw_rect(1190 + self.x_offset, 890 - self.id * (self.height + 20), self.width, self.height, 0, 1, (1, 1), self.color)
        self.text.render(1190 - 7.5 + self.x_offset, 890 - self.height * (0.5) - self.id * (self.height + 20), TIP_TEXT_SCALE, TIP_TEXT_SCALE, 0, 1, (1, 0.5), self.tcolor)
        draw_rect(1190 + self.x_offset - self.width, 890 - self.height - self.id * (self.height + 20), self.width * (max(min((self.timer - 1) / self.time, 1), 0)), self.height * 0.15, 0, 1, (0, 0), self.timecolor)

def import_chart():
    global chart_path
    chart_path = askopenfilename()
    TEXT[3][0].change_text(chart_path)
    format, n, l, m, i, cp, ce, il = get_info(chart_path)
    if format == "rpe":
        INPUTBOARD[0].set(n)
        INPUTBOARD[1].set(l)
        INPUTBOARD[4].set(cp)
        INPUTBOARD[5].set(ce)
        INPUTBOARD[6].set(il)
        if not m is None:
            global music_path
            music_path = m
            TEXT[6][0].change_text(m)
        if not i is None:
            global ill_path
            ill_path = i
            TEXT[9][0].change_text(i)

def import_music():
    global music_path
    music_path = askopenfilename()
    TEXT[6][0].change_text(music_path)

def import_ill():
    global ill_path
    ill_path = askopenfilename()
    TEXT[9][0].change_text(ill_path)

def start():
    name=INPUTBOARD[0].get()
    level=INPUTBOARD[1].get()
    composer=INPUTBOARD[4].get()
    charter=INPUTBOARD[5].get()
    illustrator=INPUTBOARD[6].get()
    w = INPUTBOARD[2].get()
    h = INPUTBOARD[3].get()
    cmd=f"python main.py --chart \"{chart_path}\" --music \"{music_path}\" --illustration \"{ill_path}\" --name \"{name}\" --level \"{level}\" --composer \"{composer}\" --charter \"{charter}\" --illustrator \"{illustrator}\"{f" --width {w}" if w.isdigit() else ""}{f" --height {h}" if h.isdigit() else ""}"
    print(cmd)
    win32gui.ShowWindow(hwnd, False)
    subprocess.run(cmd)
    win32gui.ShowWindow(hwnd, True)

BUTTON = (
    Button(250,750,240,50,import_chart,(0.5,0.5)),
    Button(250,685,240,50,import_music,(0.5,0.5)),
    Button(250,620,240,50,import_ill,(0.5,0.5)),
    Button(80,100,80,50,start,(0.5,0.5)),
)

INPUTBOARD = (
    InputBoard(125,555,240,50,(0,0.5),11,1050,240),
    InputBoard(125,490,240,50,(0,0.5),13,1050,240),
    InputBoard(200,230,240,50,(0,0.5),16,975,240),
    InputBoard(200,165,240,50,(0,0.5),17,975,240),
    InputBoard(125,425,240,50,(0,0.5),19,1050,240),
    InputBoard(125,360,240,50,(0,0.5),21,1050,240),
    InputBoard(125,295,240,50,(0,0.5),23,1050,240),
)

def draw_ui():
    for button in BUTTON:
        button.draw()
    for inputboard in INPUTBOARD:
        inputboard.draw()
    for text in TEXT:
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
            for button in BUTTON:
                button.click(event.pos[0], LAUNCHER_HEIGHT-event.pos[1])
            for inputboard in INPUTBOARD:
                inputboard.click(event.pos[0], LAUNCHER_HEIGHT-event.pos[1])
        if event.type == pygame.TEXTINPUT:
            for inputboard in INPUTBOARD:
                inputboard.input(event.text)
        if event.type == pygame.KEYDOWN:
            if event.unicode == "\x08":
                for inputboard in INPUTBOARD:
                    inputboard.back()


    glClear(GL_COLOR_BUFFER_BIT)

    draw_texture(bg, LAUNCHER_WIDTH / 2, LAUNCHER_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1))

    draw_ui()

    pygame.display.flip()