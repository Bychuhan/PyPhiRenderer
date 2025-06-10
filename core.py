from OpenGL import error
import pygame
from func import *
from const import *
import log
pygame.init()

class Text:
    def __init__(self, text: str, font: pygame.font.Font, maxwidth = 999999, letter_spacing=0):
        self.text = None
        self.font = font
        self.texture = None
        self.w = 0
        self.h = 0
        self.letter_spacing = letter_spacing
        self.change_text(text)
        self.attach_line = None
        self.maxwidth = maxwidth

    def render(self, x, y, sw, sh, r, a, anchor=(0, 0), color=(1, 1, 1), time=0):
        if self.texture is not None:
            _size = 1
            if self.w * sw > self.maxwidth:
                _size = (self.maxwidth / (self.w * sw))
            if self.attach_line is None:
                draw_text_texture(self.texture, x, y, sw * _size, sh * _size, r, a, anchor, color, xoffset=X_OFFSET)
            else:
                lx, ly, lr, la, lsx, lsy, lc = self.attach_line.get_data(time)
                draw_text_texture(self.texture, x + lx, y + ly, sw * lsx * _size, sh * lsy * _size, r + lr, la, anchor, lc, xoffset=X_OFFSET)

    def attach(self, line):
        self.attach_line = line

    def change_text(self, text: str):
        if self.text != text:
            if self.texture is not None:
                glDeleteTextures(1, [self.texture.texture_id])
            w = -self.letter_spacing
            for char in text:
                w += self.font.size(char)[0]+self.letter_spacing
            text_img = pygame.Surface((max(0, w), self.font.size(text)[1]), pygame.SRCALPHA)
            x = 0
            for char in text:
                char_surface = self.font.render(char, True, (255, 255, 255))
                text_img.blit(char_surface, (x, 0))
                x += char_surface.get_width() + self.letter_spacing
            self.w, self.h = text_img.get_size()
            self.text = text
            try:
                self.texture = Texture.from_bytes_with_wh("RGBA", pygame.image.tobytes(text_img, "RGBA"), self.w, self.h)
            except error.GLError:
                log.error("Text 纹理过大")
                self.texture = Texture.from_bytes_with_wh("RGBA", pygame.image.tobytes(pygame.Surface((0,0), pygame.SRCALPHA), "RGBA"), 0, 0)