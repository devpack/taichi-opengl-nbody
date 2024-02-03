# taichi-opengl-nbody

- Requirements:

python3 -m pip install taichi pygame ModernGL PyGLM PyOpenGL imgui
 
- pygame + modergl rendering backend:

python3 main.py --arch=cpu --fps=60

python3 main.py --arch=gpu --fps=-1

- Taichi GGUI backend:

python3 main_taichi_ggui.py --arch=cpu --body=256 --fps=-1

python3 main_taichi_ggui.py --arch=gpu --body=1024 --fps=-1

![ggui_test](https://github.com/devpack/taichi-opengl-nbody/blob/main/pics/ggui_test.png)
