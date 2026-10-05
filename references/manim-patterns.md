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

```bash
# 探测
python -c "import manim; print(manim.__version__)"
# 安装（隔离 venv 优先）
pip install manim            # 需要 system 依赖 cairo/pango/ffmpeg

# 渲染（中等画质，快）
manim -qm scene.py SceneName
# 预览（低画质，最快）
manim -ql scene.py SceneName
# 高清交付
manim -qh scene.py SceneName
```
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
