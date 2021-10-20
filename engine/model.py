from typing import Union

from pathlib import Path
import struct
import pygame
import moderngl
import pyrr

from .objparser import parse
from .camera import Camera
from .light import BasicLight


PROGRAMS = {}
def _compile_programs(ctx: moderngl.Context, force: bool = False):
    """
    This function caches shader programs for models to use

    'force' keyword recompiles all shaders
    """
    if len(PROGRAMS) == 0 or force:
        PROGRAMS.clear()
        PROGRAMS["default"] = ctx.program(
            vertex_shader   = open("shaders/default.vsh").read(),
            fragment_shader = open("shaders/default.fsh").read()
        )

        PROGRAMS["unlit"] = ctx.program(
            vertex_shader   = open("shaders/unlit.vsh").read(),
            fragment_shader = open("shaders/unlit.fsh").read()
        )

        PROGRAMS["static"] = ctx.program(
            vertex_shader   = open("shaders/static.vsh").read(),
            fragment_shader = open("shaders/static.fsh").read()
        )

        PROGRAMS["skybox"] = ctx.program(
            vertex_shader   = open("shaders/skybox.vsh").read(),
            fragment_shader = open("shaders/skybox.fsh").read()
        )

        PROGRAMS["shadow"] = ctx.program(
            vertex_shader   = open("shaders/shadow.vsh").read(),
            fragment_shader = open("shaders/shadow.fsh").read()
        )

        PROGRAMS["shadowmap"] = ctx.program(
            vertex_shader   = open("shaders/shadowmap.vsh").read(),
            fragment_shader = open("shaders/shadowmap.fsh").read()
        )

        PROGRAMS["debug"] = ctx.program(
            vertex_shader   = open("shaders/debug.vsh").read(),
            fragment_shader = open("shaders/debug.fsh").read()
        )


class BaseModel:
    """
    Base model class
    """
    def __init__(self,
            ctx: moderngl.Context,
            position: tuple[float, float, float],
            texture: str,
            texture_format: str,
            vertices: list[tuple[float, float, float]],
            tex_coords: list[tuple[float, float]],
            norm_coords: list[tuple[float, float, float]],
            flip_texture: bool,
            from_filepath: bool = True,
            build_mipmaps: bool = True):

        self.ctx = ctx
        self.program = PROGRAMS["default"]
        self.shadowmap_program = PROGRAMS["shadowmap"]
        self.debug_program = PROGRAMS["debug"]

        self.rotation = pyrr.Vector3([0.0, 0.0, 0.0])
        self.scale = pyrr.Vector3([1.0, 1.0, 1.0])

        self.texture_format = texture_format
        self.build_mipmaps = build_mipmaps

        self.posmat = pyrr.matrix44.create_from_translation(pyrr.Vector3(position))

        self.model_coords = vertices
        self.texture_coords = tex_coords
        self.norm_coords = norm_coords

        self.create_vao()

        if from_filepath:
            surf = pygame.image.load(texture)
            if flip_texture: surf = pygame.transform.flip(surf, False, True)
            self.surface = surf
        else:
            self.surface = pygame.Surface((1, 1))

        if texture_format == "RGB":
            self.surface = self.surface.convert((255, 65280, 16711680, 0))
        elif texture_format == "RGBA":
            self.surface = self.surface.convert_alpha()

        self.create_texture()

    def create_texture(self):
        self.texture = self.ctx.texture(
            self.surface.get_size(),
            len(self.texture_format),
            pygame.image.tostring(self.surface, self.texture_format, True)
        )

        self.texture.repeat_x = False
        self.texture.repeat_y = False

        #self.texture.anisotropy = 16
        if self.build_mipmaps: self.texture.build_mipmaps()

    def update_texture(self):
        self.texture.write(pygame.image.tostring(self.surface, self.texture_format, True))
        if self.build_mipmaps: self.texture.build_mipmaps()

    def create_vao(self):
        pos = self.ctx.buffer(struct.pack(f"{len(self.model_coords)}f", *self.model_coords))
        uv  = self.ctx.buffer(struct.pack(f"{len(self.texture_coords)}f", *self.texture_coords))
        nor = self.ctx.buffer(struct.pack(f"{len(self.norm_coords)}f", *self.norm_coords))

        if self.program == PROGRAMS["unlit"]:
            self.vao = self.ctx.vertex_array(
                self.program, [
                    (pos, "3f", "a_position"),
                    (uv,  "2f", "a_texture")
                ])
        else:
            self.vao = self.ctx.vertex_array(
                self.program, [
                    (pos, "3f", "a_position"),
                    (uv,  "2f", "a_texture"),
                    (nor, "3f", "a_normal")
                ])

        self.shadow_vao = self.ctx.vertex_array(
            self.shadowmap_program, [
                (pos, "3f", "a_position")
            ])

        self.debug_vao = self.ctx.vertex_array(
            self.debug_program, [
                (pos, "3f", "a_position"),
                (uv,  "2f", "a_texture"),
                (pos, "3f", "a_position")
            ])

    def update(self, camera: Camera, light_source: BasicLight):
        self.program["projection"].value = tuple(camera.projection.flatten())
        self.program["view"].value = tuple(camera.get_view_matrix().flatten())
        self.program["model"].value = tuple(self.posmat.flatten())
        self.program["angle"].value = tuple(self.rotation.tolist())
        self.program["scale"].value = tuple(self.scale.tolist())

        self.program["viewpos"].value = tuple(camera.final_position.tolist())
        self.program["lightpos"].value = tuple(light_source.position.tolist())

        self.program["color"].value = light_source.color
        self.program["ambient_intensity"].value = light_source.ambient_intensity
        self.program["diffuse_intensity"].value = light_source.diffuse_intensity
        self.program["specular_intensity"].value = light_source.specular_intensity
        self.program["specular_power"].value = light_source.specular_power

    def update_shadow(self, camera: Camera, camera2: Camera, light_source: BasicLight):
        self.program["projection"].value = tuple(camera.projection.flatten())
        self.program["view"].value = tuple(camera.get_view_matrix().flatten())
        self.program["model"].value = tuple(self.posmat.flatten())
        self.program["lightprojection"].value = tuple(camera2.projection.flatten())
        self.program["lightview"].value = tuple(camera2.get_view_matrix().flatten())
        self.program["angle"].value = tuple(self.rotation.tolist())
        self.program["scale"].value = tuple(self.scale.tolist())

        self.program["viewpos"].value = tuple(camera.final_position.tolist())
        self.program["lightpos"].value = tuple(light_source.position.tolist())

        self.program["color"].value = light_source.color
        self.program["ambient_intensity"].value = light_source.ambient_intensity
        self.program["diffuse_intensity"].value = light_source.diffuse_intensity
        self.program["specular_intensity"].value = light_source.specular_intensity
        self.program["specular_power"].value = light_source.specular_power

    def update_shadowmap(self, camera: Camera):
        self.shadowmap_program["projection"].value = tuple(camera.projection.flatten())
        self.shadowmap_program["view"].value = tuple(camera.get_view_matrix().flatten())
        self.shadowmap_program["model"].value = tuple(self.posmat.flatten())

    def update_debug(self, camera: Camera):
        self.debug_program["projection"].value = tuple(camera.projection.flatten())
        self.debug_program["view"].value = tuple(camera.get_view_matrix().flatten())
        self.debug_program["model"].value = tuple(self.posmat.flatten())

    def render(self, skybox=None):
        self.texture.use(location=0)
        if skybox: skybox.texture.use(location=1)
        self.vao.render()

    def render_shadow(self):
        self.shadow_vao.render()

    def render_debug(self):
        self.debug_vao.render()


class UnlitModel(BaseModel):
    """
    Unlit model doesn't get effected by any light source
    """
    def __init__(self,
            ctx: moderngl.Context,
            position: tuple[float, float, float],
            texture: str,
            texture_format: str,
            vertices: list[tuple[float, float, float]],
            tex_coords: list[tuple[float, float]],
            norm_coords: list[tuple[float, float, float]],
            flip_texture: bool,
            from_filepath: bool = True,
            build_mipmaps: bool = True):

        super().__init__(
            ctx,
            position,
            texture,
            texture_format,
            vertices,
            tex_coords,
            norm_coords,
            flip_texture,
            from_filepath,
            build_mipmaps)

        self.program = PROGRAMS["unlit"]
        self.create_vao()

    def update(self, camera: Camera):
        self.program["projection"].value = tuple(camera.projection.flatten())
        self.program["view"].value = tuple(camera.get_view_matrix().flatten())
        self.program["model"].value = tuple(self.posmat.flatten())
        self.program["angle"].value = tuple(self.rotation.tolist())
        self.program["scale"].value = tuple(self.scale.tolist())


class StaticModel(BaseModel):
    """
    Static model doesn't get effected by camera view
    mostly meant to be used as UI objects
    """
    def __init__(self,
            ctx: moderngl.Context,
            position: tuple[float, float, float],
            texture: str,
            texture_format: str,
            vertices: list[tuple[float, float, float]],
            tex_coords: list[tuple[float, float]],
            flip_texture: bool,
            from_filepath: bool = True,
            build_mipmaps: bool = False):
        
        super().__init__(
            ctx,
            position,
            texture,
            texture_format,
            vertices,
            tex_coords,
            [0],
            flip_texture,
            from_filepath,
            build_mipmaps)

        self.program = PROGRAMS["static"]
        self.create_vao()

    def create_vao(self):
        pos = self.ctx.buffer(struct.pack(f"{len(self.model_coords)}f", *self.model_coords))
        uv  = self.ctx.buffer(struct.pack(f"{len(self.texture_coords)}f", *self.texture_coords))

        self.vao = self.ctx.vertex_array(
            self.program, [
                (pos, "3f", "a_position"),
                (uv,  "2f", "a_texture"),
            ])


class Skybox:
    def __init__(self, ctx, texture):
        self.ctx = ctx

        objfile = parse("assets/models/cube.obj")

        self.program = PROGRAMS["skybox"]

        self.rotation = pyrr.Vector3([0.0, 0.0, 0.0])
        self.scale = pyrr.Vector3([1.0, 1.0, 1.0])

        self.texture_format = "rgb"

        self.posmat = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0.0]))

        self.model_coords = objfile.vertices
        self.texture_coords = objfile.uv_coords
        self.norm_coords = objfile.vertex_normals

        self.texture = texture

        #self.texture.anisotropy = 4

        self.create_vao()

    def update(self, camera: Camera):
        self.program["projection"].value = tuple(camera.projection.flatten())
        viewmatrix = camera.get_view_matrix()

        viewmatrix[3][0] = 0
        viewmatrix[3][1] = 0
        viewmatrix[3][2] = 0
        self.program["view"].value = tuple(viewmatrix.flatten())
        #self.program["model"].value = tuple(pyrr.matrix44.create_from_translation(camera.position).flatten())#tuple(self.posmat.flatten())

        #self.program["viewpos"].value = tuple(camera.position.tolist())

    def render(self):
        self.texture.use()
        self.vao.render()

    def create_vao(self):
        pos = self.ctx.buffer(struct.pack(f"{len(self.model_coords)}f", *self.model_coords))
        uv  = self.ctx.buffer(struct.pack(f"{len(self.texture_coords)}f", *self.texture_coords))
        nor = self.ctx.buffer(struct.pack(f"{len(self.norm_coords)}f", *self.norm_coords))

        self.vao = self.ctx.vertex_array(
            self.program, [
                (pos, "3f", "a_position"),
            ])


def load_obj(
        ctx: moderngl.Context,
        obj_filepath: Union[Path, str],
        texture_filepath: Union[Path, str],
        position: tuple[float, float, float],
        texture_format: str = "RGB",
        flip_texture: bool = False,
        unlit: bool = False) -> Union[BaseModel, UnlitModel]:

    _compile_programs(ctx)

    objfile = parse(obj_filepath)
    
    if unlit:
        return UnlitModel(
            ctx,
            position,
            texture_filepath,
            texture_format,
            objfile.vertices,
            objfile.uv_coords,
            objfile.vertex_normals,

            flip_texture)
    else:
        return BaseModel(
            ctx,
            position,
            texture_filepath,
            texture_format,
            objfile.vertices,
            objfile.uv_coords,
            objfile.vertex_normals,
            flip_texture)


def create_skybox(ctx, texture):
    return Skybox(ctx, texture)