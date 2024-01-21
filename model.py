from config import *
import pygame as pg
import numpy as np
import moderngl as mgl
import glm, math
import random, sys

import taichi as ti

# -----------------------------------------------------------------------------------------------------------
# dataclass version here: https://github.com/devpack/taichi-tests/blob/main/nbody-dataclass.py

@ti.data_oriented
class NBodySystem:
    def __init__(self, nb_body=8):

        self.nb_body = nb_body

        self.pos = ti.Vector.field(3, dtype=ti.f32, shape=self.nb_body)
        self.vel = ti.Vector.field(3, dtype=ti.f32, shape=self.nb_body)
        self.acc = ti.Vector.field(3, dtype=ti.f32, shape=self.nb_body)

        self.mass = 1.0

    @ti.kernel
    def init(self):
        for i in range(self.nb_body):
            self.pos[i] = [((ti.random(float) * 2) - 1) * 8.0, ((ti.random(float) * 2) - 1) * 8.0, ((ti.random(float) * 2) - 1) * 8.0]
            self.vel[i] = [0.0, 0.0, 0.0]
            self.acc[i] = [0.0, 0.0, 0.0]

    @ti.kernel
    def update(self, dt: ti.f32, eps: ti.f32):

        for i in range(self.nb_body):
            self.vel[i] += self.acc[i] * dt * 0.5
            self.pos[i] += self.vel[i] * dt

        
        # ! only the outer loop is optimized => avoid nested for loops
        #for i, j in ti.ndrange(self.nb_body, self.nb_body):
        for i in range(self.nb_body):
            for j in range(self.nb_body):
                if i != j:
                    DR = self.pos[j] - self.pos[i]
                    DR2 = ti.math.dot(DR, DR)
                    DR2 += eps * eps

                    PHI = self.mass / (ti.sqrt(DR2) * DR2)

                    self.acc[i] += DR * PHI

        for i in range(self.nb_body):
            self.vel[i] += self.acc[i] * dt * 0.5
            self.acc[i] = [0.0, 0.0, 0.0]            

# -----------------------------------------------------------------------------------------------------------

class Simulation:

    def __init__(self, app, nbody_program):
        self.app = app
        self.ctx = app.ctx

        self.nbody_program = nbody_program

        self.m_model = glm.mat4()

        self.nbody_program['m_model'].write(self.m_model)
        self.nbody_program['m_proj'].write(self.app.camera.m_proj)
        self.nbody_program['m_view'].write(self.app.camera.m_view)
        #self.nbody_program['cam_pos'].write(self.app.camera.position)

        self.nbody_system = NBodySystem(nb_body=self.app.nb_body)
        self.nbody_system.init()

        vertex_data = np.asarray(self.nbody_system.pos.to_numpy(), dtype='f4') #vertex_data = np.array(bodies, dtype='f4')

        # VBO / VAO
        self.vbo = self.ctx.buffer(data = vertex_data)
        self.vao = self.ctx.vertex_array(self.nbody_program, [(self.vbo, '3f', 'in_position')])

    def update(self):
        self.nbody_program['m_model'].write(self.m_model)
        self.nbody_program['m_view'].write(self.app.camera.m_view)
        #self.nbody_program['cam_pos'].write(self.app.camera.position)

        self.nbody_system.update(self.app.dt, self.app.eps)

        vertex_data = np.asarray(self.nbody_system.pos.to_numpy(), dtype='f4')
        self.vbo.write(vertex_data)

    def render(self):
        self.vao.render(MODE) # mgl.POINTS)

    def destroy(self):
        self.vbo.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.nbody_program[u_name] = u_value
        except KeyError:
            pass