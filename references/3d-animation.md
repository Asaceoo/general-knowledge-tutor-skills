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
- **质量档开关（v1.5.1 新增，真机实测可用）**：`enable_anti_aliasing('ssaa')` 抗锯齿、`enable_depth_peeling(64)` **透明体正确排序**、`enable_shadows()`、`enable_ssao()`、`enable_eye_dome_lighting()`。半透明面片互相穿透时**必须开 depth peeling**——否则会出现与 mplot3d 同类的伪影，「靠淡化辅助元素缓解」那套将就做法不该用在 B 层。
- 动画 = 多帧 `plotter.screenshot()` 落帧后用 **ffmpeg 合成 MP4**（优先，体积约为 GIF 的 1/5）或 pillow 合成 GIF（仅循环展示用）。`plotter.open_movie()` 需要 imageio/av 后端，缺装时直接走帧序列 + ffmpeg（实测有的环境两者都没装，`open_movie` 不可用）。
- 完整可复制模板见文末「附：PyVista 质量档」。

模板（标量场切片 + 向量场箭头）：

```python
import numpy as np, pyvista as pv
pv.OFF_SCREEN = True

grid = pv.ImageData(dimensions=(40, 40, 40))
x, y, z = np.meshgrid(*[np.linspace(-2, 2, 40)]*3, indexing="ij")
grid["v"] = np.sin(x*y*z/2).ravel(order="F")   # 标量场：ImageData 点序为 F-order，多维数组必须显式 ravel，否则新版 pyvista 报 "Number of scalars (40)" 不匹配
vec = np.c_[np.sin(y).ravel(order="F"), np.cos(x).ravel(order="F"),
            np.zeros_like(x).ravel(order="F")]  # (N,3) 向量场：np.c_ 前必须先 ravel，否则形状 (40,40,120) 报错
grid["vec"] = vec   # (N,3) 形状的向量场可整体赋值

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
- 坑（2026-10-06 实测）：vpython 依赖 `pkg_resources`，而 **setuptools ≥81 已移除该模块**（Python 3.13 新环境默认装到 84.x 就会 `ModuleNotFoundError: No module named 'pkg_resources'`）→ 先 `pip install "setuptools<81"` 再装 vpython。

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

## 三-E、Blender 无头渲染（E 层电影级，v1.5.3 起真机验证）

要点与坑（Blender **5.2.2 LTS** 实测，2026-10-07）：

- **`bpy` 不是一个 pip 包的问题**：两条完全不同的路径——① 本机装了 Blender **应用** → 用 `blender -b ... -P script.py`（推荐，**不需要** `pip install bpy`）；② 只有 Python 环境 → 才需要那个 330MB 的 `bpy` wheel（且与 Python 版本强绑定）。**不要因为「pip 里没有 bpy」就断定本机没有 Blender。**
- 无头调用：`blender -b --factory-startup -P script.py`。`--factory-startup` 跳过用户插件与偏好，启动更快、结果可复现；漏了 `-b` 会弹窗口。
- **探测（Windows）**：`blender.exe` 通常**不在 PATH**，必须查注册表 + 常见目录：

```powershell
Get-Command blender -EA SilentlyContinue
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
                 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -EA SilentlyContinue |
  Where-Object { $_.DisplayName -like '*Blender*' } | Select-Object DisplayName, DisplayVersion, InstallLocation
Get-Item 'C:\Program Files\Blender Foundation\*\blender.exe' -EA SilentlyContinue
```

- **引擎选择**：`scn.render.engine` 可直接赋 `'BLENDER_EEVEE'`（实测可用）；`'CYCLES'` 同样**可用**（`bpy.app.build_options.cycles = True`）。**但不要用 `RenderSettings.bl_rna.properties['engine'].enum_items` 判断可用性**——实测它只返回 `['BLENDER_EEVEE']`，**会漏报 Cycles**（该枚举是动态的）。判断方式就是赋值 + `try`。
- **无头可用性**：本机 `-b` 下 EEVEE 正常（有 GPU/GL 上下文）；若某环境 EEVEE 报上下文错误，改 `scn.render.engine = 'CYCLES'` + `scn.cycles.device = 'CPU'` 兜底（Cycles 纯 CPU，不依赖显示设备）。
- **实测性能**（320×180、简单场景、含 Blender 启动）：EEVEE 首帧 ~1.0 s、后续 **~0.16 s/帧**（12 帧 2.8 s，整轮墙钟 5.1 s）；Cycles CPU 8 采样 ~0.2 s/帧。**所以它并不「慢」**，慢的是高分辨率/多采样/复杂材质——先用小分辨率出样片再抬规格。
- 合成：`ffmpeg -framerate 12 -i f_%03d.png -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" out.mp4`（libx264 要求宽高偶数，见同款坑）。
- **启用门槛**：只在「质感本身承载说服力」时用（材质/金属/光照/运镜/体积），概念类讲解继续 Manim/PyVista——E 层是最高成本档，别当默认。

### 3-E.1 适用 / 不适用对照表（v1.5.4 新增，防止「有 Blender 就到处用」）

**只在「信息本身依赖质感 / 体积 / 真实仿真 / 运镜」时上 E 层。** 下列能力经本机探测确认独有：Cycles 已编译、烟/火（`quick_effect_add`）、Mantaflow 流体（`fluid_add`）、刚体/布料/粒子、glTF 与 USD 导出、Grease Pencil 全部可用。

**适用**：

| 学科 | 典型主题 | 用哪一样 |
|---|---|---|
| 物理·光学 | 棱镜色散、透镜成像、全内反射、焦散 | **Cycles 光线追踪**（光线真的按折射率拐弯，示意图替代不了） |
| 物理·天文 | 月相与日食阴影、潮汐锁定、轨道共振 | 真实光照与阴影 + 精确轨道几何 |
| 化学·生物 | DNA/蛋白质螺旋、金刚石晶格、NaCl 晶胞、病毒衣壳对称性 | 精确建模 + 材质区分元素/链 |
| 工程·机械 | 齿轮传动、凸轮、连杆机构、差速器 | **刚体约束仿真**（算出来的运动学，不是手绘动画） |
| 数学 | 莫比乌斯环、克莱因瓶、极小曲面、拓扑变形 | 网格精度 + 材质表现「不可定向」 |
| 流体·气象 | 涡环、烟羽、绕流尾迹、云 | **Mantaflow 流体/烟雾**（数值仿真） |
| 材料·地质 | 晶体生长、断层错动、岩层褶皱 | 体积 + 程序化纹理 |

**不适用（照旧守「2D 能讲清就不上 3D」）**：

| 场景 | 该用谁 |
|---|---|
| 概念定义、体系 DAG | Mermaid / SVG |
| 数据分布、关系图 | matplotlib / plotly |
| **公式推导、逐步讲解** | Manim（「讲到哪画到哪」是它的强项，Blender 做这个又慢又别扭） |
| 场 / 曲面 / 体数据可视化 | **PyVista**（更科学、深度正确、更快） |
| 参数拖动探索 | 交互 HTML / Desmos |
| 网页内拖拽 3D | Three.js / vpython / model-viewer |

> 一句话边界：**E 层默认产物是不可交互的录像**——想让人自己转着看，走 §3-E.2 的 glb 路线。

最小脚本（可复制运行；本块由回归用 `blender -b --factory-startup -P` **真机执行**）：

```python
import bpy, math, os
scn = bpy.context.scene
scn.render.engine = 'BLENDER_EEVEE'          # 不可用时改 'CYCLES' + scn.cycles.device='CPU'
scn.render.resolution_x, scn.render.resolution_y = 320, 180   # 先小后大：样片 → 交付
scn.render.image_settings.file_format = 'PNG'
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_blender_frames')
os.makedirs(out, exist_ok=True)
obj = bpy.data.objects.get('Cube')            # --factory-startup 自带 Cube/Camera/Light
if obj:
    obj.rotation_mode = 'XYZ'
scn.frame_start, scn.frame_end = 1, 8
for f in range(1, 9):
    scn.frame_set(f)
    if obj:
        obj.rotation_euler = (0.4, 0.6, 2 * math.pi * f / 8)
    scn.render.filepath = os.path.join(out, f'f_{f:03d}.png')
    bpy.ops.render.render(write_still=True)
print('FRAMES', len([n for n in os.listdir(out) if n.endswith('.png')]))
# blender -b --factory-startup -P blender_frames.py   →  f_001.png ... f_008.png
# ffmpeg -y -framerate 12 -i _blender_frames/f_%03d.png -c:v libx264 -pix_fmt yuv420p \
#        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" out.mp4
```

### 3-E.2 Blender → glb → model-viewer：同一场景的「可交互」出口（v1.5.4，真机实测）

E 层的 mp4 只能看；要让读者**自己转着看**，Blender 可直接导出带材质的 glb（`io_scene_gltf2` 内置）。三步：

```bash
# 1) Blender 内导出。曲线对象必须先转网格，glTF 只吃 mesh：
#    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
#    bpy.context.view_layer.objects.active = ob; bpy.ops.object.convert(target='MESH')
#    bpy.ops.export_scene.gltf(filepath='model.glb', export_format='GLB')

# 2) 取渲染库（v3.5.0 是 ES 模块，必须用 <script type="module">；内联后离线可用）
curl -L -o model-viewer.min.js \
  https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js

# 3) 用 references/templates/model-viewer-template.html 组装单文件：
#    __MODEL_VIEWER_JS__ ← min.js 全文（实测 913 KB；文件内无 </script 字面量，可安全内联）
#    __GLB_SRC__         ← "data:model/gltf-binary;base64," + base64(glb)
#    __TITLE__           ← 主题标题
```

**实测（傅里叶相量螺旋 · Blender 5.2.2 · 220 点 + bevel_resolution 2）**：

| 环节 | 数据 |
|---|---|
| glb | **288 KB**（base64 后 385 KB） |
| 内联 model-viewer | 913 KB |
| 单文件 HTML | **1.29 MB**，断网双击可开（拖拽旋转 / 滚轮缩放 / 自动旋转） |
| 真机断言 | `python scripts/selftest_web.py <产物>` → PASS：组件已注册 / glb 已解析 / **画布非空(像素)** |

**两条实测坑**：

1. **曲线不转网格 = 静默丢几何**：`CURVE` 不在 glTF 导出范围内，不报错，只是导出的模型少几条线。
2. **`modelIsVisible` 在 headless 下可能恒为 false**——这是环境信号，**判 `skip` 不判 `fail`**（同 SELFTEST 约定第 0 条）；真正证明「画出来了」用 `mv.toDataURL()` 的长度（空画布极小）。

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
- [ ] 深度伪影已缓解（辅助线淡化、主线加粗）；**透明/体渲染场景已开 `enable_depth_peeling`**，不是只靠淡化硬扛。
- [ ] 中文轴标签正常（Microsoft YaHei 前置设置）。
- [ ] 动画产物优先 MP4（帧序列 + ffmpeg）；GIF 仅用于循环场景且体积 ≤2 MB。
- [ ] 交互类 HTML（Three.js / vpython / model-viewer）已确认离线可用（CDN 内联或本地 assets），否则明确标注「查看需联网」。
- [ ] 交互类 HTML 已通过 `python scripts/selftest_web.py <产物>` 自测（非空 + 交互生效 + WebGL 可渲染；见 extended-viz-2.md §6）。

---

## 附：PyVista 质量档（v1.5.1 新增，真机实测）

半透明 / 体渲染场景直接复制本模板起手：

```python
import pyvista as pv
pv.OFF_SCREEN = True

p = pv.Plotter(off_screen=True, window_size=(900, 640))
p.enable_anti_aliasing("ssaa")      # 抗锯齿：ssaa 质量最好，fxaa 最快
p.enable_depth_peeling(64)          # 透明体深度排序（不开则半透明面片互相穿透）
p.add_mesh(pv.Sphere(theta_resolution=48, phi_resolution=48),
           color="lightblue", opacity=0.85)
p.add_mesh(pv.Cylinder(direction=(1, 0, 0)), color="tomato", opacity=0.6)
p.camera_position = "xy"
p.screenshot("pv_quality.png")
p.close()
print("quality preset ok")
```

帧序列 → MP4（实测 40 帧 360×240：GIF 104.6 KB vs MP4 19.4 KB）：

```bash
# 逐帧 plotter.screenshot(f"frame_{i:03d}.png") 之后：
ffmpeg -y -framerate 20 -i frame_%03d.png -c:v libx264 -pix_fmt yuv420p \
       -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" out.mp4
```

> **libx264 要求宽高均为偶数**：奇数尺寸（如 360×225）会直接报 `height not divisible by 2` 并让整条编码失败，务必带 `-vf scale=trunc(iw/2)*2:trunc(ih/2)*2`。
