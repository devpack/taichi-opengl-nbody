import time, collections
import moderngl as mgl

# ----------------------------------------------------------------------------------------------------------------------

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 800
FONT_SIZE     = 32
CLEAR_ON      = 1

USE_TAICHI = 1

# ----------------------------------------------------------------------------------------------------------------------

NB_BODY = 1024

EPS     = 0.3      # soft
DT      = 1.0/256.0 # time step
EPS2    = EPS * EPS
HALF_DT = 0.5 * DT

# ----------------------------------------------------------------------------------------------------------------------

# drawing mode
#MODE = mgl.LINE_STRIP
MODE = mgl.POINTS
#MODE = mgl.TRIANGLES

# ----------------------------------------------------------------------------------------------------------------------

# camera
CAM_POS = (0, 0, 20)
FOV = 50
NEAR = 0.1
FAR = 2000
SPEED = 0.01
SENSITIVITY = 0.07

GRAB_MOUSE = False
LIGHT_POS = (10, 40, 1000)

# ----------------------------------------------------------------------------------------------------------------------

class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)
