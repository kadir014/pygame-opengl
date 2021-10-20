import moderngl
import pygame

from .model import StaticModel


class Image:
    def __init__(self,
            ctx: moderngl.Context,
            window_size: tuple[float, float],
            texture_filepath: str,
            size: tuple[float, float],
            position: tuple[float, float],
            texture_format: str = "RGB",
            flip_texture: bool = False):

        self.window_size = window_size

        x = size[0] / window_size[0]
        y = size[1] / window_size[1]

        self.x, self.y = position

        v0 = -x, -y, 0
        v1 = x, -y, 0
        v2 = -x, y, 0
        v3 = x, y, 0

        model_coords = [
            *v1, *v2, *v0, *v1, *v3, *v2
        ]

        texture_coords = [
            1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1
        ]

        self._model = StaticModel(
            ctx,
            (0.0, 0.0, 0.0),
            texture_filepath,
            texture_format,
            model_coords,
            texture_coords,
            flip_texture)

        self._model.program["pos_x"].value = self.x / self.window_size[0]
        self._model.program["pos_y"].value = self.y / self.window_size[1]

    def render(self):
        self._model.program["pos_x"].value = self.x / self.window_size[0]
        self._model.program["pos_y"].value = self.y / self.window_size[1]
        self._model.render()


class Text:
    def __init__(self,
            ctx: moderngl.Context,
            window_size: tuple[float, float],
            position: tuple[float, float],
            text: str,
            font: str = "Arial",
            font_size: int = 20):

        self.window_size = window_size

        self.font = font
        self.font_size = font_size
        self.text = text

        self._render_text()

        x = self.surface.get_width() / window_size[0]
        y = self.surface.get_height() / window_size[1]
        self._w = self.surface.get_width()
        self._h = self.surface.get_height()

        self.x, self.y = position

        v0 = -x, -y, 0
        v1 = x, -y, 0
        v2 = -x, y, 0
        v3 = x, y, 0

        model_coords = [
            *v1, *v2, *v0, *v1, *v3, *v2
        ]

        texture_coords = [
            1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1
        ]

        self._model = StaticModel(
            ctx,
            (0.0, 0.0, 0.0),
            None,
            "RGBA",
            model_coords,
            texture_coords,
            False,
            from_filepath = False)

        self._render_text()
        self._model.surface = self.surface
        self._model.create_texture()

    def _render_text(self):
        self.fontobj = pygame.font.SysFont(self.font, self.font_size)
        self.surface = self.fontobj.render(self.text, True, (255, 255, 255)).convert_alpha()

    def change_text(self, text: str):
        self.text = text
        self._render_text()
        self._model.surface.fill((0, 0, 0, 0))
        self._model.surface.blit(self.surface, (0, 0))
        self._model.update_texture()

    def render(self):
        self._model.program["pos_x"].value = (self.x+self._w) / self.window_size[0]
        self._model.program["pos_y"].value = (self.y+self._h) / self.window_size[1]
        self._model.render()