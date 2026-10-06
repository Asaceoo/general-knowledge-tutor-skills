# Python 可视化速查（matplotlib / plotly / SVG / 交互组件）

供 `general-knowledge-tutor` Phase 4 调用。Manim 之外的兜底与补充手段，全部真实运行。

## A. matplotlib — 数据/分布/关系图（可合成 GIF 降级动画）

```python
import matplotlib.pyplot as plt
import numpy as np

# 中文乱码防线（Windows）：必须在绘图前设置，否则标题/标签变方框
plt.rcParams.update({
    "font.family": ["Microsoft YaHei", "SimHei", "sans-serif"],
    "axes.unicode_minus": False,   # 负号显示
})

x = np.linspace(0, 10, 400)
y = 1 / x
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, y, color="#1f77b4")
ax.axhline(0, color="gray", lw=0.8)
ax.set_xlabel("x"); ax.set_ylabel("y = 1/x")
ax.set_title("极限：x→∞ 时 1/x→0")
fig.savefig("limit_curve.png", dpi=120)
```

**多帧合成 GIF（替代 Manim 动画）**：
```python
import numpy as np                          # 本块可独立复制运行（不依赖上一块）
import matplotlib.pyplot as plt
import matplotlib.animation as ani
fig, ax = plt.subplots()
line, = ax.plot([], [])
def update(i):
    xx = np.linspace(0.5, 9, 200)[:i*10]
    line.set_data(xx, 1/xx[:i*10]); return line,
anim = ani.FuncAnimation(fig, update, frames=20, interval=120)
anim.save("limit.gif", writer="pillow")
```

## B. plotly — 可缩放交互图（分布/三维/关系）

```python
import plotly.express as px
import numpy as np, pandas as pd
df = pd.DataFrame({"x": np.linspace(0,10,100), "y": 1/np.linspace(0.1,10,100)})
fig = px.line(df, x="x", y="y", title="1/x 衰减")
fig.write_html("limit_interactive.html")   # 可嵌入讲解页
```

## C. SVG — 概念图/体系图/依赖 DAG（手写代码保证可缩放）

用字符串拼装 `<svg>`，节点=`<rect>`+`<text>`，边=`<line>`/`<path>`。适合「体系坐标」与「第一性原理拆解树」。交付为 `.svg` 或直接内联进 HTML。

最小模板：
```python
svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="200">
<rect x="40" y="80" width="120" height="40" rx="6" fill="#e8f0fe"/>
<text x="100" y="105" text-anchor="middle" font-size="14">原子事实</text>
<line x1="160" y1="100" x2="260" y2="100" stroke="#333"/>
<rect x="260" y="80" width="120" height="40" rx="6" fill="#d2e3fc"/>
<text x="320" y="105" text-anchor="middle" font-size="14">推理链</text>
</svg>'''
open("dag.svg", "w", encoding="utf-8").write(svg)
```

## D. 交互式 HTML 组件（平台无关）— 可探索参数

用于「调参数看变化」类直觉（指数衰减 λ、学习率 η、复利利率 r）。用 HTML+JS，滑块驱动重绘。

交付方式按运行环境选择（优先级从高到低）：
1. 环境有内联 HTML 组件能力（如 WorkBuddy 的 widget 类工具）→ 以原始 HTML 片段交付（不含 `<html>/<head>/<body>`）。
2. 无内联能力 → 写独立 `.html` 文件，在回复中给出路径，提示用户双击浏览器打开。

要点：
- 用 `<input type="range">` + `<canvas>` 或内联 SVG，JS 监听 `input` 事件实时重算。
- 适配主题：浅色主题下用浅色背景 + 深色文字；不确定主题时用中性配色。

最小骨架：
```html
<canvas id="c" width="480" height="240"></canvas>
<input id="r" type="range" min="0.01" max="0.3" step="0.01" value="0.1">
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
function draw(r){ctx.clearRect(0,0,480,240);ctx.beginPath();
  for(let i=0;i<240;i++){const y=240-Math.exp(-r*i/40)*220;
    i?ctx.lineTo(i,y):ctx.moveTo(i,y);}ctx.stroke();}
document.getElementById('r').oninput=e=>draw(+e.target.value);draw(0.1);
</script>
```

## E. 选择决策

- 要「过程/演化/讲到哪画到哪」→ Manim（首选）或 matplotlib-GIF。
- 要「可缩放探索数据」→ plotly HTML。
- 要「体系/依赖结构」→ SVG / Mermaid。
- 要「调参建直觉」→ 交互式 HTML 组件（交付方式见 D 节）。
- 以上均真实运行产出文件，不交付伪代码。
