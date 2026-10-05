# 扩展可视化工具箱与表达方式

供 `general-knowledge-tutor` Phase 4 调用。本文件收录 Manim + 3d-animation.md 之外的扩展手段。准入原则与全技能一致：**真实运行、降级不跳过、能用 2D 讲清不上 3D**。

## 零、依赖探测（一次跑完）

```bash
python -c "import pyvis; print('pyvis OK')"          # 网络/依赖图
python -c "import schemdraw; print('schemdraw OK')"  # 电路/原理示意图
node --version                                        # Motion Canvas 需要 Node
# ECharts / D3 / p5.js / GeoGebra / Desmos：CDN，零安装，查看时需联网
```

未安装的 pip 工具：优先 `pip install`（隔离环境）；装不上 → 走各节的降级链，不阻塞交付。

## 一、ECharts — 图表瑞士军刀（CDN 零依赖，中文生态最好）

填补空白：桑基图、和弦图、热力日历、关系图、3D 柱状——matplotlib 做起来费劲的，ECharts 一段配置搞定。中文标签渲染无乱码问题。

交付方式：写独立 `.html`（含 CDN script + 一个 div + 初始化 JS），或内联进学习卡。CDN 失败 → 显示降级文案 + 指向 matplotlib 静态版。

最小模板（桑基图：能量/资金/注意力流向）：

```html
<div id="chart" style="width:640px;height:400px"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script>
if (typeof echarts === 'undefined') {
  document.getElementById('chart').innerHTML = '<p>⚠ ECharts 未加载（需联网），静态版见备用图。</p>';
} else {
  const c = echarts.init(document.getElementById('chart'));
  c.setOption({
    series: [{
      type: 'sankey', layout: 'none', emphasis: {focus: 'adjacency'},
      data: [{name:'发电'},{name:'工业'},{name:'居民'},{name:'输电损耗'},{name:'有效用电'}],
      links: [
        {source:'发电',target:'输电损耗',value:8},
        {source:'发电',target:'有效用电',value:42},
        {source:'有效用电',target:'工业',value:28},
        {source:'有效用电',target:'居民',value:14},
      ],
    }],
  });
}
</script>
```

降级链：ECharts → matplotlib 对应图（桑基可用 `matplotlib.sankey`，效果打折）→ 分步文字。

## 二、D3.js — 完全自定义交互（CDN 零依赖）

填补空白：力导向网络图、自定义坐标系、复杂联动。比 ECharts 灵活，成本也更高——**能用 ECharts 配置出来就不上 D3**。

最小模板（力导向图）：

```html
<svg id="net" width="640" height="400"></svg>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
if (typeof d3 === 'undefined') {
  document.getElementById('net').outerHTML = '<p>⚠ D3 未加载（需联网）。</p>';
} else {
  const nodes = [{id:'核心'},{id:'前置A'},{id:'前置B'},{id:'延伸'}];
  const links = [{source:1,target:0},{source:2,target:0},{source:0,target:3}];
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(320, 200));
  d3.select('#net').selectAll('line').data(links).join('line')
    .attr('stroke', '#999');
  d3.select('#net').selectAll('circle').data(nodes).join('circle')
    .attr('r', 10).attr('fill', '#4a86e8');
  sim.on('tick', () => {
    d3.selectAll('line')
      .attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
      .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    d3.selectAll('circle').attr('cx',d=>d.x).attr('cy',d=>d.y);
  });
}
</script>
```

降级链：D3 → ECharts 关系图 → pyvis → Mermaid。

## 三、p5.js — 创意编程过程动画（CDN 零依赖）

填补空白：粒子流场、波动传播、生成过程演示——比 matplotlib-GIF 灵活一个量级，浏览器直接跑且可调参。

最小模板（粒子流场：向量场直觉）：

```html
<div id="p5box"></div>
<script src="https://cdn.jsdelivr.net/npm/p5@1/lib/p5.min.js"></script>
<script>
if (typeof p5 === 'undefined') {
  document.getElementById('p5box').innerHTML = '<p>⚠ p5.js 未加载（需联网），静态流线图见备用图。</p>';
} else {
  new p5(function(p){
    const W = 480, H = 320, N = 400;
    let parts = [];
    p.setup = function(){ p.createCanvas(W, H).parent('p5box');
      for (let i=0;i<N;i++) parts.push({x: p.random(W), y: p.random(H)}); };
    function field(x, y){ return {vx: Math.sin(y*0.02), vy: Math.cos(x*0.02)}; } // 示例场
    p.draw = function(){
      p.background(245); p.stroke(40, 40, 180);
      for (const pt of parts){
        const {vx, vy} = field(pt.x, pt.y);
        p.line(pt.x, pt.y, pt.x+vx*4, pt.y+vy*4);
        pt.x = (pt.x + vx + W) % W;   // 环绕边界
        pt.y = (pt.y + vy + H) % H;
      }
    };
  });
}
</script>
```

降级链：p5.js 动画 → matplotlib streamplot 静态流线图 → 矢量小箭头网格 PNG。

## 四、pyvis / graphviz — Phase 2 知识 DAG 专用（pip）

填补空白：Phase 2 依赖图自动布局（手写 SVG 费时且丑）。pyvis 产物是交互 HTML（可拖拽节点）；graphviz 产物是静态 SVG（布局最专业）。

```python
# pyvis：交互式依赖图（pip install pyvis）
from pyvis.network import Network
net = Network(height="400px", width="100%", directed=True, notebook=False)
net.add_nodes(["极限", "函数", "连续", "导数"])           # 延伸层/支撑层按需分层
net.add_edges([("极限", "连续"), ("连续", "导数"), ("函数", "极限")])
net.write_html("dag.html")          # 自包含 HTML（含 CDN，可离线微调）
```

```python
# graphviz：静态专业布局（需系统安装 graphviz 或 pip install graphviz）
from graphviz import Digraph
g = Digraph(format="svg")
g.edges([("极限", "连续"), ("连续", "导数"), ("函数", "极限")])
g.render("dag")                      # dag.svg
```

降级链：pyvis → graphviz SVG → Mermaid → 文本缩进树。

## 五、schemdraw — 电路/原理示意图（pip）

填补空白：电子学、力学、光学原理图的专用表达（元件符号标准、带标签）。

```python
import schemdraw
import schemdraw.elements as elm
with schemdraw.Drawing() as d:
    d += elm.Battery().up().label('10V')
    d += elm.Resistor().right().label('1kΩ')
    d += elm.Capacitor().down().label('10μF')
    d.save('circuit.svg')
```

降级链：schemdraw → SVG 手绘 → 文字分步说明。

## 六、GeoGebra / Desmos — 数学交互 applet（iframe 零代码）

填补空白：「调参看曲线族」「几何变换探索」类直觉——官方 applet 原生支持拖动滑块，零 JS 代码。

- **Desmos**（函数/曲线族）：`<iframe src="https://www.desmos.com/calculator/xxxx?embed" width="640" height="400"></iframe>`
- **GeoGebra**（几何/3D）：`<iframe src="https://www.geogebra.org/material/xxxx/embed" ...></iframe>`

降级链：iframe → 自写滑块 HTML widget → 多状态静态图。

## 七、Motion Canvas — Manim 的现代替代（需 Node）

适用：已有 Node 环境、需要**时间轴级精确控制**的讲解动画（TS 编写，逐帧可编程）。产出 MP4/WebM。

```bash
npm init @motion-canvas@latest   # 创建项目 → npm start（实时预览）→ npm run build
```

```typescript
// src/scenes/example.tsx —— 最小场景
import {makeScene2D, Circle} from '@motion-canvas/2d';
import {createRef} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  const c = createRef<Circle>();
  view.add(<Circle ref={c} size={0} fill="#4a86e8" />);
  yield* c().size(120, 1.2);      // 半径动画 1.2 秒
  yield* c().fill('#e74c3c', 1);   // 颜色渐变 1 秒
});
```

降级链：Motion Canvas → Manim → matplotlib GIF → SVG。

## 八、可视化表达方式（形式层，跨工具）

| 表达方式 | 适用概念 | 实现要点 | 降级 |
|---|---|---|---|
| **Scrollytelling 滚动叙事** | 长推理链（Phase 1 完美适配） | HTML + IntersectionObserver，滚动到哪步亮哪步（A+B→C 逐步点亮） | 编号步骤列表 |
| **小倍数图 small multiples** | 参数族对比（不同 λ/η/r 并排） | matplotlib subplots 统一坐标轴，一眼看趋势 | 单图叠多曲线+图例 |
| **粒子流场** | 向量场、梯度、流体 | p5.js（动）/ PyVista 流线（静） | streamplot 静态图 |
| **物理仿真驱动** | 碰撞、共振、轨道 | vpython / pymunk | 手写关键帧动画 |
| **交互式幻灯** | 可讲解可教学交付 | reveal.js 自包含 HTML（CDN） | Markdown 分节 |
| **手绘白板风** | 降低认知压迫感 | rough.js（CDN，给 SVG 加手绘抖动） | 标准配色 |

## 九、选型速查（扩展工具 vs 现有工具）

- 能量/资金/流程**分流** → ECharts 桑基
- **网络关系** → pyvis（交互）/ D3 力导向（自定义）/ Mermaid（轻量）
- **函数调参探索** → Desmos / GeoGebra iframe（零代码）→ 自写 widget
- **场与流** → p5.js / PyVista
- **电路/光路/力学示意** → schemdraw
- **质感动画** → Blender bpy → Manim → Motion Canvas → matplotlib GIF
- **长推理链** → Scrollytelling
- 以上全部真实运行/真实渲染，CDN 类必须带降级文案。

## 十、交付前自检

- [ ] 每个扩展工具产物真实运行（HTML 可打开、PNG 已落盘、脚本无报错）。
- [ ] CDN 依赖有失败降级文案与静态替代。
- [ ] 选型有据：优先零依赖与既有工具，扩展工具仅在填补空白时启用。
- [ ] iframe 类（GeoGebra/Desmos）已注明需联网，并给出离线替代。
- [ ] 中文显示正常（ECharts 原生 OK；D3/p5 需 CSS 指定字体）。
