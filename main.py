import pygame, data, sys, subprocess, tqdm, err_hook, math, time, os, win32gui, atexit
from pygame.locals import DOUBLEBUF, OPENGL, SRCALPHA
from OpenGL.GL import *
from OpenGL.GLU import *
from const import *
from func import *
from tkinter.filedialog import askopenfilename
from dxsmixer import *
from texture import *
from PIL import Image, ImageFilter
from log import *
from states import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
'''from ending import *
from loading import *'''

pygame.init()
window = pygame.display.set_mode((REAL_WIDTH, REAL_HEIGHT), flags = DOUBLEBUF | OPENGL | SRCALPHA)
icon = pygame.image.load(".\\Resources\\icon.png")
pygame.display.set_caption(CAPTION)
pygame.display.set_icon(icon)
gluOrtho2D(0, REAL_WIDTH, 0, REAL_HEIGHT)
#gluOrtho2D(-REAL_WIDTH*3/2-REAL_WIDTH/2, REAL_WIDTH*3, -REAL_HEIGHT*3/2-REAL_HEIGHT/2, REAL_HEIGHT*3)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

clock = pygame.time.Clock()

hwnd = pygame.display.get_wm_info()['window']#win32gui.FindWindow(None, pygame.display.get_caption()[0])

stop = False

'''
import win32con, win32api
from BlurWindow import blurWindow

blurWindow.GlobalBlur(hwnd)

ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
ex_style |= win32con.WS_EX_LAYERED
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 1, win32con.LWA_COLORKEY)'''

# tchart
class TChart(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.exists(event.src_path):
            time.sleep(0.2)
            if os.path.samefile(chart_path, event.src_path):
                global pause, pause_start_time, y_st, music, start_time, now_time, lines, stop
                stop = True
                lines.clear()
                music.stop()
                data.judges = data.Judge(0, 0, 0, 0, 0, 0, 0, 1, 2)
                info("Reloading chart...")
                load_chart(chart_path)
                info(f"Loaded chart | {chart_path}")
                music.play()
                start_time = time.time()
                now_time = 0.
                stop = False
            if os.path.samefile(music_path, event.src_path):
                global music_length, offset
                stop = True
                music.stop()
                info("Reloading music...")
                try:
                    music.load(music_path)
                except:
                    error_and_exit_no_tip("音乐加载失败")
                music_length = music.get_length()
                music.play()
                music.set_pos(now_time + offset)
                info(f"Loaded music | {music_path}")
                stop = False

if "--render" in sys.argv and "--preview" not in sys.argv:
    win32gui.ShowWindow(hwnd, False)

from parse_chart import *
from core import *

show_bar = '--showbar' in sys.argv

UI = (
    (Text(str(data.judges.combo),FONT), (WINDOW_WIDTH / 2, 570.78 * HEIGHT_SCALE), 0.5667 * HEIGHT_SCALE, (0.5, 0.5), "combonumber"),
    (Text(get_value("combotips", "COMBO"),FONT), (WINDOW_WIDTH / 2, 543.25 * HEIGHT_SCALE), 0.1973 * HEIGHT_SCALE, (0.5, 0.5), "combo"),
    (Text(str(data.judges.score),FONT), (WINDOW_WIDTH - 22.2 * HEIGHT_SCALE, 582.2 * HEIGHT_SCALE), 0.4031 * HEIGHT_SCALE, (1, 1), "score"),
    (Text("",FONT,0.647 * WINDOW_HEIGHT), ((28 if show_bar else 23.8) * HEIGHT_SCALE, 18.6 * HEIGHT_SCALE), 0.288 * HEIGHT_SCALE, (0, 0), "name"),
    (Text("",FONT), (WINDOW_WIDTH - 23.8 * HEIGHT_SCALE, 18.6 * HEIGHT_SCALE), 0.288 * HEIGHT_SCALE, (1, 0), "level"),
    #(Text("100.00%",FONT), (WINDOW_WIDTH - 22.2 * HEIGHT_SCALE, 550 * HEIGHT_SCALE), 0.25 * HEIGHT_SCALE, (1, 1), "acc"),
)

if "--chart" in sys.argv:
    chart_path = get_value("chart", "")
else:
    print("chart")
    chart_path = askopenfilename()

iszip = os.path.splitext(chart_path)[1] == '.zip' or os.path.splitext(chart_path)[1] == '.pez'

if iszip:
    import zipfile
    chart_zip = zipfile.ZipFile(chart_path)
    r = hex(int(random.random() * (8 ** 16)))[2:]
    file_path = f".\\.temp\\{r}"
    chart_zip.extractall(file_path)
    info_path = (f"{file_path}\\info.yml" if os.path.exists(f"{file_path}\\info.yml") else (f"{file_path}\\info.txt" if os.path.exists(f"{file_path}\\info.txt") else (f"{file_path}\\info.csv" if os.path.exists(f"{file_path}\\info.csv") else (None))))
    if info_path is None:
        error_and_exit_no_tip('未找到info')
    chart_path, music_path, illustration_path, name, level, composer, charter, illustrator = parse_info(info_path)
else:
    if "--music" in sys.argv:
        music_path = get_value("music", "")
    else:
        print("music")
        music_path = askopenfilename()

    if "--illustration" in sys.argv:
        illustration_path = get_value("illustration", "")
    else:
        print("illustration")
        illustration_path = askopenfilename()
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
    if "--level" in sys.argv:
        level = get_value("level", "UK")
    else:
        print("level:",end="")
        level = input()
    t_text = None
    composer = get_value("composer", "UK")
    charter = get_value("charter", "UK")
    illustrator = get_value("illustrator", "UK")

def load_chart(_path):
    global lines, formatVersion, offset, num_of_notes, chart, format, bpm_list, attachUI, path, pause_attach, bar_attach
    lines, formatVersion, offset, num_of_notes, chart, format, bpm_list, attachUI, path = parse_chart(_path)
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
    for line in lines:
        line.load_note_hl()
        line.load_note()
load_chart(chart_path)
info(f"Loaded chart | {chart_path}")

shaders = {}
videos = {}
if os.path.exists(f"{path}/extra.json"):
    extra_path = f"{path}/extra.json"
    shaders, videos = parse_extra(extra_path)

music = musicCls()
try:
    music.load(music_path)
except:
    error_and_exit_no_tip("音乐加载失败")
music_length = music.get_length()
info(f"Loaded music | {music_path}")

try:
    illustration = Image.open(illustration_path)
except:
    error_and_exit_no_tip("曲绘加载失败")
n_ill = illustration
if REAL_WIDTH / illustration.width > REAL_HEIGHT / illustration.height:
    ill_scale = REAL_WIDTH / illustration.width
else:
    ill_scale = REAL_HEIGHT / illustration.height
illustration = illustration.filter(ImageFilter.GaussianBlur(int(get_value('illblur', 80))))
illustration = illustration.resize((math.ceil(illustration.width * ill_scale), math.ceil(illustration.height * ill_scale)))
illustration = illustration.convert("RGB")
rill_clip = X_OFFSET/illustration.width
rill_xfs = (illustration.width-REAL_WIDTH)/2/illustration.width
rill_yfs = (illustration.height-REAL_HEIGHT)/2
illustration = Texture.from_image(illustration)
info(f"Loaded illustration | {illustration_path}")

UI[3][0].change_text(str(name))
UI[4][0].change_text(str(level))

if iszip and "--render" not in sys.argv:
    import shutil
    shutil.rmtree(f".\\.temp\\{r}")

tip = get_tip(".\\Resources\\tips")
bg_alpha = float(get_value('bgalpha', 0.1))

"""with open(".\\temp.txt", "w", encoding="utf-8") as f:
    f.write(f"python main.py --chart \"{chart_path}\" --music \"{music_path}\" --illustration \"{illustration_path}\" --name \"{name}\" --level \"{level}\"{" --render" if "--render" in sys.argv else ""}")
    f.close()"""

def update_ui():
    if data.judges.combo > data.judges.max_combo:
        data.judges.max_combo = data.judges.combo
    s = (data.judges.perfect / num_of_notes + (data.judges.good / num_of_notes * 0.685))
    data.judges.score = (0.9 * s + data.judges.max_combo / num_of_notes * 0.1) * 1e6
    a = data.judges.perfect + data.judges.good + data.judges.bad + data.judges.miss
    data.judges.acc = (1 if a == 0 else ((data.judges.perfect + data.judges.good * 0.65) / a))
    UI[0][0].change_text(str(data.judges.combo))
    UI[2][0].change_text(str(round(data.judges.score)).zfill(7))
    c = str(round(data.judges.acc*10000)/100)
    #UI[5][0].change_text(f"{c}{"0" if len(c.split(".")[1]) == 1 else ""}%")

def draw_ui(time):
    for text in UI:
        if (text[4] == "combo" or text[4] == "combonumber") and data.judges.combo < 3:
            continue
        text[0].render(text[1][0],text[1][1],text[2],text[2],0,1,text[3],(1,1,1), time)
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
    process = (time + offset) / music_length
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
        draw_rect(_2x, _2y, 2 * HEIGHT_SCALE, 6.3 * HEIGHT_SCALE * lsy, lr, la, (0,0.5), lc, xoffset=X_OFFSET)
        draw_rect(lx + s, _y, process * (WINDOW_WIDTH - s), 6.3 * HEIGHT_SCALE * lsy, lr, la, (0,0.5), lc, xoffset=X_OFFSET)
    if show_bar:
        draw_rect(16.67 * HEIGHT_SCALE, 20 * HEIGHT_SCALE, 3.89 * HEIGHT_SCALE, 20 * HEIGHT_SCALE, 0, 1, (0, 0), (1, 1, 1), xoffset=X_OFFSET)

def phi_update(time):
    for line in lines:
        line.update(time)
        line.draw()
    for line in lines:
        line.update_hold(time)
    for line in lines:
        line.update_note(time)
    for line in lines:
        line.update_hit(time)

if format == "rpe":
    bpm = bpm_list[0]["bpm"]

def update_bpm(bpmlist, time):
    if len(bpmlist) == 1:
        return bpm_list[0]["bpm"]
    if time >= bpm_list[0]["time"]:
        bpm_list.pop(0)
        return update_bpm(bpmlist, time)
    return bpm_list[0]["bpm"]

def rpe_update(time):
    bpm = update_bpm(bpm_list, time)
    for line in lines:
        line.update(time)
        line.draw()
    for line in lines:
        line.update_hold(time, bpm, keys)
    for line in lines:
        line.update_note(time, keys)
    for line in lines:
        line.update_hit(time)

ui_state = States.Playing
keys = []

if "--render" not in sys.argv:
    pygame.display.set_caption(f"{CAPTION} | PLAYING")
    music.play()
    _t = - offset 
    start_time = time.time()
    pause = False
    pause_start_time = time.time()
    y_st = time.time()

    if not iszip:
        def clean():
            observer.stop()
            observer.join()

        atexit.register(clean)

        event_handler = TChart()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()

    '''loading_time = 0
    loading = Loading(n_ill, name=name, level=level, composer=composer, charter=charter, illustrator=illustrator, tip=tip)
    ending: Ending = None'''
    while True:
        while not stop:
            clock.tick()

            for event in pygame.event.get():
                """if event.type == pygame.MOUSEMOTION:
                    pos = list(event.pos)
                    pos[1] = WINDOW_HEIGHT - pos[1]
                    print(pos)"""
                if ui_state == States.Playing:
                    if not AUTOPLAY:
                        if event.type == pygame.KEYDOWN:
                            keys.append(event.unicode)
                            if format == 'rpe':
                                now_time = time.time() - start_time - offset
                                bpm = update_bpm(bpm_list, now_time)
                                t = 9999999
                                n = None
                                rt = 9999999
                                rn = None
                                for line in lines:
                                    nt, nn, nrt, nrn = line.note_judge(now_time)
                                    if nt < t and abs(nt) <= 0.18:
                                        t = nt
                                        n = nn
                                    if nrt < rt and abs(nrt) <= 0.08:
                                        rt = nrt
                                        rn = nrn
                                if t != 9999999:
                                    if not (not rn is None and (abs(t)>0.08)):
                                        debug(f"{t if t < 0 else f"+{t}"} | {'perfect' if abs(t) <= 0.08 else ('good' if abs(t) <= 0.16 else 'bad')}")
                                        n.judge(t, now_time)
                                        for line in lines:
                                            line.update_hold(now_time, bpm, keys)
                                            line.update_note(now_time, keys)
                                    elif not rn is None:
                                        rn.judge_dfn = True
                                        debug(f"defend by {"flick" if rn.type == 3 else "drag"}")
                                n = None
                                rn = None
                        if event.type == pygame.KEYUP:
                            try:
                                keys.remove(event.unicode)
                            except:
                                pass
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
                    sys.exit()

            glClear(GL_COLOR_BUFFER_BIT)

            draw_texture(illustration, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 1, 1, 0, 1, (0.5,0.5), (1,1,1), xoffset=X_OFFSET)
            draw_rect(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,WINDOW_WIDTH,WINDOW_HEIGHT,0,0.5,(0.5,0.5),(0,0,0),xoffset=X_OFFSET)
            draw_rect(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,WINDOW_WIDTH,WINDOW_HEIGHT,0,bg_alpha,(0.5,0.5),(0,0,0),xoffset=X_OFFSET)

            match ui_state:
                case 1:
                    pass
                    '''if loading.update():
                        loading = None
                        music.play()
                        _t = - offset
                        start_time = time.time()
                        pause = False
                        pause_start_time = time.time()
                        y_st = time.time()
                        ui_state = States.Playing
                    else:
                        loading.draw()'''

                case 2:
                    if pause:
                        start_time = y_st + (time.time() - pause_start_time)
                    now_time = time.time() - start_time - offset

                    if now_time >= _t:
                        debug(f"FPS | {round(clock.get_fps())}")
                        _t += 1

                    if format == "phi":
                        phi_update(now_time)
                    elif format == "rpe":
                        rpe_update(now_time)

                    update_ui()
                    draw_ui(now_time)

                    if W_LIMIT:
                        draw_texture(illustration, 0, -rill_yfs, 1, 1, 0, 1, (rill_xfs,0), (1,1,1), clip=((rill_xfs,0),(rill_clip+rill_xfs,0),(rill_clip+rill_xfs,1),(rill_xfs,1)))
                        draw_texture(illustration, REAL_WIDTH, -rill_yfs, 1, 1, 0, 1, (1-rill_xfs,0), (1,1,1), clip=((1-rill_clip-rill_xfs,0),(1-rill_xfs,0),(1-rill_xfs,1),(1-rill_clip-rill_xfs,1)))
                        draw_rect(0,0,X_OFFSET,REAL_HEIGHT,0,0.7,(0,0),(0.1,0.1,0.1))
                        draw_rect(REAL_WIDTH,0,X_OFFSET,REAL_HEIGHT,0,0.7,(1,0),(0.1,0.1,0.1))

                    '''if now_time + offset > music_length:
                        lines.clear()
                        music.stop()
                        ending = Ending(n_ill, name, level)
                        ui_state = States.Ending'''

                case 3:
                    pass
                    '''ending.update()
                    ending.draw()'''

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
    if iszip:
        import shutil
        shutil.rmtree(f".\\.temp\\{r}")
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
        draw_rect(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,WINDOW_WIDTH,WINDOW_HEIGHT,0,0.5,(0.5,0.5),(0,0,0),xoffset=X_OFFSET)
        draw_rect(WINDOW_WIDTH/2,WINDOW_HEIGHT/2,WINDOW_WIDTH,WINDOW_HEIGHT,0,bg_alpha,(0.5,0.5),(0,0,0),xoffset=X_OFFSET)

        if format == "phi":
            phi_update(now_time)
        elif format == "rpe":
            rpe_update(now_time)
        update_ui()
        draw_ui(now_time)

        if W_LIMIT:
            draw_texture(illustration, 0, -rill_yfs, 1, 1, 0, 1, (rill_xfs,0), (1,1,1), clip=((rill_xfs,0),(rill_clip+rill_xfs,0),(rill_clip+rill_xfs,1),(rill_xfs,1)))
            draw_texture(illustration, REAL_WIDTH, -rill_yfs, 1, 1, 0, 1, (1-rill_xfs,0), (1,1,1), clip=((1-rill_clip-rill_xfs,0),(1-rill_xfs,0),(1-rill_xfs,1),(1-rill_clip-rill_xfs,1)))
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