import pygame
from func import *

class Text:
    def __init__(self, text: str, font: pygame.font.Font, maxwidth = 999999):
        self.text = None
        self.font = font
        self.texture = None
        self.w = 0
        self.h = 0
        self.change_text(text)
        self.attach_line = None
        self.maxwidth = maxwidth

    def render(self, x, y, sw, sh, r, a, anchor=(0, 0), color=(1, 1, 1), time=0):
        if self.texture is not None:
            _size = 1
            if self.w * sw > self.maxwidth:
                _size = (self.maxwidth / (self.w * sw))
            if self.attach_line is None:
                draw_text_texture(self.texture, x, y, sw * _size, sh * _size, r, a, anchor, color)
            else:
                lx, ly, lr, la, lsx, lsy, lc = self.attach_line.get_data(time)
                draw_text_texture(self.texture, x + lx, y + ly, sw * lsx * _size, sh * lsy * _size, r + lr, la, anchor, lc)

    def attach(self, line):
        self.attach_line = line

    def change_text(self, text: str):
        if self.text != text:
            if self.texture is not None:
                glDeleteTextures(1, [self.texture.texture_id])
            text_img = self.font.render(text, True, (255,255,255))
            self.w, self.h = text_img.get_size()
            self.text = text
            self.texture = Texture.from_bytes_with_wh("RGBA", pygame.image.tobytes(text_img, "RGBA"), self.w, self.h)