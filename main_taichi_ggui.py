import sys, argparse

import taichi as ti

# python3 main_taichi_ggui.py --arch=cpu --body=10 --fps=0
# python3 main_taichi_ggui.py --arch=vulkan --body=1024 --fps=60
# -----------------------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Leapfrog N-Body")

parser.add_argument('-a', '--arch', help='Taichi backend', default="cpu", action="store")
parser.add_argument('-f', '--fps', help='Max FPS, 0 for unlimited', default=0, type=int)
parser.add_argument('-b', '--body', help='NB Body', default=64, type=int)

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

NB_BODY = args["body"]

# -----------------------------------------------------------------------------------------------------------

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 800

# -----------------------------------------------------------------------------------------------------------

EPS = 0.5
DT  = 0.005

CAMERA_POS = ti.Vector([0.0, 0.0, 8.0])

# -----------------------------------------------------------------------------------------------------------

pos = ti.Vector.field(3, dtype=ti.f64, shape=NB_BODY)
vel = ti.Vector.field(3, dtype=ti.f64, shape=NB_BODY)
acc = ti.Vector.field(3, dtype=ti.f64, shape=NB_BODY)
mass = 1.0

# -----------------------------------------------------------------------------------------------------------

# initial distribution
@ti.kernel
def init_pos():
    for i in range(NB_BODY):
        pos[i] = [((ti.random(float) * 2) - 1) * 1.0, ((ti.random(float) * 2) - 1) * 1.0, ((ti.random(float) * 2) - 1) * 1.0]
        vel[i] = [0.0, 0.0, 0.0]
        acc[i] = [0.0, 0.0, 0.0]

# -----------------------------------------------------------------------------------------------------------

# Leapfrog integration
@ti.kernel
def update_pos(dt: ti.f64, eps: ti.f64):

    for i in range(NB_BODY):
        vel[i] += acc[i] * 0.5 * dt
        pos[i] += vel[i] * dt

    # ! only the outer loop is optimized 
    #for i, j in ti.ndrange(NB_BODY, NB_BODY): # does not work on vulkan / opengl ?
    for i in range(NB_BODY):
        for j in range(NB_BODY):
            if i != j:
                DR = pos[j] - pos[i]
                DR2 = ti.math.dot(DR, DR)
                DR2 += eps*eps

                PHI = mass / (ti.sqrt(DR2) * DR2)

                acc[i] += DR * PHI

    for i in range(NB_BODY):
        vel[i] += acc[i] * 0.5 * dt
        acc[i] = [0.0, 0.0, 0.0]  

# -----------------------------------------------------------------------------------------------------------

def show_options(window):
    global DT, EPS

    window.GUI.begin("Options", 0.05, 0.1, 0.2, 0.15)
    DT = window.GUI.slider_float("dt", DT, minimum=0.0, maximum=0.1)
    EPS = window.GUI.slider_float("eps", EPS, minimum=0.01, maximum=1.0)
    window.GUI.end()

# -----------------------------------------------------------------------------------------------------------

def main():

    init_pos()

    window = ti.ui.Window("LeapFrog N-body", res=(SCREEN_WIDTH, SCREEN_HEIGHT), fps_limit=-1, vsync=0)
    canvas = window.get_canvas()

    scene = window.get_scene()

    camera = ti.ui.Camera()
    camera.position(CAMERA_POS.x, CAMERA_POS.y, CAMERA_POS.z)
    camera.lookat(0.0, 0.0, 0.0)
    camera.up(0, 1, 0)
    camera.projection_mode(ti.ui.ProjectionMode.Perspective)
    scene.set_camera(camera)

    canvas.set_background_color((0.1, 0.1, 0.1))
    
    cam_moved = False

    # drawing loop
    while window.running:

        camera.track_user_inputs(window, movement_speed=1.0, hold_key=ti.ui.RMB)

        for e in window.get_events(ti.ui.PRESS):
            if e.key in [ti.ui.ESCAPE]:
                exit()
            if e.key in [ti.ui.DOWN]:
                CAMERA_POS.z += 1.001
                cam_moved = True
            if e.key in [ti.ui.UP]:
                CAMERA_POS.z -= 1.001
                cam_moved = True

        if cam_moved:
            camera.position(CAMERA_POS.x, CAMERA_POS.y, CAMERA_POS.z)
            camera.lookat(0.0, 0.0, 0.0)
            cam_moved = False

        scene.set_camera(camera)

        update_pos(DT, EPS)

        scene.ambient_light((0.8, 0.8, 0.8))
        scene.point_light(pos=(0.5, 1.5, 1.5), color=(1, 1, 1))
        
        scene.particles(pos, radius=0.01, color=(1.0, 1.0, 1.0))
        #canvas.circles(pos, radius=0.001, color=(1, 1, 1))

        canvas.scene(scene)
        show_options(window)

        window.show()

    window.destroy()

if __name__ == "__main__":
    main()