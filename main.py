import sys, argparse

import pygame as pg
import numpy as np
import moderngl as mgl
import glm

from camera import Camera
from model import *
from config import *
from shader_program import ShaderProgram
from light import Light

import taichi as ti

# -----------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, max_fps=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_fps = max_fps

        #
        print("NB_BODY=", NB_BODY)

        #
        self.lastTime = time.time()
        self.currentTime = time.time()

        self.fps = FPSCounter()

        self.mode = MODE
        
        # pygame init
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode((self.screen_width, self.screen_height), flags=pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF) # | pg.FULLSCREEN)

        # camera control: keys + mouse
        pg.event.set_grab(GRAB_MOUSE)
        pg.mouse.set_visible(True)
        self.u_scroll = 5.0

        self.forward = False
        self.backward = False
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_button_down = False

        # OpenGL context / options
        self.ctx = mgl.create_context()
        
        if self.mode == mgl.POINTS:
            self.ctx.enable_only(mgl.PROGRAM_POINT_SIZE | mgl.BLEND)

        #self.ctx.wireframe = True
        #self.ctx.front_face = 'cw'
        #self.ctx.enable(flags=mgl.DEPTH_TEST)
        #self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        # light
        self.light = Light(position=LIGHT_POS)

        self.all_shaders = ShaderProgram(self.ctx)
        self.nbody_program = self.all_shaders.get_program("nbody")

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

        # scene object
        self.scene = []

        self.bodies = Bodies(self, self.nbody_program)
        self.scene.append(self.bodies)

        self.ctx.clear(color = (0.0, 0.0, 0.0))

    def destroy(self):
        self.all_shaders.destroy()

        for obj in self.scene:
            obj.destroy()

    def set_uniform(self, program, u_name, u_value):
        try:
            program[u_name] = u_value
        except KeyError:
            pass

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:
            fps = f"FPS: {self.fps.get_fps():3.0f}"
            cam_pos = f"CamPos: {int(self.camera.position.x)}, {int(self.camera.position.y)}, {int(self.camera.position.z)}"
            pg.display.set_caption(fps + " | " + cam_pos)

            self.lastTime = self.currentTime

        self.fps.tick()

    def check_events(self):

        for event in pg.event.get():

            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.destroy()
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.forward = True
                if event.key == pg.K_DOWN:
                    self.backward = True
                if event.key == pg.K_RIGHT:
                    self.right = True
                if event.key == pg.K_LEFT:
                    self.left = True
                if event.key == pg.K_LCTRL:
                    self.up = True
                if event.key == pg.K_LSHIFT:
                    self.down = True
                
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.forward = False
                if event.key == pg.K_DOWN:
                    self.backward = False
                if event.key == pg.K_RIGHT:
                    self.right = False
                if event.key == pg.K_LEFT:
                    self.left = False
                if event.key == pg.K_LCTRL:
                    self.up = False
                if event.key == pg.K_LSHIFT:
                    self.down = False
                    
            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_button_down = True

            if event.type == pg.MOUSEBUTTONUP:
                self.mouse_button_down = False

            if event.type == pg.MOUSEWHEEL: # which, flipped, x, y, touch, precise_x, precise_y
                self.mouse_scroll(event.x, event.y)

            if event.type == pg.MOUSEMOTION:
                mouse_position = pg.mouse.get_pos()
                self.mouse_pos(mouse_position[0], mouse_position[1])

        # mouse camera control
        if self.mouse_button_down:
            mx, my = pg.mouse.get_pos()

            if self.mouse_x:
                self.mouse_dx = self.mouse_x - mx
            else:
                self.mouse_dx = 0

            if self.mouse_y:
                self.mouse_dy = self.mouse_y - my
            else:
                self.mouse_dy = 0

            self.mouse_x = mx
            self.mouse_y = my

        else:
            self.mouse_x = 0
            self.mouse_y = 0
            self.mouse_dx, self.mouse_dy = 0, 0

    def mouse_pos(self, x, y, dx=0, dy=0):
        pass
        #self.set_uniform(self.world_program, 'u_mouse', (x, y))

    def mouse_scroll(self, x, y):
        self.u_scroll = max(1.0, self.u_scroll + y)
        #self.set_uniform(self.world_program, 'u_scroll', self.u_scroll)
        
        #if y == 1:
        #    self.down = True
        #if y == -1:
        #    self.up = True

    def get_time(self):
        return pg.time.get_ticks() * 0.001

    def set_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):

        while True:
            # app.time used for object model motion
            self.set_time()

            # pygame events
            self.check_events()

            self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

            if CLEAR_ON:
                self.ctx.clear(color = (0.0, 0.0, 0.0))

            for obj in self.scene:
                obj.update()
                obj.render()

            pg.display.flip()


            self.delta_time = self.clock.tick(self.max_fps)
            self.get_fps()
            self.num_frames += 1

# -----------------------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="")

parser.add_argument('-a', '--arch', help='Taichi backend', default="cpu", action="store")
parser.add_argument('-f', '--fps', help='Max FPS, 0 for unlimited', default=0, type=int)

result = parser.parse_args()
args = dict(result._get_kwargs())

print("Args = %s" % args)

if args["arch"] in ("cpu", "x64"):
    ti.init(ti.cpu)
elif args["arch"] in ("gpu", "cuda"):
    ti.init(ti.gpu)
elif args["arch"] in ("opengl",):
    ti.init(ti.opengl)
elif args["arch"] in ("vulkan",):
    ti.init(ti.vulkan)

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App(max_fps=args["fps"])
    app.run()

