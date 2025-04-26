import pygame, data, sys, subprocess, tqdm, err_hook, math, time, os, win32gui
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
from const import *
from func import *
from tkinter.filedialog import askopenfilename
from dxsmixer import *
from texture import *
from PIL import Image, ImageFilter, ImageEnhance
from log import *
from states import *
"""from ending import *
from loading import *"""

pygame.init()
window = pygame.display.set_mode((REAL_WIDTH, REAL_HEIGHT), flags = DOUBLEBUF | OPENGL)
icon = pygame.image.load(".\\Resources\\icon.png")
pygame.display.set_caption(CAPTION)
pygame.display.set_icon(icon)
gluOrtho2D(0, REAL_WIDTH, 0, REAL_HEIGHT)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

hwnd = win32gui.FindWindow(None, pygame.display.get_caption()[0])

if "--render" in sys.argv and "--preview" not in sys.argv:
    win32gui.ShowWindow(hwnd, False)

from parse_chart import *
from core import *

UI = (
    (Text(str(data.judges.combo),FONT), (WINDOW_WIDTH / 2, 570.78 * HEIGHT_SCALE), 0.5667 * HEIGHT_SCALE, (0.5, 0.5), "combonumber"),
    (Text("COMBO",FONT), (WINDOW_WIDTH / 2, 543.25 * HEIGHT_SCALE), 0.1973 * HEIGHT_SCALE, (0.5, 0.5), "combo"),
    (Text(str(data.judges.score),FONT), (WINDOW_WIDTH - 22.2 * HEIGHT_SCALE, 582.2 * HEIGHT_SCALE), 0.4031 * HEIGHT_SCALE, (1, 1), "score"),
    (Text("",FONT,0.647 * WINDOW_HEIGHT), (23.8 * HEIGHT_SCALE, 18.6 * HEIGHT_SCALE), 0.288 * HEIGHT_SCALE, (0, 0), "name"),
    (Text("",FONT), (WINDOW_WIDTH - 23.8 * HEIGHT_SCALE, 18.6 * HEIGHT_SCALE), 0.288 * HEIGHT_SCALE, (1, 0), "level"),
)

if "--chart" in sys.argv:
    chart_path = get_value("chart", "")
else:
    print("chart")
    chart_path = askopenfilename()
lines, formatVersion, offset, num_of_notes, chart, format, bpm_list, attachUI, path = parse_chart(chart_path)
if "--offset" in sys.argv:
    offset = int(get_value("offset", offset))
pause_attach = None
bar_attach = None
if format == "rpe":
    for i in UI:
        if i[4] in attachUI:
            if not attachUI[i[4]] is None:
                i[0].attach(attachUI[i[4]])
    pause_attach = attachUI["pause"]
    bar_attach = attachUI["bar"]
info(f"Loaded chart | {chart_path}")

shaders = {}
videos = {}
if os.path.exists(f"{path}/extra.json"):
    extra_path = f"{path}/extra.json"
    shaders, videos = parse_extra(extra_path)

for line in lines:
    line.load_note_hl()
    line.load_note()

if "--music" in sys.argv:
    music_path = get_value("music", "")
else:
    print("music")
    music_path = askopenfilename()
music = musicCls()
try:
    music.load(music_path)
except:
    error_and_exit_no_tip("傻逼你音乐呢")
music_length = music.get_length()
info(f"Loaded music | {music_path}")

if "--illustration" in sys.argv:
    illustration_path = get_value("illustration", "")
else:
    print("illustration")
    illustration_path = askopenfilename()

try:
    illustration = Image.open(illustration_path)
except:
    error_and_exit_no_tip("傻逼你曲绘呢")
if REAL_WIDTH / illustration.width > REAL_HEIGHT / illustration.height:
    ill_scale = REAL_WIDTH / illustration.width
else:
    ill_scale = REAL_HEIGHT / illustration.height
illustration = illustration.filter(ImageFilter.GaussianBlur(80))
illustration = illustration.resize((int(illustration.width * ill_scale), int(illustration.height * ill_scale))).convert("RGB")
rill_clip = X_OFFSET/illustration.width
illustration = Texture.from_image(illustration)
info(f"Loaded illustration | {illustration_path}")

clock = pygame.time.Clock()

t_text = None
if not ("--name" in sys.argv and "--level" in sys.argv):
    clock.tick()
    t_text = Text("看看控制台TAT", FONT)
    t_text.render(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, -1, 1, 0, 1, (0.5, 0.5), (1, 1, 1))
    pygame.display.flip()

if "--name" in sys.argv:
    name = get_value("name", "UK")
else:
    print("songname:",end="")
    name = input()
UI[3][0].change_text(str(name))
if "--level" in sys.argv:
    level = get_value("level", "UK")
else:
    print("level:",end="")
    level = input()
UI[4][0].change_text(str(level))
composer = get_value("composer", "UK")
charter = get_value("charter", "UK")
illustrator = get_value("illustrator", "UK")
tip = get_tip(".\\Resources\\tips")

t_text = None

"""with open(".\\temp.txt", "w", encoding="utf-8") as f:
    f.write(f"python main.py --chart \"{chart_path}\" --music \"{music_path}\" --illustration \"{illustration_path}\" --name \"{name}\" --level \"{level}\"{" --render" if "--render" in sys.argv else ""}")
    f.close()"""

def update_ui():
    data.judges.score = str(round(data.judges.perfect / num_of_notes * 1e6)).zfill(7)
    UI[0][0].change_text(str(data.judges.combo))
    UI[2][0].change_text(str(data.judges.score))

def draw_ui(time):
    for text in UI:
        if (text[4] == "combo" or text[4] == "combonumber") and data.judges.combo < 3:
            continue
        text[0].render(text[1][0],text[1][1],text[2],text[2],0,1,text[3],(1,1,1), now_time)
    if pause_attach is None:
        draw_rect(19.83 * HEIGHT_SCALE, 578.1 * HEIGHT_SCALE, 6.2 * HEIGHT_SCALE, 22 * HEIGHT_SCALE, 0, 1, (0,1), (1,1,1), xoffset=X_OFFSET)
        draw_rect(32 * HEIGHT_SCALE, 578.1 * HEIGHT_SCALE, 6.2 * HEIGHT_SCALE, 22 * HEIGHT_SCALE, 0, 1, (0,1), (1,1,1), xoffset=X_OFFSET)
    else:
        lx, ly, lr, la, lsx, lsy, lc = pause_attach.get_data(time)
        _xs = 6.2 * HEIGHT_SCALE * lsx
        _ys = 22 * HEIGHT_SCALE * lsy
        _x = 19.83 * HEIGHT_SCALE + lx
        _y = 578.1 * HEIGHT_SCALE + ly
        _2xt = (32 - 19.83) * HEIGHT_SCALE
        _2x = _x + math.cos(math.radians(lr)) * (_2xt * lsx)
        _2y = _y + math.sin(math.radians(lr)) * (_2xt * lsx)
        draw_rect(_x, _y, _xs, _ys, lr, la, (0,1), lc, xoffset=X_OFFSET)
        draw_rect(_2x, _2y,_xs, _ys, lr, la, (0,1), lc, xoffset=X_OFFSET)
    process = (now_time + offset) / music_length
    s = 0 - 6.3 * HEIGHT_SCALE / 2
    if bar_attach is None:
        draw_rect(s + process * (WINDOW_WIDTH - s), WINDOW_HEIGHT, 2 * HEIGHT_SCALE, 6.3 * HEIGHT_SCALE, 0, 1, (0,1), (1,1,1), xoffset=X_OFFSET)
        draw_rect(s, WINDOW_HEIGHT, process * (WINDOW_WIDTH - s), 6.3 * HEIGHT_SCALE, 0, 1, (0,1), (0.569, 0.569, 0.569), xoffset=X_OFFSET)
    else:
        lx, ly, lr, la, lsx, lsy, lc = bar_attach.get_data(time)
        process *= lsx
        _y = WINDOW_HEIGHT - 6.3 * HEIGHT_SCALE / 2 + ly
        _2x = (lx + s) + math.cos(math.radians(lr)) * (process * (WINDOW_WIDTH - s))
        _2y = _y + math.sin(math.radians(lr)) * (process * (WINDOW_WIDTH - s))
        draw_rect(_2x, _2y, 2 * HEIGHT_SCALE, 6.3 * HEIGHT_SCALE * lsy, lr, la, (0,0.5), lc)
        draw_rect(lx + s, _y, process * (WINDOW_WIDTH - s), 6.3 * HEIGHT_SCALE * lsy, lr, la, (0,0.5), lc)

def phi_update():
    for line in lines:
        line.update(now_time)
        line.draw()
    for line in lines:
        line.update_hold(now_time)
    for line in lines:
        line.update_note(now_time)
    for line in lines:
        line.update_hit(now_time)

if format == "rpe":
    bpm = bpm_list[0]["bpm"]

def update_bpm(bpmlist):
    if len(bpmlist) == 1:
        return bpm_list[0]["bpm"]
    if now_time >= bpm_list[0]["time"]:
        bpm_list.pop(0)
        return update_bpm(bpmlist)
    return bpm_list[0]["bpm"]

def rpe_update():
    bpm = update_bpm(bpm_list)
    for line in lines:
        line.update(now_time)
        line.draw()
    for line in lines:
        line.update_hold(now_time, bpm)
    for line in lines:
        line.update_note(now_time)
    for line in lines:
        line.update_hit(now_time)

ui_state = States.Playing

if "--render" not in sys.argv:
    pygame.display.set_caption(f"{CAPTION} | PLAYING")
    music.play()
    _t = - offset
    start_time = time.time()
    pause = False
    pause_start_time = time.time()
    y_st = time.time()
    """loading_time = 0
    loading = Loading(illustration_path, name=name, level=level, composer=composer, charter=charter, illustrator=illustrator, tip=tip)"""
    while True:
        clock.tick()

        for event in pygame.event.get():
            """if event.type == pygame.MOUSEMOTION:
                pos = list(event.pos)
                pos[1] = WINDOW_HEIGHT - pos[1]
                print(pos)"""
            if ui_state == States.Playing:
                if event.type == pygame.MOUSEWHEEL:
                    if pause:
                        y_st += event.y * 0.5
                    else:
                        start_time += event.y * 0.5
                    music.set_pos(time.time() - start_time)
                if event.type == pygame.KEYDOWN:
                    if event.unicode == " ":
                        pause = not pause
                        if pause:
                            pause_start_time = time.time()
                            y_st = start_time
                            music.pause()
                        else:
                            start_time = y_st + (time.time() - pause_start_time)
                            music.unpause()
                            music.set_pos(time.time() - start_time)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        glClear(GL_COLOR_BUFFER_BIT)

        match ui_state:
            case 1:
                pass
                """draw_texture(illustration, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1))
                if loading.update():
                    loading = None
                    music.play()
                    _t = - offset
                    start_time = time.time()
                    pause = False
                    pause_start_time = time.time()
                    y_st = time.time()
                    ui_state = States.Playing
                else:
                    loading.draw()"""

            case 2:
                if pause:
                    start_time = y_st + (time.time() - pause_start_time)
                now_time = time.time() - start_time - offset

                if now_time >= _t:
                    debug(f"FPS | {round(clock.get_fps())}")
                    _t += 1

                draw_texture(illustration, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1), xoffset=X_OFFSET)
                draw_rect(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,WINDOW_WIDTH,WINDOW_HEIGHT,0,0.6,(0.5,0.5),(0,0,0),xoffset=X_OFFSET)

                if format == "phi":
                    phi_update()
                elif format == "rpe":
                    rpe_update()

                update_ui()
                draw_ui(now_time)

                if W_LIMIT:
                    draw_texture(illustration, 0, 0, 1, 1, 0, 1, (0,0), (1,1,1), clip=((0,0),(rill_clip,0),(rill_clip,1),(0,1)))
                    draw_texture(illustration, REAL_WIDTH, 0, 1, 1, 0, 1, (1,0), (1,1,1), clip=((1-rill_clip,0),(1,0),(1,1),(1-rill_clip,1)))
                    draw_rect(0,0,X_OFFSET,REAL_HEIGHT,0,0.7,(0,0),(0.1,0.1,0.1))
                    draw_rect(REAL_WIDTH,0,X_OFFSET,REAL_HEIGHT,0,0.7,(1,0),(0.1,0.1,0.1))

                """if now_time + offset > music_length:
                    lines.clear()
                    music.stop()
                    ending = Ending()
                    ui_state = States.Ending"""

            case 3:
                pass
                """ending.update()
                ending.draw()"""

        pygame.display.flip()
else:
    ispreview = "--preview" in sys.argv
    pygame.display.set_caption("PREVIEW" if ispreview else CAPTION)
    import hitsound
    fps = int(get_value("fps", 60))
    output = get_value("output", f"{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())} {name}_{level.split(" ")[0] if " Lv." in level or "  Lv." in level else level}.mp4")
    delta = 1 / fps
    bitrate = int(get_value("bitrate", 15000))
    hitsound.summon(chart, music_path, ".\\sound.mp3", format, path)
    ffmpeg_command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{REAL_WIDTH}x{REAL_HEIGHT}", "-pix_fmt", "rgb24",
        "-r", str(fps), "-i", "-", "-i", ".\\sound.mp3", "-c:v", "libx264", "-b:v", f"{bitrate}k", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-strict", "experimental", "-vf", "vflip", output
    ]
    frame = int(fps * music_length)
    process = subprocess.Popen(ffmpeg_command, stdin = subprocess.PIPE, stderr = subprocess.DEVNULL)
    print("已开始渲染，按下 Ctrl+C 停止...")
    now_time = 0. - offset
    for i in tqdm.tqdm(range(frame), desc = "Rendering video", unit = "frames"):
        if ispreview:
            clock.tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    break
        glClear(GL_COLOR_BUFFER_BIT)

        draw_texture(illustration, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1), xoffset=X_OFFSET)
        draw_rect(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,WINDOW_WIDTH,WINDOW_HEIGHT,0,0.6,(0.5,0.5),(0,0,0),xoffset=X_OFFSET)

        if format == "phi":
            phi_update()
        elif format == "rpe":
            rpe_update()
        update_ui()
        draw_ui(now_time)

        if W_LIMIT:
            draw_texture(illustration, 0, 0, 1, 1, 0, 1, (0,0), (1,1,1), clip=((0,0),(rill_clip,0),(rill_clip,1),(0,1)))
            draw_texture(illustration, REAL_WIDTH, 0, 1, 1, 0, 1, (1,0), (1,1,1), clip=((1-rill_clip,0),(1,0),(1,1),(1-rill_clip,1)))
            draw_rect(0,0,X_OFFSET,REAL_HEIGHT,0,0.7,(0,0),(0.1,0.1,0.1))
            draw_rect(REAL_WIDTH,0,X_OFFSET,REAL_HEIGHT,0,0.7,(1,0),(0.1,0.1,0.1))

        if ispreview:
            pygame.display.flip()

        frame_image = glReadPixels(0, 0, REAL_WIDTH, REAL_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
        process.stdin.write(frame_image)
        now_time += delta
    process.stdin.close()
    process.wait()

    if os.path.exists(".\\sound.mp3"):
        os.remove(".\\sound.mp3")

    pygame.quit()
    exit()