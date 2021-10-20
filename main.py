import time
import random
import pygame
import moderngl
from numpy import pi
import pyrr

from engine.model import load_obj, create_skybox
from engine.light import BasicLight
from engine.camera import FirstPersonController
from engine.ui import Image, Text


pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 8)
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
# These two lines creates a "virtual mouse" so you can move it freely
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)
running = True

ctx = moderngl.create_context()
ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
ctx.multisample = True

camera = FirstPersonController(WINDOW_WIDTH / WINDOW_HEIGHT)
camera.noclip = True

light_source = BasicLight()
light_source.ambient_intensity = 0.6


floors = []
for z in range(3):
    for x in range(3):
        floors.append(load_obj(ctx, "assets/models/plane.obj", "assets/textures/wood.png", (x*10, -5, z*10)))

obj = load_obj(ctx, "assets/models/obamium.obj", "assets/textures/obamium.png", (-4, -3.5, -5), flip_texture=True)

obj3 = load_obj(ctx, "assets/models/cube.obj", "assets/textures/green.png", (3, -3.4, 4))
obj3.rotation.x = 0.7
obj3.rotation.z = -0.2

obj4 = load_obj(ctx, "assets/models/sphere.obj", "assets/textures/white.png", (1.0, 0.0, 1.0), unlit=True)

obj6 = load_obj(ctx, "assets/models/wolf.obj", "assets/textures/white.png", (9, -5.2, 6))
obj6.rotation.y = 1.5


img = Image(
    ctx,
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    "assets/textures/crosshair.png",
    (20, 20),
    (0, 0),
    texture_format = "RGBA")

text = Text(
    ctx,
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    (-WINDOW_WIDTH+30, WINDOW_HEIGHT-70),
    "a@@@@@@@@@@@@@@@@",
    font = "SegoeUI",
    font_size = 16,
)

text1 = Text(
    ctx,
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    (-WINDOW_WIDTH+30, WINDOW_HEIGHT-110),
    "a@@@@@@@@@@@@@@@@",
    font = "SegoeUI",
    font_size = 16,
)

text2 = Text(
    ctx,
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    (-WINDOW_WIDTH+30, WINDOW_HEIGHT-150),
    "a@@@@@@@@@@@@@@@@",
    font = "SegoeUI",
    font_size = 16,
)

text.change_text("This meant")
text1.change_text("to be a")
text2.change_text("UI text")


running_sounds = (
    pygame.mixer.Sound("assets/sounds/f1.wav"),
    pygame.mixer.Sound("assets/sounds/f2.wav"),
    pygame.mixer.Sound("assets/sounds/f3.wav"),
    pygame.mixer.Sound("assets/sounds/f4.wav"),
    pygame.mixer.Sound("assets/sounds/f5.wav"),
    pygame.mixer.Sound("assets/sounds/f6.wav"),
    pygame.mixer.Sound("assets/sounds/f7.wav"),
    pygame.mixer.Sound("assets/sounds/f8.wav"),
    pygame.mixer.Sound("assets/sounds/f9.wav"),
    pygame.mixer.Sound("assets/sounds/f10.wav")
)

walking_sounds = (
    pygame.mixer.Sound("assets/sounds/fs0.wav"),
    pygame.mixer.Sound("assets/sounds/fs1.wav"),
    pygame.mixer.Sound("assets/sounds/fs2.wav"),
    pygame.mixer.Sound("assets/sounds/fs3.wav")
)

jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")

last_sound = time.time()
last_i = -1
def walking_sound():
    global last_sound, last_i

    if not camera.noclip and camera.on_ground:
        if camera.is_sprinting and time.time() - last_sound > 0.23:
            last_sound = time.time()

            i = last_i
            while i == last_i:
                i = random.randint(0, 3)
            last_i = i
            running_sounds[i].play()

        elif time.time() - last_sound > 0.47:
            last_sound = time.time()

            i = last_i
            while i == last_i:
               i = random.randint(0, len(walking_sounds)-1)
            last_i = i
            walking_sounds[i].play()


top = pygame.image.load("assets/skybox/generic_top.png").convert((255, 65280, 16711680, 0))
bottom = pygame.image.load("assets/skybox/generic_bottom.png").convert((255, 65280, 16711680, 0))
left = pygame.image.load("assets/skybox/generic_left.png").convert((255, 65280, 16711680, 0))
front = pygame.image.load("assets/skybox/generic_front.png").convert((255, 65280, 16711680, 0))
right = pygame.image.load("assets/skybox/generic_right.png").convert((255, 65280, 16711680, 0))
back = pygame.image.load("assets/skybox/generic_back.png").convert((255, 65280, 16711680, 0))

data = right.get_view("1").raw + left.get_view("1").raw + top.get_view("1").raw + bottom.get_view("1").raw + front.get_view("1").raw + back.get_view("1").raw

cubemap = ctx.texture_cube((900, 900), 3, data)

skybox = create_skybox(ctx, cubemap)


while running:
    clock.tick(60)
    pygame.display.set_caption(f"Pygame OpenGL Experiment  @{clock.get_fps():.4}FPS  —  pygame {pygame.version.ver}  moderngl {moderngl.__version__}")

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == camera.key_map["jump"] and camera.on_ground:
                jump_sound.play()

        elif event.type == pygame.MOUSEWHEEL:
            if camera.on_ground:
                jump_sound.play()

    keys = pygame.key.get_pressed()
    mx, my = pygame.mouse.get_pos()
    rx, ry = pygame.mouse.get_rel()
    ry *= -1

    camera.process(rx, ry, events, keys)

    if camera.is_walking:
        walking_sound()


    ctx.screen.use()
    ctx.screen.clear()

    ctx.disable(moderngl.DEPTH_TEST)
    ctx.front_face = 'cw'
    skybox.update(camera)
    skybox.render()
    ctx.front_face = 'ccw'
    ctx.enable(moderngl.DEPTH_TEST)

    for floor in floors:
       floor.update(camera, light_source)
       floor.render()

    obj.update(camera, light_source)

    obj3.update(camera, light_source)
    obj3.render(skybox)

    obj4.update(camera)
    obj4.render()

    obj6.update(camera, light_source)
    obj6.render()

    ctx.disable(moderngl.DEPTH_TEST)
    img.render()
    text.render()
    text1.render()
    text2.render()
    ctx.enable(moderngl.DEPTH_TEST)

    pygame.display.flip()

pygame.quit()
