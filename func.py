import sys, random, unicodedata, math
from OpenGL.GL import *
from OpenGL.GLU import gluDisk
from OpenGL.GLU import gluNewQuadric
from texture import *
from rpe_easings import *

def draw_line(x1:float, y1:float, x2:float, y2:float,width:float,color:tuple[float,float,float,float],xoffset=0):
    glColor4f(*color)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1+xoffset, y1)
    glVertex2f(x2+xoffset, y2)

    glEnd()

def draw_quad(a:tuple[float,float],b:tuple[float,float],c:tuple[float,float],d:tuple[float,float],color:tuple[float,float,float,float]):
    glColor4f(*color)
    glBegin(GL_QUADS)
    glVertex2f(*a)
    glVertex2f(*b)
    glVertex2f(*c)
    glVertex2f(*d)

    glEnd()

def draw_rect(x, y, w, h, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.),xoffset=0):
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    glRotate(r, 0., 0., 1.)
    glBegin(GL_QUADS)
    glTexCoord2f(0.,0.)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1.,0.)
    glVertex2f(w+x_offset, y_offset)
    glTexCoord2f(1.,1.)
    glVertex2f(w+x_offset, h+y_offset)
    glTexCoord2f(0.,1.)
    glVertex2f(x_offset, h+y_offset)
    glEnd()
    glPopMatrix()

def draw_texture(texture: Texture, x, y, sw, sh, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.), clip:tuple[tuple[float]]=((0., 0.), (1., 0.), (1., 1.), (0., 1.)),xoffset=0):
    w, h = texture.width*sw, texture.height*sh
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    glRotate(r, 0., 0., 1.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture.texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(*clip[0])
    glVertex2f(w * clip[0][0]+x_offset, h * clip[0][1]+y_offset)
    glTexCoord2f(*clip[1])
    glVertex2f(w * clip[1][0]+x_offset, h * clip[1][1]+y_offset)
    glTexCoord2f(*clip[2])
    glVertex2f(w * clip[2][0]+x_offset, h * clip[2][1]+y_offset)
    glTexCoord2f(*clip[3])
    glVertex2f(w * clip[3][0]+x_offset, h * clip[3][1]+y_offset)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

def draw_text_texture(texture: Texture, x, y, sw, sh, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.),xoffset=0):
    w, h = texture.width*sw, texture.height*sh
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    y_offset -= (texture.height-75) * sh * (1 - anchor[1])
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    glRotate(r, 0., 0., 1.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture.texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1., 0.)
    glVertex2f(w+x_offset, y_offset)
    glTexCoord2f(1., 1.)
    glVertex2f(w+x_offset, h+y_offset)
    glTexCoord2f(0., 1.)
    glVertex2f(x_offset, h+y_offset)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

def draw_circle(x, y, r, a, color, xoffset=0):
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    gluDisk(gluNewQuadric(), 0, r, 32, 1)
    glPopMatrix()

def get_value(name, default):
    try:
        index = sys.argv.index(f"--{name}")
        return sys.argv[index+1]
    except ValueError:
        return default

def anim(time, st, et, start, end, ease):
    if time < st:
        return start
    if time > et:
        return end
    p = (time - st) / (et - st)
    return start + (end - start) * rpe_easings[ease](p)

def get(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_tip(path):
    with open(path, "r", encoding="utf-8") as f:
        f = f.readlines()
        if len(f) == 0:
            return ''
        tip = f[random.randint(0,len(f)-1)]
        tip = (tip[:-1] if tip[-1] == '\n' else tip)
        return tip

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_chinese(char):
    n = unicodedata.name(char)
    return ('CJK' in n or n == "FULLWIDTH COMMA")

def is_intersection(midpoint, angle, width, height):
    x_mid, y_mid = midpoint
    if angle == 90 or angle == 270:
        return 0 <= x_mid <= width
    if angle == 0 or angle == 180:
        return 0 <= y_mid <= height
    slope = math.tan(angle)
    intercept = y_mid - slope * x_mid
    y_left = slope * 0 + intercept
    y_right = slope * width + intercept
    x_bottom = (0 - intercept) / slope
    x_top = (height - intercept) / slope
    return (0 <= y_left <= height) or (0 <= y_right <= height) or (0 <= x_bottom <= width) or (0 <= x_top <= width)
    # 这是kbw写的。关注B站空吧哇热门手法玩家谢谢喵