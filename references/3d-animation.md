# 3D 动画模板（mplot3d / Three.js / Manim ThreeDScene）

供 `general-knowledge-tutor` Phase 4 调用。3D 只在「空间结构本身承载信息」时启用（旋转、螺旋、场、曲面、轨道）——能用 2D 讲清的不上 3D，避免为炫技增加认知负担。

## 零、选型决策（五层）

| 层 | 场景 | 首选 | 依赖 | 产物 |
|---|---|---|---|---|
| A | 零依赖兜底（任何环境可用） | matplotlib mplot3d → GIF | numpy + matplotlib | .gif，base64 内嵌 HTML 卡 |
| B | 质量主力（场/曲面/体渲染，深度排序正确） | PyVista | pip install pyvista | .gif / .png / 交互 .html |
| C | 教学仿真（轨道/波/刚体，几行代码出动画） | vpython | pip install vpython | 自包含 .html（浏览器 3D 可交互） |
| D | 卡内交互式 3D（可拖拽视角） | Three.js（r128 经典版，CDN） | 仅浏览器（查看时需联网） | 内联 `<script>` |
| E | 电影级渲染（质感/运镜/材质） | Blender bpy 无头渲染 | 本机装 Blender 即可（无需 Manim） | .png 序列 → .gif/.mp4 |
| F | 已装 Manim 时的 3D | `ThreeDScene` | manim | .mp4 |
| G | 数据型 3D（散点/曲面探索） | plotly（可选装进 venv） | plotly | 自包含 .html |

优先级：A 永远可用（兜底）；有 pip → 上 B/C；查看者联网 → D；本机有 Blender → E 是质感天花板；F/G 按需。

## 〇、依赖探测

```bash
python -c "import pyvista; print(pyvista.__version__)"    # B 层
python -c "import vpython; print('vpython OK')"            # C 层
blender --version                                           # E 层（本机常见安装路径可直接调用）
python -c "import manim; print(manim.__version__)"         # F 层
```

## 一、mplot3d → GIF（主力，真机渲染）

要点与坑：
- `matplotlib.use("Agg")` + `PillowWriter`，无需任何显示后端。
- **深度排序伪影**：mplot3d 按 artist 添加顺序画，网格线可能穿透曲线——用 `ax.set_zorder` 无法根治，靠淡化辅助元素（alpha≤0.6）+ 粗主线缓解。
- **无缝循环**：让相机方位角 `azim` 匀速转满 360°，首尾帧相机位置重合，即得无缝环绕镜头。
- **体积控制**：dpi 85–95、60 帧、fps 16–20，GIF 控制在 1–2 MB（base64 后 ×1.33）。

模板（傅里叶三维螺旋：e^{iωt}，俯视=旋转，侧视=振荡）：

```python
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

T = 4*np.pi                                   # 两个整周期
t = np.linspace(0, T, 700)
frames = 60
fig = plt.figure(figsize=(6.4, 4.6), dpi=90)
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25); ax.set_zlim(0, T)
ax.set_box_aspect((1, 1, 1.7))
ax.set_xlabel("Re"); ax.set_ylabel("Im"); ax.set_zlabel("t")

# 静态辅助：全螺旋(淡) + 底面投影圆 + 两侧投影墙(虚线)
ax.plot(np.cos(t), np.sin(t), t, color="#95a5a6", lw=0.9, alpha=0.45)
ax.plot(np.cos(t), np.sin(t), 0*t, color="#95a5a6", lw=0.8, ls="--", alpha=0.5)
ax.plot(np.cos(t), -1.25*np.ones_like(t), t, color="#95a5a6", lw=0.8, ls="--", alpha=0.5)
ax.plot(1.25*np.ones_like(t), np.sin(t), t, color="#95a5a6", lw=0.8, ls="--", alpha=0.5)

bright, = ax.plot([], [], [], color="#2471a3", lw=2.4)          # 亮段
tip,   = ax.plot([], [], [], "o", color="#c0392b", ms=6)        # 运动点
dropb, = ax.plot([], [], [], ls="--", color="#95a5a6", lw=0.9)  # 垂落到投影圆
dropc, = ax.plot([], [], [], ls=":",  color="#95a5a6", lw=0.9)  # 投到 y 墙
drops, = ax.plot([], [], [], ls=":",  color="#95a5a6", lw=0.9)  # 投到 x 墙
ttl = ax.set_title("")

def update(i):
    k = int(len(t) * (i + 1) / frames)
    bright.set_data(np.cos(t[:k]), np.sin(t[:k])); bright.set_3d_properties(t[:k])
    x, y, z = np.cos(t[k-1]), np.sin(t[k-1]), t[k-1]
    tip.set_data([x], [y]); tip.set_3d_properties([z])
    dropb.set_data([x, x], [y, y]); dropb.set_3d_properties([z, 0])
    dropc.set_data([x, x], [y, -1.25]); dropc.set_3d_properties([z, z])
    drops.set_data([x, 1.25], [y, y]); drops.set_3d_properties([z, z])
    ttl.set_text("三维螺旋：e$^{iωt}$（俯视=旋转，侧视=振荡）")
    ax.view_init(elev=18, azim=-60 + 360*i/frames)   # 匀速环绕 → 无缝循环
    return bright, tip

anim = FuncAnimation(fig, update, frames=frames, interval=55)
anim.save("helix3d.gif", writer=PillowWriter(fps=18))
```

## 二、Three.js 交互组件（卡内可拖拽 3D）

适用：调参/旋转/缩放探索。用 **r128 经典全局构建**（`three.min.js`，CDN 稳定）；必须写**降级文案**：`if (typeof THREE === 'undefined')` 时提示需联网并指向 GIF 静态版。

骨架：
```html
<div id="box3d"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const box = document.getElementById('box3d');
  if (typeof THREE === 'undefined') {
    box.innerHTML = '<p>⚠ Three.js 未加载（需联网），静态版见上方 GIF。</p>'; return;
  }
  const scene = new THREE.Scene(); scene.background = new THREE.Color(0xffffff);
  const cam = new THREE.PerspectiveCamera(45, 640/360, 0.1, 100);
  const ren = new THREE.WebGLRenderer({antialias:true}); ren.setSize(640,360);
  box.appendChild(ren.domElement);
  // 螺旋线
  const pts = [], T = 4*Math.PI;
  for (let i=0;i<=400;i++){ const t=T*i/400;
    pts.push(new THREE.Vector3(Math.cos(t), Math.sin(t), t/(2*Math.PI)-1)); }
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),
            new THREE.LineBasicMaterial({color:0x2471a3})));
  // 运动点 + 相机自动环绕
  const ball = new THREE.Mesh(new THREE.SphereGeometry(0.05,16,16),
               new THREE.MeshBasicMaterial({color:0xc0392b})); scene.add(ball);
  let t = 0;
  (function loop(){ t += 0.02; const z = t/(2*Math.PI)-1;
    ball.position.set(Math.cos(t), Math.sin(t), z);
    cam.position.set(2.6*Math.cos(t*0.3), 2.6*Math.sin(t*0.3), 1.1);
    cam.lookAt(0,0,0); ren.render(scene,cam); requestAnimationFrame(loop); })();
})();
</script>
```

## 三、Manim ThreeDScene（已装 Manim 时启用）

```python
from manim import *

class Helix3D(ThreeDScene):
    def construct(self):
        ax = ThreeDAxes(x_range=(-2,2,1), y_range=(-2,2,1), z_range=(0,8,2))
        helix = ParametricFunction(
            lambda t: np.array([np.cos(t), np.sin(t), t]),
            t_range=[0, 4*PI], color=BLUE)
        self.set_camera_orientation(phi=75*DEGREES, theta=-60*DEGREES)
        self.add(ax)
        self.play(Create(helix), run_time=4)
        self.begin_ambient_camera_rotation(rate=0.15)   # 自动环绕
        self.wait(3)
# manim -qm scene.py Helix3D
```

## 三-B、PyVista（B 层质量主力：场/曲面/体渲染）

要点与坑：
- **深度排序正确**（基于 VTK），根治 mplot3d 伪影——优先用于场、等值面、流线。
- 离屏渲染需 `pv.OFF_SCREEN = True`；无 GPU 环境可能失败 → 降级 A 层。
- 动画 = 多帧 `plotter.screenshot()` 收集后合成 GIF（pillow）。

模板（标量场切片 + 向量场箭头）：

```python
import numpy as np, pyvista as pv
pv.OFF_SCREEN = True

grid = pv.ImageData(dimensions=(40, 40, 40))
x, y, z = np.meshgrid(*[np.linspace(-2, 2, 40)]*3, indexing="ij")
grid["v"] = np.sin(x*y*z/2)                    # 标量场
vec = np.c_[np.sin(y), np.cos(x), np.zeros_like(x)]  # 向量场
grid["vec"] = vec

p = pv.Plotter(off_screen=True, window_size=(900, 640))
p.add_mesh(grid.slice(normal="z"), cmap="coolwarm")  # 中层切片
arrows = grid.glyph(orient="vec", scale=False, factor=0.15)
p.add_mesh(arrows, color="k", opacity=0.5)
p.screenshot("field_slice.png")
```

## 三-C、vpython（C 层教学仿真：轨道/波/刚体）

要点：
- 产物是**自包含 HTML**（`canvas` + WebGL），浏览器打开即可拖拽视角——天然适合学习卡内嵌。
- 动画由 `rate()` 控制帧率，`sphere/arrow/curve` 等对象即改即动。

模板（行星轨道 + 速度矢量）：

```python
from vpython import sphere, vector, arrow, curve, color, rate
import numpy as np

sun  = sphere(pos=vector(0,0,0), radius=0.5, color=color.yellow)
ball = sphere(pos=vector(5,0,0), radius=0.2, color=color.blue,
              make_trail=True)
v = vector(0, 0.9, 0)
trail = curve(color=color.blue)
dt, G, M = 0.01, 1.0, 100.0
for _ in range(2000):
    r = ball.pos
    a = -G*M*r / r.mag**3                 # 万有引力
    v += a*dt; ball.pos += v*dt
    trail.append(ball.pos)
    arrow(pos=ball.pos, axis=v*0.5, color=color.green)
    rate(100)                              # 100 帧/秒
# 运行后浏览器自动打开 3D 场景；交付时用其导出的 HTML
```

## 三-E、Blender bpy 无头渲染（E 层电影级，本机有 Blender 即用）

要点与坑：
- 命令行无头运行：`blender -b scene.blend -P script.py`（或 `--python-expr`），不弹窗口。
- 每帧渲染 PNG 序列后用 ffmpeg 合成 GIF/MP4：`ffmpeg -framerate 20 -i frame_%03d.png out.gif`。
- 依赖探测：`blender --version`；Windows 常见路径 `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`。
- 首帧材质/灯光配置成本高——只在「质感本身承载说服力」时启用（物理场景、几何结构展示）。

最小脚本（生成旋转立方体 PNG 序列）：

```python
import bpy, math
scene = bpy.context.scene
for f in range(60):
    scene.frame_set(f)
    bpy.data.objects["Cube"].rotation_euler = (0.4, 0.6, 2*math.pi*f/60)
    scene.render.filepath = f"//frame_{f:03d}.png"
    bpy.ops.render.render(write_still=True)
# blender -b -P orbit.py  →  frame_000.png ... frame_059.png
```

## 四、plotly 3D（可选，数据探索型）

装进 venv（勿全局）：`pip install plotly` → `fig.write_html("x.html", include_plotlyjs="cdn")`。可缩放旋转、悬停读值，适合曲面/散点云；产物独立 HTML，卡内以链接挂载。

## 五、交付前自检

- [ ] 3D 确实在承载 2D 承载不了的信息（旋转/空间结构），而非装饰。
- [ ] 选层合理：零依赖任务没上 Blender/PyVista 炫技；质量任务没用 mplot3d 硬扛伪影。
- [ ] mplot3d 产物真实渲染，GIF 帧数、体积（≤2 MB）达标，相机环绕无缝。
- [ ] PyVista 离屏渲染成功；失败已降级 A 层并注明。
- [ ] vpython HTML 在浏览器打开可交互（拖拽视角）。
- [ ] Blender 产物 PNG 序列完整、合成后帧率正常。
- [ ] Three.js 有 CDN 失败降级文案，静态 GIF 可替代。
- [ ] 深度伪影已缓解（辅助线淡化、主线加粗）。
- [ ] 中文轴标签正常（Microsoft YaHei 前置设置）。
