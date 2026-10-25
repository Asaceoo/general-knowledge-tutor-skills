# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "docs", "images")
os.makedirs(OUT, exist_ok=True)

INK = "#0f172a"
MUTED = "#64748b"
BLUE = "#2563eb"
AMBER = "#d97706"
GREEN = "#059669"
PURPLE = "#7c3aed"
ROSE = "#e11d48"
NL = chr(10)

def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax

def box(ax, x, y, w, h, title, lines, ec=BLUE, fc="#ffffff", ts=13, ls=10, gap=0.34):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                linewidth=2, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w / 2, y + h - 0.26, title, ha="center", va="top", fontsize=ts,
            color=INK, weight="bold", zorder=3)
    if lines:
        ax.text(x + w / 2, y + h - 0.26 - gap, NL.join(lines), ha="center", va="top",
                fontsize=ls, color=MUTED, zorder=3, linespacing=1.55)

def arrow(ax, p1, p2, color=MUTED, rad=0.0, lw=2):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=18,
                                 linewidth=lw, color=color,
                                 connectionstyle="arc3,rad=" + str(rad), zorder=1))

def title(ax, y, main, sub):
    ax.text(0.35, y, main, fontsize=21, color=INK, weight="bold", va="top")
    ax.text(0.35, y - 0.52, sub, fontsize=11, color=MUTED, va="top")

# ---------- 图1：五阶段流水线 ----------
def fig_workflow():
    fig, ax = canvas(16, 9)
    title(ax, 8.98, "五阶段学习包流水线", "从「帮我搞懂 X」到一份可自检的结构化学习包：每阶段有明确产出与门控")
    box(ax, 0.55, 6.95, 2.78, 1.02, "Phase 0  意图定位",
        ["结构化选项：深度 / 覆盖", "基础 / 可视化（禁开放式追问）"], ec=MUTED, ts=11, ls=8.4, gap=0.30)
    items = [
        ("Phase 1  第一性原理拆解", ["隐含假设 · 原子事实", "推理链 A+B→C"], BLUE),
        ("Phase 2  体系化知识地图", ["概念依赖 DAG", "跨学科坐标"], PURPLE),
        ("Phase 3  本质理解", ["一句话本质 + 类比", "类比失效边界"], AMBER),
        ("Phase 4  可视化生产", ["Manim / 3D / 交互 HTML", "真机渲染 · 不交伪产物"], GREEN),
        ("Phase 5  结构化交付", ["主卡 + 通俗版", "自检题 + 学习路径"], ROSE),
    ]
    x, w, gap = 0.55, 2.78, 0.25
    for t, ls, c in items:
        box(ax, x, 4.15, w, 2.02, t, ls, ec=c, ts=10.5, ls=8.8, gap=0.34)
        x += w + gap
    for i in range(4):
        x1 = 0.55 + (w + gap) * i + w
        arrow(ax, (x1 + 0.03, 5.16), (x1 + gap - 0.03, 5.16))
    arrow(ax, (1.94, 6.93), (1.94, 6.20))
    box(ax, 0.55, 1.55, 14.9, 1.95, "交付物：一份学习包 = 双文档 + 真实产物 + 自检闭环",
        ["主卡（通识可视化学习卡）· 通俗版 · Manim 动画 · 3D 单文件 HTML · 交互组件",
         "语音讲解 mp3 · 自测 HTML · Anki 记忆卡 · 全部脚本可复跑"], ec=MUTED, fc="#f8fafc", ts=13.5, ls=10, gap=0.62)
    for i in range(5):
        cx = 0.55 + (w + gap) * i + w / 2
        arrow(ax, (cx, 4.13), (cx, 3.54), color="#cbd5e1")
    fig.savefig(os.path.join(OUT, "01-five-phase.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------- 图2：可视化能力矩阵 ----------
def fig_matrix():
    fig, ax = canvas(16, 9.6)
    title(ax, 9.35, "可视化能力矩阵", "同一个知识点，按「它是什么」选工具；每档都有降级链，环境缺依赖也不至于卡死")
    rows = [
        ("过程 / 演化", "Manim 分镜动画", "帧序列 → ffmpeg MP4 → GIF", BLUE),
        ("数据 / 关系", "matplotlib / plotly / ECharts", "SVG 手绘", PURPLE),
        ("场 / 曲面 / 体渲染", "PyVista（深度排序正确）", "mplot3d 多视角 PNG", GREEN),
        ("空间结构 / 旋转", "Blender glb → model-viewer", "trimesh 造 glb / PyVista", AMBER),
        ("可探索参数", "交互 HTML（拖参数 / 拖对象）", "静态多状态图", ROSE),
        ("体系 / 流程 / DAG", "Mermaid 文本即图", "graphviz PNG / 缩进树", MUTED),
    ]
    ax.text(0.85, 7.62, "知识点类型", fontsize=10.5, color=MUTED, weight="bold")
    ax.text(5.40, 7.62, "首选工具", fontsize=10.5, color=MUTED, weight="bold")
    ax.text(11.20, 7.62, "降级链（缺依赖时）", fontsize=10.5, color=MUTED, weight="bold")
    y_top, h, step = 7.35, 0.90, 1.02
    for i, (name, tool, fallback, c) in enumerate(rows):
        y = y_top - h - i * step
        ax.add_patch(FancyBboxPatch((0.55, y), 14.9, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.10",
                                    linewidth=1.4, edgecolor="#e2e8f0", facecolor="#ffffff", zorder=2))
        ax.add_patch(FancyBboxPatch((0.55, y), 0.13, h, boxstyle="square,pad=0",
                                    linewidth=0, facecolor=c, zorder=3))
        ax.text(0.88, y + h / 2, name, fontsize=11.5, color=INK, va="center", weight="bold", zorder=4)
        ax.text(5.40, y + h / 2, tool, fontsize=11, color=c, va="center", weight="bold", zorder=4)
        ax.text(11.20, y + h / 2, fallback, fontsize=10, color=MUTED, va="center", zorder=4)
    box(ax, 0.55, 0.28, 14.9, 0.72,
        "硬规则：用 3D 就必配一张 2D 备选图；交互 / 3D 产物必须能通过 SELFTEST 机器断言",
        [], ec="#cbd5e1", fc="#f8fafc", ts=11)
    fig.savefig(os.path.join(OUT, "02-viz-matrix.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------- 图3：Blender 四道闸 ----------
def fig_gates():
    fig, ax = canvas(15, 9.4)
    title(ax, 9.15, "3D / Blender 调用决策：四道闸",
          "从左到右过闸，任一不通过就走「否则」分支——装了 Blender 也不等于处处用它")
    gates = [
        ("闸① 有空间维度吗？", "2D 会不会丢掉「转一下才能看见」的信息", "否 → 老实做 2D", BLUE),
        ("闸② 是公式 / 数据 / 参数探索？", "反向门控：这类交 Manim、图表、交互 HTML", "是 → 不上 3D", PURPLE),
        ("闸③ 本机有什么？", "blender.exe / trimesh / pyvista / manim 四个都探", "都没有 → mplot3d 兜底", AMBER),
        ("闸④ 质感 / 仿真不可替代？", "场与曲面归 PyVista；光路/机构/流体才轮到 E 层", "否 → PyVista 更快", GREEN),
    ]
    y = 6.75
    for i, (t, sub, no, c) in enumerate(gates):
        box(ax, 0.55, y, 6.5, 1.30, t, [sub], ec=c, ts=12, ls=9.5, gap=0.48)
        box(ax, 8.10, y + 0.29, 3.05, 0.72, no, [], ec="#e2e8f0", fc="#f8fafc", ts=10.2)
        arrow(ax, (7.10, y + 0.65), (8.05, y + 0.65), color="#cbd5e1", lw=1.6)
        if i < len(gates) - 1:
            arrow(ax, (3.80, y - 0.02), (3.80, y - 0.28), color="#94a3b8")
        y -= 1.60
    box(ax, 12.30, 2.55, 2.20, 3.55, "过闸后" + NL + "两种出口",
        ["① glb + model-viewer", "（可拖拽，首选）", "", "② mp4 / gif 录像", "（仅运镜叙事）"],
        ec=ROSE, ts=11, ls=8.6, gap=0.55)
    arrow(ax, (11.20, 3.95), (12.25, 3.95), color=ROSE, lw=2.2)
    fig.savefig(os.path.join(OUT, "03-blender-gates.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------- 图4：真机自检闭环 ----------
def fig_loop():
    fig, ax = canvas(14, 8.6)
    title(ax, 8.35, "真机自检闭环",
          "每条产物都要有机器判据：画布非空、交互真的生效、渲染真的出片——不靠肉眼「看起来对」")
    box(ax, 0.9, 5.15, 3.5, 1.45, "写脚本", ["分镜 / 模板复用", "参数可复跑"], ec=BLUE, ts=12.5, ls=9.2, gap=0.45)
    box(ax, 5.05, 5.15, 3.5, 1.45, "真机执行", ["Blender / Chrome headless", "matplotlib / ffmpeg"], ec=PURPLE, ts=12.5, ls=9.2, gap=0.45)
    box(ax, 9.20, 5.15, 3.9, 1.45, "产物", ["mp4 / png / glb / html", "mp3 / apkg"], ec=AMBER, ts=12.5, ls=9.2, gap=0.45)
    box(ax, 9.20, 2.35, 3.9, 1.45, "机器断言", ["SELFTEST 约定", "画布非空 / 交互生效 / WebGL"], ec=GREEN, ts=12.5, ls=9.2, gap=0.45)
    box(ax, 5.05, 2.35, 3.5, 1.45, "全量回归", ["逐条断言", "PASS / SKIP / FAIL 汇总"], ec=ROSE, ts=12.5, ls=9.2, gap=0.45)
    box(ax, 0.9, 2.35, 3.5, 1.45, "清单兜底", ["改动必查 audit-checklist", "SKIP 须有环境理由"], ec=MUTED, ts=12.5, ls=9.2, gap=0.45)
    arrow(ax, (4.42, 5.87), (5.02, 5.87))
    arrow(ax, (8.57, 5.87), (9.17, 5.87))
    arrow(ax, (11.15, 5.12), (11.15, 3.83))
    arrow(ax, (9.17, 3.07), (8.57, 3.07))
    arrow(ax, (5.02, 3.07), (4.42, 3.07))
    arrow(ax, (2.65, 3.83), (2.65, 5.12), color="#cbd5e1")
    ax.text(0.62, 4.48, "不通过 → 回炉", fontsize=9, color="#94a3b8", rotation=90, va="center")
    fig.savefig(os.path.join(OUT, "04-selftest-loop.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

if __name__ == "__main__":
    fig_workflow()
    fig_matrix()
    fig_gates()
    fig_loop()
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".png"):
            print("OK", f, os.path.getsize(os.path.join(OUT, f)))