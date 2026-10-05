# 3D 动画模板（mplot3d / Three.js / Manim ThreeDScene）

供 `general-knowledge-tutor` Phase 4 调用。3D 只在「空间结构本身承载信息」时启用（旋转、螺旋、场、曲面、轨道）——能用 2D 讲清的不上 3D，避免为炫技增加认知负担。

## 零、选型决策

| 场景 | 首选 | 依赖 | 产物 |
|---|---|---|---|
| 真机渲染动画（零新增依赖） | matplotlib mplot3d → GIF | numpy + matplotlib | .gif，base64 内嵌 HTML 卡 |
| 卡内交互式 3D（可拖拽视角） | Three.js（r128 经典版，CDN） | 仅浏览器（查看时需联网） | 内联 `<script>` |
| 已装 Manim 时的电影级 3D | `ThreeDScene` | manim | .mp4 |
| 数据型 3D（散点/曲面探索） | plotly（可选装进 venv） | plotly | 自包含 .html |

优先级：mplot3d GIF 是兜底主力；Three.js 用于「调参探索」型直觉；其余按需。

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

## 四、plotly 3D（可选，数据探索型）

装进 venv（勿全局）：`pip install plotly` → `fig.write_html("x.html", include_plotlyjs="cdn")`。可缩放旋转、悬停读值，适合曲面/散点云；产物独立 HTML，卡内以链接挂载。

## 五、交付前自检

- [ ] 3D 确实在承载 2D 承载不了的信息（旋转/空间结构），而非装饰。
- [ ] mplot3d 产物真实渲染，GIF 帧数、体积（≤2 MB）达标，相机环绕无缝。
- [ ] Three.js 有 CDN 失败降级文案，静态 GIF 可替代。
- [ ] 深度伪影已缓解（辅助线淡化、主线加粗）。
- [ ] 中文轴标签正常（Microsoft YaHei 前置设置）。
