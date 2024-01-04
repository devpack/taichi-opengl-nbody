from config import *
import pygame as pg
import numpy as np
import moderngl as mgl
import glm, math
import random, sys

import taichi as ti

# -----------------------------------------------------------------------------------------------------------

@ti.data_oriented
class BodyTi:
    def __init__(self):

        self.pos = ti.Vector.field(3, dtype=ti.f64, shape=NB_BODY)
        self.vel = ti.Vector.field(3, dtype=ti.f64, shape=NB_BODY)
        self.acc = ti.Vector.field(3, dtype=ti.f64, shape=NB_BODY)

        self.mass = 1.0

    @ti.kernel
    def init(self):
        for i in range(NB_BODY):
            self.pos[i] = [((ti.random(float) * 2) - 1) * 8.0, ((ti.random(float) * 2) - 1) * 8.0, ((ti.random(float) * 2) - 1) * 8.0]
            self.vel[i] = [0.0, 0.0, 0.0]
            self.acc[i] = [0.0, 0.0, 0.0]

    @ti.kernel
    def update(self):

        for i in range(NB_BODY):
            self.vel[i] += self.acc[i] * HALF_DT
            self.pos[i] += self.vel[i] * DT

        for i in range(NB_BODY):
            for j in range(NB_BODY):
                if i != j:
                    DR = self.pos[j] - self.pos[i]
                    DR2 = ti.math.dot(DR, DR)
                    DR2 += EPS2

                    PHI = self.mass / (ti.sqrt(DR2) * DR2)

                    self.acc[i] += DR * PHI

        for i in range(NB_BODY):
            self.vel[i] += self.acc[i] * HALF_DT
            self.acc[i] = [0.0, 0.0, 0.0]            

# -----------------------------------------------------------------------------------------------------------

class Body:

    def __init__(self, x, y, z, vx=0.0, vy=0.0, vz=0.0, ax=0.0, ay=0.0, az=0.0, mass=1.0):

        self.x  = x
        self.y  = y
        self.z  = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.ax = ax
        self.ay = ay
        self.az = az

        self.mass = mass

# -----------------------------------------------------------------------------------------------------------

class Bodies:

    def __init__(self, app, nbody_program):
        self.app = app
        self.ctx = app.ctx

        self.nbody_program = nbody_program

        self.m_model = glm.mat4()

        self.nbody_program['m_model'].write(self.m_model)
        self.nbody_program['m_proj'].write(self.app.camera.m_proj)
        self.nbody_program['m_view'].write(self.app.camera.m_view)
        #self.nbody_program['cam_pos'].write(self.app.camera.position)

        if USE_TAICHI:
            self.body_ti = BodyTi()
            self.body_ti.init()

            vertex_data = np.asarray(self.body_ti.pos.to_numpy(), dtype='f4') #vertex_data = np.array(bodies, dtype='f4')

        else:
            self.init_bodies()

            body_pos = [(el.x, el.y, el.z) for el in self.bodies]
            #body_vel = [(el.vx, el.vy, el.vz, 0.0) for el in self.bodies]
            #vertex_data = np.asarray(list(zip(body_pos, body_vel)), dtype='f4') #vertex_data = np.array(bodies, dtype='f4')
            vertex_data = np.asarray(body_pos, dtype='f4') #vertex_data = np.array(bodies, dtype='f4')

        # VBO / VAO
        self.vbo = self.ctx.buffer(data = vertex_data)
        self.vao = self.ctx.vertex_array(self.nbody_program, [(self.vbo, '3f', 'in_position')])

    def calc_bodies(self):
        # leap 1/2
        for body in self.bodies:
            body.vx += body.ax * HALF_DT
            body.vy += body.ay * HALF_DT
            body.vz += body.az * HALF_DT

            body.x += body.vx * DT
            body.y += body.vy * DT
            body.z += body.vz * DT

        # O2
        for pi in self.bodies:
            for pj in self.bodies:
                if pi != pj:
                    DRX = pj.x - pi.x
                    DRY = pj.y - pi.y
                    DRZ = pj.z - pi.z

                    DR2 = DRX * DRX + DRY * DRY + DRZ * DRZ
                    DR2 += EPS2

                    PHI = pj.mass / (math.sqrt(DR2) * DR2)

                    pi.ax += DRX * PHI
                    pi.ay += DRY * PHI
                    pi.az += DRZ * PHI

        # leap 1/2
        for body in self.bodies:
            body.vx += body.ax * HALF_DT
            body.vy += body.ay * HALF_DT
            body.vz += body.az * HALF_DT

            body.ax = body.ay = body.az = 0.0

    def update(self):
        self.nbody_program['m_model'].write(self.m_model)
        self.nbody_program['m_view'].write(self.app.camera.m_view)
        #self.nbody_program['cam_pos'].write(self.app.camera.position)

        if not USE_TAICHI:
            self.calc_bodies()

            body_pos = [(el.x, el.y, el.z) for el in self.bodies]
            #body_vel = [(el.vx, el.vy, el.vz, 0.0) for el in self.bodies]
            #vertex_data = np.asarray(list(zip(body_pos, body_vel)), dtype='f4') #vertex_data = np.array(bodies, dtype='f4')
            vertex_data = np.asarray(body_pos, dtype='f4') #vertex_data = np.array(bodies, dtype='f4')

            self.vbo.write(vertex_data)
        else:
            self.body_ti.update()

            vertex_data = np.asarray(self.body_ti.pos.to_numpy(), dtype='f4')
            self.vbo.write(vertex_data)

    def render(self):
        self.vao.render(mgl.POINTS)

    def destroy(self):
        self.vbo.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.nbody_program[u_name] = u_value
        except KeyError:
            pass

    def init_bodies(self):

        self.bodies = []

        for i in range(0, NB_BODY):
            posx = random.uniform(-1.0, 1.0) * 8.0
            posy = random.uniform(-1.0, 1.0) * 8.0
            posz = random.uniform(-1.0, 1.0) * 8.0
        
            b = Body(posx, posy, posz)
            self.bodies.append(b)
