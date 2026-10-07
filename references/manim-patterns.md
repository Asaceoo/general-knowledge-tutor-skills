# Manim 可视化模板与分镜规范

本文件供 `general-knowledge-tutor` 在 Phase 4 调用。目标是让动画**讲到哪画到哪、节奏贴合朗读**，而非堆特效。

## 一、分镜（Storyboard）格式（务必先写）

在写代码前，先产出镜头列表。每镜要素：
- **镜号**：Shot 1 / 2 / 3 …
- **画面**：这一镜出现/变化的视觉元素（文字、图形、曲线、箭头）。
- **旁白**：该镜对应的讲解词（约 4 字/秒，控制时长）。
- **时长(s)**：旁白字数 / 4，向上取整。
- **动作**：write（逐笔写）/ draw（画）/ transform（变形）/ move（移动）/ highlight（高亮）。

示例（讲解「极限」）：
```
Shot 1 | 画面：标题「极限：无限逼近但不必到达」
        旁白：极限描述的是一个量无限逼近某个值的过程。 时长 4s  动作：write
Shot 2 | 画面：x 轴 + 曲线 y=1/x，动点沿曲线向右下移动
        旁白：比如 x 越大，1/x 越接近 0，但永远不等于 0。 时长 6s  动作：move+draw
Shot 3 | 画面：高亮 y=0 这条渐近线，标注「极限值=0」
        旁白：这个被逼近却不一定到达的值，就是极限。 时长 5s  动作：highlight
```

分镜定稿后再写 `Scene`，保证动画与讲解一一对应。

## 二、环境与渲染

### 2.1 依赖探测必须跨解释器（v1.5.1 起强制）

`python -c "import manim"` 只反映**当前解释器**。实测环境中 PATH 上的 `python` 是一个干净解释器，manim 却装在另一个 venv 里——单解释器探测会返回「无 manim」，让整条链路白白降级到 matplotlib GIF（而实测 manim 渲染 `-ql` 只要 6.6 秒，能力完全可用）。**先扫全部解释器，落成「环境画像」，Phase 4 全程按画像用绝对路径调用：**

```powershell
$pys = @()
$pys += (Get-Command python -All | ForEach-Object { $_.Source })
$pys += (py -0p 2>$null | ForEach-Object { ($_ -split '\s+')[-1] })
$pys += (Get-ChildItem "$env:USERPROFILE\.workbuddy\binaries\python\envs\*\Scripts\python.exe" -EA SilentlyContinue).FullName
$pys += (Get-ChildItem "$env:USERPROFILE\anaconda3\envs\*\python.exe" -EA SilentlyContinue).FullName
$probe = 'import importlib.util as u; print([m for m in ["manim","pyvista","vpython","pymunk","edge_tts","genanki","matplotlib"] if u.find_spec(m)])'
foreach ($p in ($pys | Sort-Object -Unique)) {
  if (Test-Path $p) { Write-Output ("$p  ==>  " + (& $p -c $probe)) }
}
```

> 实测依赖可能**跨环境分布**：manim 在 A 环境，pyvista / vpython / pymunk / edge-tts / genanki 在 B 环境。按能力分别调用各自解释器，不要为了「统一」而重复安装。`py -0p` 只列注册过的安装、PATH 只列 PATH 上的——两者都会漏掉 venv，必须补目录扫描。

### 2.2 LaTeX（公式类主题的硬依赖，v1.5.1 新增）

`MathTex` / `Tex` 需要系统级 `latex` + `dvisvgm`，**只装 manim 不够**，而本节原先只提 cairo/pango/ffmpeg。探测：

```bash
python -c "import shutil; print(shutil.which('latex'), shutil.which('dvisvgm'))"
```

两者为 `None` 时 `MathTex` 直接渲染失败（实测：报错退出、无任何产物）。实测本机装了 MiKTeX 但 bin 不在 PATH，加上即恢复渲染：

```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;$env:PATH"   # 会话级；永久生效用 setx / 系统环境变量
```

装不了 LaTeX 时的降级顺序：`MathTex` → `Text` + Unicode 数学符号 → matplotlib mathtext 渲成 PNG 再用 `ImageMobject` 插入（三步都必须真实渲染验证）。

### 2.3 两段式渲染（替代「3 分钟硬阈值」）

第一段 `-ql` 出样片（秒级）确认构图/节奏/字体，第二段 `-qm`/`-qh` 只跑一次交付档。迭代期**保留缓存**，`--disable_caching` 只在需要强制重渲时用。

```bash
# 安装（隔离 venv 优先）
pip install manim            # 需要 system 依赖 cairo/pango/ffmpeg

# 渲染（中等画质，快）
manim -qm scene.py SceneName
# 预览（低画质，最快）
manim -ql scene.py SceneName
# 高清交付
manim -qh scene.py SceneName
```

> **音频（SoX）**：manim 自带音频合成依赖 SoX，缺失时渲染开头会警告 `SoX could not be found`（不影响画面）。配音不要走这条路——用 `references/extended-viz-2.md` 的 edge-tts + ffmpeg 合体管线（不依赖 SoX）。

产物在 `./media/videos/scene/.../SceneName.mp4`。渲染后确认文件存在且大小合理（>10KB）再交付。

## 三、可复用场景模板

### 模板 A：逐笔写出 + 标题（最常用，概念/定义讲解）

```python
from manim import *

class ConceptWrite(Scene):
    def construct(self):
        title = Text("极限：无限逼近而不必到达", font_size=34)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        body = Text(
            "极限描述一个量\n无限逼近某值的过程",
            font_size=28, line_spacing=1.2,
        )
        self.play(Write(body))
        self.wait(2)
        self.play(FadeOut(body))
```

### 模板 B：几何/曲线绘制 + 标注（过程、函数、证明）

```python
from manim import *

class CurveDraw(Scene):
    def construct(self):
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 1.2, 0.2],
                  x_length=8, y_length=4,
                  axis_config={"font_size": 18})
        ax_labels = ax.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(ax), Write(ax_labels))

        curve = ax.plot(lambda x: 1 / x, x_range=[0.5, 9],
                        color=BLUE)
        self.play(Create(curve), run_time=2)

        # 动点沿曲线逼近
        dot = Dot(color=RED).move_to(ax.c2p(1, 1))
        self.play(dot.animate.move_to(ax.c2p(8, 1/8)), run_time=3)
        self.wait(1)
```

### 模板 C：变形/对比（两个概念差异、状态切换）

```python
from manim import *

class TransformDemo(Scene):
    def construct(self):
        a = Square(side_length=2, color=BLUE).shift(LEFT)
        b = Circle(radius=1, color=GREEN).shift(RIGHT)
        self.play(Create(a), Create(b))
        self.play(Transform(a, b.copy().shift(LEFT)))   # 方形变圆，演示"形态切换"
        self.wait(1)
```

### 模板 D：分步推导（推理链，逐行出现）

```python
from manim import *

class Derivation(Scene):
    def construct(self):
        steps = [
            MathTex(r"f'(x)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}"),
            MathTex(r"=\lim_{h\to0}\frac{(x+h)^2-x^2}{h}"),
            MathTex(r"=\lim_{h\to0}(2x+h)"),
            MathTex(r"=2x"),
        ]
        for i, s in enumerate(steps):
            s.to_edge(UP).shift(DOWN * i * 0.9)
            self.play(Write(s))
            self.wait(1.2)
```

> 中文场景用 `Text`，公式用 `MathTex`/`Tex`。字体缺失时 Manim 会回退默认字体，不影响渲染。

## 四、降级方案（无 Manim 时）

1. 优先 `matplotlib` 画多帧 PNG 再合成 GIF（见 visualization-cookbook.md）。
2. 几何/图类用 **SVG** 代码生成静态图，配文字分步说明替代动画。
3. 文内明确标注「本应动画呈现，已降级为静态图」，保持诚实。

## 五、自检清单（交付前）

- [ ] 分镜已先于代码写好，且旁白时长≈朗读时长。
- [ ] 脚本真实渲染产出 mp4，文件存在且可播放。
- [ ] 每镜「画面」与「旁白」对应，无空镜/废镜。
- [ ] 中文显示正常（无方框乱码）。
- [ ] 动画服务于「讲清本质」，而非炫技。
