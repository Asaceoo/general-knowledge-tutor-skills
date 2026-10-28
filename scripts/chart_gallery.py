# -*- coding: utf-8 -*-
"""图表画廊：真实渲染全部图表，作为 references/chart-catalog.md 的可执行证据。

用法：python scripts/chart_gallery.py
输出：docs/images/charts/<类型>.png + docs/images/charts/_gallery.png（拼版）
"""
import os
import re
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge
from matplotlib.sankey import Sankey

plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
# 关键：networkx / sankey 等库会显式请求 "sans-serif"，只设 font.family 不够，
# 必须同时把 font.sans-serif 指向中文字体，否则标签回落 DejaVu Sans 变成方框（实测）。
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "docs", "images", "charts")
os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, GREEN, PURPLE, ROSE, GRAY = "#2563eb", "#d97706", "#059669", "#7c3aed", "#e11d48", "#94a3b8"
PALETTE = [BLUE, ORANGE, GREEN, PURPLE, ROSE, "#0891b2", "#ca8a04"]

rng = np.random.default_rng(7)


def new(w=4.8, h=3.5):
    fig, ax = plt.subplots(figsize=(w, h), dpi=110)
    fig.patch.set_facecolor("white")
    return fig, ax


def save(fig, name):
    p = os.path.join(OUT, name + ".png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def style(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=12, pad=8)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.22)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# 1 折线图
def chart_line():
    fig, ax = new()
    x = np.linspace(0, 10, 60)
    ax.plot(x, np.sin(x), color=BLUE, lw=2.2, label="方案 A")
    ax.plot(x, np.sin(x + 1.2) * 0.7, color=ORANGE, lw=2.2, label="方案 B")
    ax.legend(fontsize=8, frameon=False)
    style(ax, "折线图 · 趋势", "时间", "数值")
    return save(fig, "line")


# 2 堆叠面积图
def chart_area():
    fig, ax = new()
    x = np.arange(1, 13)
    a = np.array([3, 4, 3.6, 5, 6, 5.4, 6.2, 7, 6.6, 5.8, 5.2, 6])
    b = np.array([2, 2.4, 2.8, 2.6, 3.2, 3.6, 3.4, 3.8, 4, 4.4, 4.2, 4.6])
    c = np.array([1, 1.2, 1.4, 1.8, 1.6, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.2])
    ax.stackplot(x, a, b, c, colors=[BLUE, ORANGE, GREEN], alpha=0.8,
                 labels=["构成一", "构成二", "构成三"])
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    style(ax, "堆叠面积图 · 构成随时间", "月份", "量")
    return save(fig, "area")


# 3 分组柱状图
def chart_bar():
    fig, ax = new()
    cats = ["物理", "化学", "生物", "数学"]
    x = np.arange(len(cats)); w = 0.36
    v1 = np.array([68, 55, 72, 80]); v2 = np.array([74, 61, 66, 88])
    ax.bar(x - w/2, v1, w, color=BLUE, label="前测")
    ax.bar(x + w/2, v2, w, color=ORANGE, label="后测")
    ax.set_xticks(x); ax.set_xticklabels(cats)
    ax.legend(fontsize=8, frameon=False)
    style(ax, "分组柱状图 · 对比", "", "得分")
    return save(fig, "bar")


# 4 条形图 + 数值标签（棒棒糖变体）
def chart_hbar():
    fig, ax = new()
    names = ["模型 A", "模型 B", "模型 C", "模型 D", "模型 E"]
    vals = [0.92, 0.87, 0.81, 0.76, 0.64]
    y = np.arange(len(names))
    ax.hlines(y, 0, vals, color=GRAY, lw=2)
    ax.plot(vals, y, "o", color=BLUE, ms=9)
    for yi, v in zip(y, vals):
        ax.text(v + 0.015, yi, f"{v:.2f}", va="center", fontsize=8.5, color="#334155")
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_xlim(0, 1.05)
    style(ax, "条形图 · 排序对比（棒棒糖）", "指标值", "")
    return save(fig, "hbar")


# 5 散点图 + 拟合
def chart_scatter():
    fig, ax = new()
    x = rng.normal(50, 12, 90)
    y = 0.6 * x + rng.normal(0, 6, 90) + 12
    ax.scatter(x, y, s=28, color=BLUE, alpha=0.75, edgecolor="white", linewidth=0.6)
    k, b = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, k * xs + b, color=ROSE, lw=2, ls="--")
    r = np.corrcoef(x, y)[0, 1]
    ax.text(0.04, 0.93, f"r = {r:.2f}", transform=ax.transAxes, fontsize=9, color="#334155")
    style(ax, "散点图 · 相关", "自变量", "因变量")
    return save(fig, "scatter")


# 6 气泡图
def chart_bubble():
    fig, ax = new()
    x = rng.uniform(10, 90, 30); y = rng.uniform(10, 90, 30)
    s = rng.uniform(60, 900, 30); c = rng.uniform(0, 1, 30)
    sc = ax.scatter(x, y, s=s, c=c, cmap="viridis", alpha=0.72, edgecolor="white", linewidth=0.6)
    fig.colorbar(sc, ax=ax, shrink=0.8, label="第三维")
    style(ax, "气泡图 · 三维编码", "维度一", "维度二")
    return save(fig, "bubble")


# 7 直方图 + 核密度
def chart_hist():
    from scipy.stats import gaussian_kde
    fig, ax = new()
    d = np.concatenate([rng.normal(60, 9, 260), rng.normal(88, 6, 90)])
    ax.hist(d, bins=26, color=BLUE, alpha=0.65, edgecolor="white", density=True)
    xs = np.linspace(d.min(), d.max(), 200)
    ax.plot(xs, gaussian_kde(d)(xs), color=ROSE, lw=2.2)
    style(ax, "直方图 + 核密度 · 分布形态", "取值", "密度")
    return save(fig, "hist")


# 8 箱线图
def chart_box():
    fig, ax = new()
    data = [rng.normal(60, 8, 80), rng.normal(70, 14, 80), rng.normal(65, 5, 80)]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                    medianprops=dict(color="#0f172a", lw=1.6))
    for patch, c in zip(bp["boxes"], [BLUE, ORANGE, GREEN]):
        patch.set_facecolor(c); patch.set_alpha(0.55); patch.set_edgecolor(c)
    ax.set_xticklabels(["A 组", "B 组", "C 组"])
    style(ax, "箱线图 · 分布与离群", "", "取值")
    return save(fig, "box")


# 9 小提琴图
def chart_violin():
    fig, ax = new()
    data = [rng.normal(60, 8, 120), rng.normal(70, 14, 120), rng.normal(65, 5, 120)]
    parts = ax.violinplot(data, showmedians=True)
    for body, c in zip(parts["bodies"], [BLUE, ORANGE, GREEN]):
        body.set_facecolor(c); body.set_alpha(0.55)
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["A 组", "B 组", "C 组"])
    style(ax, "小提琴图 · 分布形状", "", "取值")
    return save(fig, "violin")


# 10 条带图（散点 + 抖动）
def chart_strip():
    fig, ax = new()
    groups = [rng.normal(60, 8, 40), rng.normal(70, 12, 40), rng.normal(65, 5, 40)]
    for i, (g, c) in enumerate(zip(groups, [BLUE, ORANGE, GREEN]), start=1):
        x = rng.normal(i, 0.055, len(g))
        ax.scatter(x, g, s=22, color=c, alpha=0.7, edgecolor="white", linewidth=0.5)
        ax.hlines(np.mean(g), i - 0.22, i + 0.22, color="#0f172a", lw=2)
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["A 组", "B 组", "C 组"])
    style(ax, "条带图 · 原始数据点", "", "取值")
    return save(fig, "strip")


# 11 山脊图
def chart_ridge():
    from scipy.stats import gaussian_kde
    fig, ax = new()
    xs = np.linspace(-4, 4, 220)
    for i, (mu, c) in enumerate(zip([-1.2, -0.4, 0.4, 1.2], PALETTE)):
        d = gaussian_kde(rng.normal(mu, 0.7, 400))(xs)
        ax.fill_between(xs, d * 0.9 + i * 0.55, i * 0.55, color=c, alpha=0.75)
        ax.plot(xs, d * 0.9 + i * 0.55, color="white", lw=1.1)
    ax.set_yticks([])
    ax.set_title("山脊图 · 多分布对比", fontsize=12, pad=8)
    ax.tick_params(labelsize=8); ax.grid(alpha=0.2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    return save(fig, "ridge")


# 12 热力图 / 相关性矩阵
def chart_heatmap():
    fig, ax = new(4.8, 3.9)
    labels = ["物理", "化学", "生物", "数学"]
    m = np.array([[1.0, 0.62, 0.45, 0.71],
                  [0.62, 1.0, 0.58, 0.49],
                  [0.45, 0.58, 1.0, 0.66],
                  [0.71, 0.49, 0.66, 1.0]])
    im = ax.imshow(m, cmap="RdYlBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4)); ax.set_xticklabels(labels)
    ax.set_yticks(range(4)); ax.set_yticklabels(labels)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=8.5,
                    color="#0f172a" if abs(m[i, j]) < 0.75 else "white")
    fig.colorbar(im, ax=ax, shrink=0.82, label="相关系数")
    ax.set_title("热力图 · 相关性矩阵", fontsize=12, pad=8)
    ax.tick_params(labelsize=8)
    return save(fig, "heatmap")


# 13 树状图 treemap
def chart_treemap():
    import squarify
    fig, ax = new()
    sizes = [38, 24, 16, 12, 6, 4]
    labels = ["力学 38%", "电磁 24%", "热学 16%", "光学 12%", "近代 6%", "其他 4%"]
    squarify.plot(sizes=sizes, label=labels, ax=ax, color=PALETTE,
                  text_kwargs={"fontsize": 8.5, "color": "white"}, pad=True)
    ax.axis("off")
    ax.set_title("树状图 · 层级占比", fontsize=12, pad=8)
    return save(fig, "treemap")


# 14 旭日图 sunburst（嵌套扇环）
def chart_sunburst():
    fig, ax = new(4.6, 4.2)
    ax.set_aspect("equal"); ax.axis("off")
    inner = [(0.55, "理科", BLUE), (0.30, "工科", ORANGE), (0.15, "文科", GREEN)]
    start = 90.0
    for frac, name, c in inner:
        ang = frac * 360
        ax.add_patch(Wedge((0, 0), 0.62, start, start + ang, width=0.30, facecolor=c, edgecolor="white"))
        mid = math.radians(start + ang / 2)
        ax.text(0.47 * math.cos(mid), 0.47 * math.sin(mid), name, ha="center", va="center",
                fontsize=8.5, color="white")
        start += ang
    outer = [(0.30, "物理"), (0.25, "化学"), (0.20, "计算机"), (0.15, "机械"), (0.10, "文学")]
    start = 90.0
    cols = [BLUE, BLUE, ORANGE, ORANGE, GREEN]
    for (frac, name), c in zip(outer, cols):
        ang = frac * 360
        ax.add_patch(Wedge((0, 0), 0.98, start, start + ang, width=0.32,
                           facecolor=c, alpha=0.6, edgecolor="white"))
        mid = math.radians(start + ang / 2)
        ax.text(0.82 * math.cos(mid), 0.82 * math.sin(mid), name, ha="center", va="center",
                fontsize=7.5, color="#0f172a")
        start += ang
    ax.set_title("旭日图 · 两层结构", fontsize=12, pad=8)
    return save(fig, "sunburst")


# 15 漏斗图
def chart_funnel():
    fig, ax = new()
    stages = ["了解", "感兴趣", "试听", "报名", "完成"]
    vals = [1000, 620, 340, 180, 96]
    for i, (s, v) in enumerate(zip(stages, vals)):
        w = v / vals[0]
        ax.add_patch(Rectangle((0.5 - w / 2, -i - 0.62), w, 0.62,
                               facecolor=PALETTE[i], alpha=0.85, edgecolor="white"))
        ax.text(1.02, -i - 0.31, f"{v}", va="center", fontsize=8.5)
        ax.text(-0.02, -i - 0.31, s, va="center", ha="right", fontsize=8.5)
    ax.set_xlim(-0.55, 1.2); ax.set_ylim(-5.1, 0.35)
    ax.axis("off")
    ax.set_title("漏斗图 · 转化与流失", fontsize=12, pad=8)
    return save(fig, "funnel")


# 16 瀑布图
def chart_waterfall():
    fig, ax = new(5.0, 3.6)
    items = ["收入", "成本", "税", "净利"]
    deltas = [120, -58, -18, None]
    cum = 0; bottoms = []; heights = []; cols = []
    for d in deltas[:-1]:
        bottoms.append(cum if d >= 0 else cum + d)
        heights.append(abs(d))
        cols.append(GREEN if d >= 0 else ROSE)
        cum += d
    bottoms.append(0); heights.append(cum); cols.append(BLUE)
    xs = np.arange(len(items))
    ax.bar(xs, heights, bottom=bottoms, color=cols, width=0.6)
    for i in range(len(items) - 1):
        level = (bottoms[i] + heights[i] if deltas[i] > 0 else bottoms[i])
        ax.plot([i + 0.3, i + 0.7], [level, level], color=GRAY, lw=1)
    ax.set_xticks(xs); ax.set_xticklabels(items)
    style(ax, "瀑布图 · 逐步增减", "", "金额")
    return save(fig, "waterfall")


# 17 甘特图
def chart_gantt():
    fig, ax = new(5.2, 3.2)
    tasks = ["读教材", "看动画", "做题", "讲给别人", "复盘"]
    spans = [(0, 3), (2, 4), (4, 3), (7, 2), (9, 2)]
    for i, ((start, dur), c) in enumerate(zip(spans, PALETTE)):
        ax.broken_barh([(start, dur)], (i - 0.3, 0.6), facecolors=c, alpha=0.85)
    ax.set_yticks(range(len(tasks))); ax.set_yticklabels(tasks)
    ax.set_xlabel("天"); ax.invert_yaxis()
    style(ax, "甘特图 · 学习计划", "", "")
    return save(fig, "gantt")


# 18 雷达图
def chart_radar():
    fig = plt.figure(figsize=(4.4, 3.9), dpi=110)
    ax = fig.add_subplot(111, polar=True)
    labels = ["理解", "记忆", "迁移", "速度", "兴趣"]
    n = len(labels)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist(); ang += ang[:1]
    for vals, c, name in [([4, 3, 2, 4, 5], BLUE, "学前一"), ([5, 5, 4, 4, 5], ORANGE, "学后二")]:
        v = vals + vals[:1]
        ax.plot(ang, v, color=c, lw=2, label=name)
        ax.fill(ang, v, color=c, alpha=0.18)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylim(0, 5); ax.tick_params(labelsize=7.5)
    ax.legend(fontsize=8, frameon=False, loc="upper right", bbox_to_anchor=(1.18, 1.12))
    ax.set_title("雷达图 · 多维画像", fontsize=12, pad=16)
    return save(fig, "radar")


# 19 平行坐标
def chart_parallel():
    fig, ax = new(5.2, 3.4)
    dims = ["成本", "速度", "精度", "稳定性", "可解释"]
    data = np.array([[3, 8, 6, 7, 5], [7, 4, 9, 6, 3], [5, 6, 7, 9, 8]])
    for i, row in enumerate(data):
        ax.plot(range(len(dims)), row, "o-", color=PALETTE[i], lw=2, ms=6, alpha=0.85)
    ax.set_xticks(range(len(dims))); ax.set_xticklabels(dims, fontsize=8.5)
    ax.set_ylim(0, 10)
    style(ax, "平行坐标 · 多维比较", "", "得分")
    return save(fig, "parallel")


# 20 斜率图
def chart_slope():
    fig, ax = new(4.2, 3.4)
    before = [62, 71, 55, 80]
    after = [78, 74, 69, 83]
    names = ["甲", "乙", "丙", "丁"]
    for i, (b, a_, n_) in enumerate(zip(before, after, names)):
        c = GREEN if a_ >= b else ROSE
        ax.plot([0, 1], [b, a_], "o-", color=c, lw=2, ms=7, alpha=0.85)
        ax.text(-0.06, b, n_, ha="right", va="center", fontsize=9)
        ax.text(1.06, a_, f"{a_}", ha="left", va="center", fontsize=8.5, color="#334155")
    ax.set_xlim(-0.3, 1.3); ax.set_xticks([0, 1]); ax.set_xticklabels(["前测", "后测"])
    style(ax, "斜率图 · 前后变化", "", "得分")
    return save(fig, "slope")


# 21 象限图
def chart_quadrant():
    fig, ax = new(4.6, 3.8)
    x = rng.uniform(-1, 1, 26); y = rng.uniform(-1, 1, 26)
    ax.axhline(0, color="#cbd5e1", lw=1.2); ax.axvline(0, color="#cbd5e1", lw=1.2)
    ax.scatter(x, y, s=rng.uniform(30, 140, 26), color=BLUE, alpha=0.65, edgecolor="white")
    for tx, ty, label in [(0.62, 0.86, "重点投入"), (-0.72, 0.86, "谨慎评估"),
                          (-0.72, -0.9, "低优先"), (0.66, -0.9, "快速试验")]:
        ax.text(tx, ty, label, fontsize=8.5, color="#475569", ha="center")
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1)
    style(ax, "象限图 · 二维决策", "收益", "成本")
    return save(fig, "quadrant")


# 22 误差棒图
def chart_errorbar():
    fig, ax = new()
    x = np.arange(4)
    means = np.array([62, 70, 66, 78])
    err = np.array([5, 8, 4, 6])
    ax.errorbar(x, means, yerr=err, fmt="o", color=BLUE, ecolor=ORANGE,
                elinewidth=2, capsize=5, ms=8)
    ax.axhline(70, color=GRAY, ls="--", lw=1.2)
    ax.set_xticks(x); ax.set_xticklabels(["A", "B", "C", "D"])
    style(ax, "误差棒图 · 均值与不确定性", "", "取值")
    return save(fig, "errorbar")


# 23 等高线 / 相图
def chart_contour():
    fig, ax = new(4.8, 3.6)
    gx, gy = np.meshgrid(np.linspace(-3, 3, 160), np.linspace(-3, 3, 160))
    z = np.exp(-(gx**2 + gy**2) / 2) + 0.7 * np.exp(-((gx - 1.4)**2 + (gy + 1.1)**2) / 1.2)
    cf = ax.contourf(gx, gy, z, levels=14, cmap="viridis", alpha=0.9)
    ax.contour(gx, gy, z, levels=7, colors="white", linewidths=0.7, alpha=0.75)
    fig.colorbar(cf, ax=ax, shrink=0.82, label="势能")
    ax.set_title("等高线 / 相图 · 场与势", fontsize=12, pad=8)
    ax.tick_params(labelsize=8)
    return save(fig, "contour")


# 24 网络图
def chart_network():
    import networkx as nx
    fig, ax = new(4.6, 3.9)
    G = nx.Graph()
    edges = [("概念", "前置"), ("概念", "延伸"), ("概念", "反例"), ("前置", "基础"),
             ("延伸", "应用"), ("反例", "边界")]
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=5)
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#cbd5e1", width=1.6)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1500, node_color=BLUE, alpha=0.85)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="white")
    ax.axis("off")
    ax.set_title("网络图 · 概念关系", fontsize=12, pad=8)
    return save(fig, "network")


# 25 桑基图（手绘双列节点 + 贝塞尔流带；matplotlib 原生 Sankey 布局发散，不适合教学）
def chart_sankey():
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch

    fig, ax = new(5.2, 3.8)
    ax.set_xlim(0, 10); ax.set_ylim(-0.6, 12.2); ax.axis("off")

    def ribbon(x0, y0a, y0b, x1, y1a, y1b, color, alpha=0.42):
        xm = (x0 + x1) / 2
        verts = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a),
                 (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
        codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
                 MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MPath(verts, codes), facecolor=color, alpha=alpha, lw=0))

    def node(x, y0, h, label, color, side="left"):
        ax.add_patch(Rectangle((x - 0.16, y0), 0.32, h, facecolor=color, edgecolor="white"))
        tx = x - 0.32 if side == "left" else x + 0.32
        ax.text(tx, y0 + h / 2, label, ha="right" if side == "left" else "left",
                va="center", fontsize=9.5, color="#0f172a")

    # 左：学习投入 20、练习 10；右：理解 13、遗忘 7、迁移 10（单位缩放）
    L = [("学习投入", 20, 8.2), ("练习", 10, 2.2)]
    R = [("理解", 13, 8.6), ("遗忘", 7, 5.4), ("迁移", 10, 2.5)]
    for name, v, y in L:
        node(2.2, y, v * 0.16, name, BLUE, "left")
    for name, v, y in R:
        node(7.8, y, v * 0.16, name, GREEN, "right")

    # 学习投入 → 理解(13) / 遗忘(7)；练习 → 迁移(10)
    ribbon(2.36, 8.2 + 7 * 0.16, 8.2 + 8.2 * 0.16, 7.64, 8.6, 8.6 + 8.2 * 0.16, BLUE)
    ribbon(2.36, 8.2, 8.2 + 7 * 0.16, 7.64, 5.4, 5.4 + 5.4 * 0.16, GRAY)
    ribbon(2.36, 2.2, 2.2 + 10 * 0.16, 7.64, 2.5, 2.5 + 10 * 0.16, ORANGE)

    ax.text(0.55, 11.9, "桑基图 · 流向与分流", fontsize=12)
    ax.text(0.55, 11.45, "带宽 ∝ 数量；一眼看出「投入去哪了」", fontsize=8.5, color="#64748b")
    return save(fig, "sankey")


# ============ 第二批（v1.7.0）============


# 26 阶梯图
def chart_step():
    fig, ax = new()
    x = np.arange(1, 11)
    y = np.array([3, 3, 5, 5, 5, 8, 8, 6, 6, 9])
    ax.step(x, y, where="post", color=BLUE, lw=2.2, marker="o", ms=5)
    ax.fill_between(x, y, step="post", color=BLUE, alpha=0.12)
    style(ax, "阶梯图 · 分段恒定", "阶段", "取值")
    return save(fig, "step")


# 27 折线 + 置信带
def chart_ci():
    fig, ax = new()
    x = np.arange(20)
    m = 50 + 6 * np.sin(x / 3) + x * 0.4
    se = 3 + np.linspace(0, 2.2, 20)
    ax.plot(x, m, color=BLUE, lw=2.2, label="均值")
    ax.fill_between(x, m - 1.96 * se, m + 1.96 * se, color=BLUE, alpha=0.18, label="95% 置信带")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    style(ax, "折线 + 置信带 · 不确定性", "期数", "取值")
    return save(fig, "ci")


# 28 迷你图矩阵（小倍数）
def chart_sparkline():
    fig, axes = plt.subplots(3, 4, figsize=(5.2, 3.4), dpi=110)
    fig.patch.set_facecolor("white")
    for i, ax in enumerate(axes.ravel()):
        y = np.cumsum(rng.normal(0, 1, 24))
        ax.plot(y, color=PALETTE[i % len(PALETTE)], lw=1.6)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(f"指标 {i + 1}", fontsize=7.5, pad=2)
    fig.suptitle("迷你图矩阵 · 小倍数看趋势", fontsize=12, y=1.02)
    fig.tight_layout()
    return save(fig, "sparkline")


# 29 帕累托图（唯一允许双轴的场景：柱=频次，线=累计占比）
def chart_pareto():
    fig, ax = new()
    cats = ["概念不清", "缺练习", "时间不足", "无反馈", "环境差"]
    v = np.array([38, 27, 18, 11, 6])
    order = np.argsort(-v)
    v = v[order]; cats = [cats[i] for i in order]
    cum = np.cumsum(v) / v.sum() * 100
    ax.bar(cats, v, color=BLUE, alpha=0.85)
    ax.set_ylabel("出现次数", fontsize=9)
    ax2 = ax.twinx()
    ax2.plot(cats, cum, "o-", color=ROSE, lw=2)
    ax2.set_ylim(0, 108); ax2.set_ylabel("累计占比 (%)", fontsize=9, color=ROSE)
    ax2.axhline(80, color=GRAY, ls="--", lw=1)
    ax.set_title("帕累托图 · 抓主要矛盾", fontsize=12, pad=8)
    ax.tick_params(labelsize=8); ax2.tick_params(labelsize=8)
    return save(fig, "pareto")


# 30 子弹图
def chart_bullet():
    fig, ax = new()
    rows = ["营收", "留存", "满意度"]
    ranges = [(0, 60), (0, 55), (0, 70)]
    targets = [78, 72, 85]
    actuals = [71, 64, 88]
    for i, (rng_, t, a) in enumerate(zip(ranges, targets, actuals)):
        lo, hi = rng_
        ax.barh(i, hi, left=0, height=0.5, color="#e2e8f0")
        ax.barh(i, hi * 0.75, left=0, height=0.5, color="#cbd5e1")
        ax.barh(i, hi * 0.45, left=0, height=0.5, color="#94a3b8")
        ax.plot([a, a], [i - 0.28, i + 0.28], color=BLUE, lw=6)
        ax.plot([t, t], [i - 0.30, i + 0.30], color="#0f172a", lw=2.2, ls=(0, (2, 1.5)))
        ax.text(108, i, f"{a} / 目标 {t}", va="center", fontsize=8.5, color="#334155")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows)
    ax.set_xlim(0, 132)
    style(ax, "子弹图 · 实际 vs 目标", "指标值", "")
    return save(fig, "bullet")


# 31 环形仪表
def chart_gauge():
    fig, ax = new(4.4, 3.0)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Wedge((0, 0), 1.0, 0, 180, width=0.22, facecolor="#e2e8f0", edgecolor="none"))
    val = 0.72
    ax.add_patch(Wedge((0, 0), 1.0, 180 - 180 * val, 180, width=0.22, facecolor=BLUE, edgecolor="none"))
    ang = math.radians(180 - 180 * val)
    ax.plot([0, 0.78 * math.cos(ang)], [0, 0.78 * math.sin(ang)], color="#0f172a", lw=3)
    ax.add_patch(Circle((0, 0), 0.09, color="#0f172a"))
    ax.text(0, -0.28, f"{val * 100:.0f}%", ha="center", fontsize=20, color=INK if False else "#0f172a")
    ax.text(0, -0.52, "目标完成度", ha="center", fontsize=9, color="#64748b")
    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-0.68, 1.15)
    ax.set_title("环形仪表 · 单值进度", fontsize=12, pad=4)
    return save(fig, "gauge")


# 32 华夫图
def chart_waffle():
    fig, ax = new(4.2, 3.6)
    ax.set_aspect("equal"); ax.axis("off")
    total, parts = 100, [42, 27, 18, 13]
    cols = [BLUE, ORANGE, GREEN, ROSE]
    filled = 0
    for i in range(total):
        r, c = divmod(i, 10)
        ax.add_patch(Rectangle((c, 9 - r), 0.86, 0.86, facecolor="#eef2f7", edgecolor="white"))
    for p, color in zip(parts, cols):
        for _ in range(p):
            r, c = divmod(filled, 10)
            ax.add_patch(Rectangle((c, 9 - r), 0.86, 0.86, facecolor=color, edgecolor="white", alpha=0.9))
            filled += 1
    ax.set_xlim(-0.3, 10); ax.set_ylim(-0.3, 10)
    ax.set_title("华夫图 · 每格 1% 的构成", fontsize=12, pad=6)
    return save(fig, "waffle")


# 33 玫瑰图
def chart_rose():
    fig = plt.figure(figsize=(4.4, 3.7), dpi=110)
    ax = fig.add_subplot(111, polar=True)
    n = 12
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    v = np.array([8, 6, 9, 12, 15, 18, 21, 19, 14, 11, 9, 7])
    ax.bar(ang, v, width=2 * np.pi / n * 0.9, color=BLUE, alpha=0.8, edgecolor="white")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    ax.set_xticks(ang); ax.set_xticklabels([f"{i+1}月" for i in range(n)], fontsize=7.5)
    ax.set_yticklabels([])
    ax.set_title("玫瑰图 · 周期分布", fontsize=12, pad=14)
    return save(fig, "rose")


# 34 云雨图（半小提琴 + 箱线 + 散点）
def chart_raincloud():
    from scipy.stats import gaussian_kde
    fig, ax = new(4.8, 3.6)
    groups = [rng.normal(60, 9, 70), rng.normal(70, 13, 70)]
    for i, (g, c) in enumerate(zip(groups, [BLUE, ORANGE]), start=1):
        d = gaussian_kde(g)
        ys = np.linspace(g.min(), g.max(), 120)
        xs = d(ys)
        xs = xs / xs.max() * 0.34
        ax.fill_betweenx(ys, i - xs, i, color=c, alpha=0.55, lw=0)
        ax.boxplot([g], positions=[i + 0.18], widths=0.12, patch_artist=True,
                   boxprops=dict(facecolor=c, alpha=0.6), medianprops=dict(color="#0f172a"))
        jx = rng.normal(i + 0.42, 0.035, len(g))
        ax.scatter(jx, g, s=12, color=c, alpha=0.55, edgecolor="none")
    ax.set_xticks([1, 2]); ax.set_xticklabels(["A 组", "B 组"])
    ax.set_xlim(0.4, 2.9)
    style(ax, "云雨图 · 分布全貌", "", "取值")
    return save(fig, "raincloud")


# 35 联合分布（散点 + 边际直方）
def chart_joint():
    fig = plt.figure(figsize=(4.8, 4.0), dpi=110)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(4, 4, hspace=0.08, wspace=0.08)
    ax = fig.add_subplot(gs[1:4, 0:3])
    axh = fig.add_subplot(gs[0, 0:3], sharex=ax)
    axv = fig.add_subplot(gs[1:4, 3], sharey=ax)
    x = rng.normal(50, 12, 160); y = 0.55 * x + rng.normal(0, 7, 160) + 8
    ax.scatter(x, y, s=16, color=BLUE, alpha=0.6, edgecolor="none")
    axh.hist(x, bins=18, color=BLUE, alpha=0.55)
    axv.hist(y, bins=18, orientation="horizontal", color=BLUE, alpha=0.55)
    axh.axis("off"); axv.axis("off")
    ax.tick_params(labelsize=7.5); ax.grid(alpha=0.2)
    ax.set_xlabel("X", fontsize=8); ax.set_ylabel("Y", fontsize=8)
    ax.set_title("联合分布 · 散点 + 边际", fontsize=12, pad=18)
    return save(fig, "joint")


# 36 六边形分箱
def chart_hexbin():
    fig, ax = new()
    x = rng.normal(0, 1, 4000); y = x * 0.6 + rng.normal(0, 1, 4000)
    hb = ax.hexbin(x, y, gridsize=22, cmap="viridis", mincnt=1)
    fig.colorbar(hb, ax=ax, shrink=0.82, label="计数")
    ax.set_title("六边形分箱 · 大样本密度", fontsize=12, pad=8)
    ax.tick_params(labelsize=8)
    return save(fig, "hexbin")


# 37 QQ 图
def chart_qq():
    from scipy import stats
    fig, ax = new()
    d = np.concatenate([rng.normal(0, 1, 180), rng.normal(3, 0.8, 40)])
    stats.probplot(d, dist="norm", plot=ax)
    ax.get_lines()[0].set(color=BLUE, ms=4, alpha=0.7)
    ax.get_lines()[1].set(color=ROSE, lw=2)
    ax.set_title("QQ 图 · 与正态的偏离", fontsize=12, pad=8)
    ax.set_xlabel("理论分位数", fontsize=8.5); ax.set_ylabel("样本分位数", fontsize=8.5)
    ax.tick_params(labelsize=8); ax.grid(alpha=0.22)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return save(fig, "qq")


# 38 森林图
def chart_forest():
    fig, ax = new(4.8, 3.7)
    labels = ["研究 A", "研究 B", "研究 C", "研究 D", "合并"]
    est = np.array([0.72, 0.85, 0.64, 0.91, 0.78])
    lo = np.array([0.55, 0.66, 0.44, 0.72, 0.70])
    hi = np.array([0.94, 1.09, 0.93, 1.15, 0.87])
    y = np.arange(len(labels))[::-1]
    ax.axvline(1.0, color=GRAY, ls="--", lw=1.2)
    for i, (e, l, h) in enumerate(zip(est, lo, hi)):
        c = BLUE if i < len(labels) - 1 else ROSE
        ax.plot([l, h], [y[i], y[i]], color=c, lw=2)
        ax.plot([e], [y[i]], "s", color=c, ms=8)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_xlim(0.35, 1.25)
    style(ax, "森林图 · 效应量与区间", "风险比 (1 = 无差异)", "")
    return save(fig, "forest")


# 39 韦恩图
def chart_venn():
    fig, ax = new(4.2, 3.7)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Circle((-0.42, 0), 0.95, color=BLUE, alpha=0.35))
    ax.add_patch(Circle((0.42, 0), 0.95, color=ORANGE, alpha=0.35))
    ax.text(-0.86, 0.72, "A 集合", fontsize=10, color="#1e3a8a")
    ax.text(0.52, 0.72, "B 集合", fontsize=10, color="#9a3412")
    ax.text(-0.62, 0.02, "128", fontsize=12, color="#0f172a")
    ax.text(0.62, 0.02, "96", fontsize=12, color="#0f172a")
    ax.text(0, 0.02, "54", fontsize=13, color="#0f172a")
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.2, 1.2)
    ax.set_title("韦恩图 · 集合重叠", fontsize=12, pad=6)
    return save(fig, "venn")


# 40 弧线图
def chart_arc():
    from matplotlib.patches import FancyArrowPatch
    fig, ax = new(5.0, 3.0)
    nodes = ["基础", "概念", "方法", "应用", "边界"]
    xs = np.arange(len(nodes))
    ax.plot([xs.min() - 0.3, xs.max() + 0.3], [0, 0], color="#cbd5e1", lw=1.5, zorder=1)
    for i, n in enumerate(nodes):
        ax.plot([i], [0], "o", color=BLUE, ms=14, zorder=3)
        ax.text(i, -0.34, n, ha="center", fontsize=8.5)
    pairs = [(0, 1), (0, 2), (1, 3), (2, 4), (0, 4)]
    for i, j in pairs:
        ax.add_patch(FancyArrowPatch((i, 0.08), (j, 0.08), connectionstyle="arc3,rad=-0.45",
                                     arrowstyle="-", color=ORANGE, lw=1.6, alpha=0.75, zorder=2))
    ax.set_ylim(-0.7, 1.1); ax.set_xlim(-0.6, len(nodes) - 0.4)
    ax.axis("off")
    ax.set_title("弧线图 · 一维排布上的关系", fontsize=12, pad=6)
    return save(fig, "arc")


# 41 日历热力
def chart_calendar():
    fig, ax = new(5.0, 3.0)
    weeks = 20
    data = np.abs(rng.normal(3, 2, (7, weeks)))
    im = ax.imshow(data, cmap="YlGnBu", aspect="auto")
    ax.set_yticks(range(7)); ax.set_yticklabels(["一", "二", "三", "四", "五", "六", "日"], fontsize=7.5)
    ax.set_xticks(range(0, weeks, 4)); ax.set_xticklabels([f"W{i+1}" for i in range(0, weeks, 4)], fontsize=7.5)
    fig.colorbar(im, ax=ax, shrink=0.8, label="强度")
    ax.set_title("日历热力 · 按周 × 星期看强度", fontsize=12, pad=8)
    return save(fig, "calendar")


# 42 矢量场
def chart_quiver():
    fig, ax = new()
    x, y = np.meshgrid(np.linspace(-2, 2, 15), np.linspace(-2, 2, 15))
    u, v = -y, x
    ax.quiver(x, y, u, v, np.hypot(u, v), cmap="viridis", pivot="mid")
    ax.set_aspect("equal")
    ax.set_title("矢量场 · 方向与强度", fontsize=12, pad=8)
    ax.tick_params(labelsize=8)
    return save(fig, "quiver")


# ============ 第三批（v1.8.0）============


# 43 百分比堆叠条形
def chart_pct_stacked():
    fig, ax = new(5.0, 3.2)
    cats = ["理科", "工科", "文科", "艺术"]
    a = np.array([38, 30, 46, 22]); b = np.array([34, 42, 32, 38]); c = np.array([28, 28, 22, 40])
    tot = a + b + c
    left = np.zeros(len(cats))
    for seg, color, name in [(a, BLUE, "课堂"), (b, ORANGE, "自学"), (c, GREEN, "实践")]:
        ax.barh(cats, seg / tot * 100, left=left, color=color, label=name, height=0.55)
        left += seg / tot * 100
    ax.set_xlim(0, 100); ax.set_xlabel("占比 (%)", fontsize=9)
    ax.legend(fontsize=8, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.42))
    style(ax, "百分比堆叠条形 · 构成对比", "", "")
    return save(fig, "pct_stacked")


# 44 发散条形（正负）
def chart_diverging():
    fig, ax = new(4.8, 3.4)
    items = ["方案 A", "方案 B", "方案 C", "方案 D"]
    v = np.array([18, -12, 27, -8])
    colors = [GREEN if x >= 0 else ROSE for x in v]
    ax.barh(items, v, color=colors, height=0.55)
    ax.axvline(0, color="#0f172a", lw=1.2)
    for i, x in enumerate(v):
        ax.text(x + (1.2 if x >= 0 else -1.2), i, f"{x:+d}", va="center",
                ha="left" if x >= 0 else "right", fontsize=8.5)
    style(ax, "发散条形 · 正负贡献", "增减", "")
    return save(fig, "diverging")


# 45 哑铃图
def chart_dumbbell():
    fig, ax = new(4.8, 3.4)
    items = ["指标 A", "指标 B", "指标 C", "指标 D"]
    before = np.array([52, 61, 47, 70])
    after = np.array([68, 66, 72, 74])
    y = np.arange(len(items))
    for i in range(len(items)):
        ax.plot([before[i], after[i]], [y[i], y[i]], color="#cbd5e1", lw=3, zorder=1)
    ax.scatter(before, y, s=90, color=GRAY, zorder=2, label="前测")
    ax.scatter(after, y, s=90, color=BLUE, zorder=3, label="后测")
    ax.set_yticks(y); ax.set_yticklabels(items)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    style(ax, "哑铃图 · 两点之间的变化", "得分", "")
    return save(fig, "dumbbell")


# 46 累积分布 CDF
def chart_cdf():
    fig, ax = new()
    d1 = rng.normal(60, 9, 300); d2 = rng.normal(70, 13, 300)
    for d, c, name in [(d1, BLUE, "A 组"), (d2, ORANGE, "B 组")]:
        xs = np.sort(d)
        ys = np.arange(1, len(xs) + 1) / len(xs)
        ax.step(xs, ys, where="post", color=c, lw=2, label=name)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.set_ylim(0, 1.02)
    style(ax, "累积分布 CDF · 比中位数更全", "取值", "累积比例")
    return save(fig, "cdf")


# 47 生存曲线（Kaplan-Meier 风格）
def chart_survival():
    fig, ax = new()
    t = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16])
    s = np.array([1.0, 0.94, 0.88, 0.80, 0.73, 0.66, 0.58, 0.52, 0.45])
    ax.step(t, s, where="post", color=BLUE, lw=2.2, label="方案 A")
    s2 = np.array([1.0, 0.90, 0.79, 0.68, 0.60, 0.50, 0.42, 0.35, 0.30])
    ax.step(t, s2, where="post", color=ORANGE, lw=2.2, label="方案 B")
    ax.plot(t[2::2], s[2::2], "|", color=BLUE, ms=10, mew=1.8)
    ax.axhline(0.5, color=GRAY, ls="--", lw=1)
    ax.legend(fontsize=8, frameon=False)
    ax.set_ylim(0, 1.05)
    style(ax, "生存曲线 · 保持率随时间", "时间", "未发生比例")
    return save(fig, "survival")


# 48 控制图
def chart_control():
    fig, ax = new(5.0, 3.4)
    x = np.arange(24)
    y = 50 + rng.normal(0, 2.2, 24)
    y[17] = 59.5
    mu, sd = y.mean(), y.std(ddof=1)
    ax.plot(x, y, "o-", color=BLUE, lw=1.6, ms=5)
    ax.axhline(mu, color="#0f172a", lw=1.2)
    for k, c in [(3, ROSE), (2, ORANGE)]:
        ax.axhline(mu + k * sd, color=c, ls="--", lw=1)
        ax.axhline(mu - k * sd, color=c, ls="--", lw=1)
    ax.scatter([17], [y[17]], s=120, facecolor="none", edgecolor=ROSE, lw=2)
    ax.text(0.5, mu + 3 * sd + 1.2, "UCL (μ+3σ)", fontsize=7.5, color=ROSE)
    style(ax, "控制图 · 过程是否失控", "批次", "指标")
    return save(fig, "control")


# 49 时间线
def chart_timeline():
    fig, ax = new(5.4, 2.9)
    events = [("提出假设", 1), ("实验验证", 3.2), ("发表论文", 5.1), ("复现失败", 7.0), ("修正模型", 8.6)]
    ax.plot([0.4, 9.6], [0, 0], color="#cbd5e1", lw=3, solid_capstyle="round")
    for i, (name, x) in enumerate(events):
        up = i % 2 == 0
        ax.plot([x], [0], "o", color=BLUE if up else ORANGE, ms=11, zorder=3)
        ax.plot([x, x], [0, 0.55 if up else -0.55], color="#94a3b8", lw=1.2)
        ax.text(x, 0.62 if up else -0.68, name, ha="center",
                va="bottom" if up else "top", fontsize=8.5)
    ax.set_ylim(-1.2, 1.2); ax.set_xlim(0, 10)
    ax.axis("off")
    ax.set_title("时间线 · 事件顺序", fontsize=12, pad=6)
    return save(fig, "timeline")


# 50 流程图
def chart_flow():
    from matplotlib.patches import FancyBboxPatch
    fig, ax = new(4.8, 3.6)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    steps = [("输入", 5.0, 8.6), ("预处理", 5.0, 6.4), ("模型", 5.0, 4.2), ("评估", 5.0, 2.0)]
    for name, x, y in steps:
        ax.add_patch(FancyBboxPatch((x - 1.7, y - 0.62), 3.4, 1.24,
                                    boxstyle="round,pad=0.02,rounding_size=0.18",
                                    facecolor="#eff6ff", edgecolor=BLUE, lw=1.8))
        ax.text(x, y, name, ha="center", va="center", fontsize=9.5)
    for i in range(len(steps) - 1):
        y0 = steps[i][2] - 0.66; y1 = steps[i + 1][2] + 0.66
        ax.annotate("", xy=(5.0, y1), xytext=(5.0, y0),
                    arrowprops=dict(arrowstyle="-|>", color="#64748b", lw=1.6))
    ax.annotate("", xy=(8.6, 4.2), xytext=(6.7, 4.2),
                arrowprops=dict(arrowstyle="-|>", color=ROSE, lw=1.6,
                                connectionstyle="arc3,rad=0"))
    ax.text(8.8, 4.2, "失败重训", fontsize=7.5, color=ROSE, va="center")
    ax.set_title("流程图 · 步骤与分支", fontsize=12, pad=6)
    return save(fig, "flow")


# 51 决策树
def chart_tree():
    from matplotlib.patches import FancyBboxPatch
    fig, ax = new(5.2, 3.6)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    nodes = [(5.0, 8.6, "特征 X > 0.5?"), (2.6, 5.4, "特征 Y > 1.2?"), (7.4, 5.4, "类别 = B"),
             (1.3, 2.0, "类别 = A"), (3.9, 2.0, "类别 = C")]
    edges = [(0, 1, "是"), (0, 2, "否"), (1, 3, "是"), (1, 4, "否")]
    for i, j, label in edges:
        x0, y0, _ = nodes[i]; x1, y1, _ = nodes[j]
        ax.annotate("", xy=(x1, y1 + 0.55), xytext=(x0, y0 - 0.55),
                    arrowprops=dict(arrowstyle="-", color="#94a3b8", lw=1.3))
        ax.text((x0 + x1) / 2 + 0.25, (y0 + y1) / 2, label, fontsize=7.5, color="#475569")
    for x, y, name in nodes:
        ax.add_patch(FancyBboxPatch((x - 1.25, y - 0.55), 2.5, 1.1,
                                    boxstyle="round,pad=0.02,rounding_size=0.14",
                                    facecolor="#f8fafc", edgecolor=PURPLE, lw=1.5))
        ax.text(x, y, name, ha="center", va="center", fontsize=7.8)
    ax.set_title("决策树 · 判断路径", fontsize=12, pad=6)
    return save(fig, "tree")


# 52 标签云（按权重排布的紧凑词块）
def chart_wordcloud():
    fig, ax = new(4.8, 3.4)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    words = [("假设", 100), ("推理链", 88), ("原子事实", 80), ("类比", 72), ("边界", 64),
             ("正交", 56), ("变换", 50), ("频率", 42), ("相位", 36), ("直觉", 30)]
    weights = [w for _, w in words]
    x, y, row_h, maxx = 0.4, 9.2, 0.0, 9.6
    for (w, wt) in words:
        fs = 8 + 14 * (wt - 30) / 70.0
        # 字符宽度近似：中文按 1.0 em，其它按 0.6 em
        est = sum(1.0 if ord(ch) > 127 else 0.6 for ch in w) * fs / 14.0
        if x + est > maxx:
            x = 0.4; y -= row_h + 0.25; row_h = 0.0
        ax.text(x, y, w, fontsize=fs, color=BLUE, va="top", ha="left", alpha=0.9)
        x += est + 0.35
        row_h = max(row_h, fs / 14.0)
    ax.text(0.4, 0.5, "字号 ∝ 词频（词的「云」；比真词云更易读）", fontsize=7.5, color="#64748b")
    ax.set_title("标签云 · 高频概念", fontsize=12, pad=6)
    return save(fig, "wordcloud")


CHARTS = [
    ("折线图", chart_line), ("堆叠面积图", chart_area), ("分组柱状图", chart_bar),
    ("条形图/棒棒糖", chart_hbar), ("散点图", chart_scatter), ("气泡图", chart_bubble),
    ("直方图+KDE", chart_hist), ("箱线图", chart_box), ("小提琴图", chart_violin),
    ("条带图", chart_strip), ("山脊图", chart_ridge), ("热力图/相关矩阵", chart_heatmap),
    ("树状图", chart_treemap), ("旭日图", chart_sunburst), ("漏斗图", chart_funnel),
    ("瀑布图", chart_waterfall), ("甘特图", chart_gantt), ("雷达图", chart_radar),
    ("平行坐标", chart_parallel), ("斜率图", chart_slope), ("象限图", chart_quadrant),
    ("误差棒图", chart_errorbar), ("等高线/相图", chart_contour), ("网络图", chart_network),
    ("桑基图", chart_sankey),
    # 第二批（v1.7.0）
    ("阶梯图", chart_step), ("折线+置信带", chart_ci), ("迷你图矩阵", chart_sparkline),
    ("帕累托图", chart_pareto), ("子弹图", chart_bullet), ("环形仪表", chart_gauge),
    ("华夫图", chart_waffle), ("玫瑰图", chart_rose), ("云雨图", chart_raincloud),
    ("联合分布", chart_joint), ("六边形分箱", chart_hexbin), ("QQ 图", chart_qq),
    ("森林图", chart_forest), ("韦恩图", chart_venn), ("弧线图", chart_arc),
    ("日历热力", chart_calendar), ("矢量场", chart_quiver),
    # 第三批（v1.8.0）
    ("百分比堆叠条形", chart_pct_stacked), ("发散条形", chart_diverging),
    ("哑铃图", chart_dumbbell), ("累积分布CDF", chart_cdf),
    ("生存曲线", chart_survival), ("控制图", chart_control),
    ("时间线", chart_timeline), ("流程图", chart_flow),
    ("决策树", chart_tree), ("标签云", chart_wordcloud),
]


# ---------------- 注册表：按需调用 -------------
# 「按需调用」的核心：只渲染你点名的那一张，不必跑全部 52 张。
# 分类用于 --list 检索；每个名字只能归一个主分类，避免歧义。
CATEGORY_GROUPS = {
    "比较": ["分组柱状图", "条形图/棒棒糖", "子弹图", "哑铃图", "斜率图", "雷达图",
             "象限图", "发散条形", "帕累托图"],
    "趋势": ["折线图", "堆叠面积图", "阶梯图", "折线+置信带", "迷你图矩阵",
             "累积分布CDF", "控制图"],
    "分布": ["直方图+KDE", "箱线图", "小提琴图", "条带图", "山脊图", "云雨图", "QQ 图"],
    "关系": ["散点图", "气泡图", "热力图/相关矩阵", "平行坐标", "联合分布", "六边形分箱"],
    "构成": ["树状图", "旭日图", "瀑布图", "华夫图", "百分比堆叠条形"],
    "流向": ["桑基图", "漏斗图", "弧线图"],
    "过程": ["甘特图", "时间线", "流程图", "决策树", "生存曲线"],
    "空间与场": ["等高线/相图", "矢量场", "日历热力", "玫瑰图"],
    "推断": ["误差棒图", "森林图"],
    "结构": ["网络图", "韦恩图"],
    "进度": ["环形仪表"],
    "文本": ["标签云"],
}


def _file_key(fn):
    """从函数源码里取 save(fig, "xxx") 的文件名，避免再维护一份映射表。"""
    import inspect
    try:
        src = inspect.getsource(fn)
    except OSError:
        return None
    found = re.findall(r'save\(fig, "([^"]+)"\)', src)
    return found[-1] if found else None


def build_registry():
    fn_by_name = dict(CHARTS)
    reg = {}
    for cat, names in CATEGORY_GROUPS.items():
        for n in names:
            fn = fn_by_name.get(n)
            if fn is None:
                continue
            reg[n] = {"fn": fn, "category": cat, "file": _file_key(fn)}
    return reg


REGISTRY = build_registry()


def render_one(name, out=None):
    """按名渲染一张图；out 给定时复制到该路径。返回实际文件路径。"""
    item = REGISTRY.get(name)
    if item is None:
        raise KeyError(name)
    path = item["fn"]()
    if out:
        import shutil
        out_dir = os.path.dirname(os.path.abspath(out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(path, out)
        return out
    return path


def contact_sheet(paths):
    try:
        from PIL import Image
    except Exception:
        print("SKIP contact sheet（缺 Pillow）")
        return None
    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail((420, 320))
        thumbs.append(im)
    cols = 6
    rows = math.ceil(len(thumbs) / cols)
    cw, ch = 440, 360
    sheet = Image.new("RGB", (cols * cw, rows * ch), "white")
    for i, im in enumerate(thumbs):
        x = (i % cols) * cw + (cw - im.width) // 2
        y = (i // cols) * ch + (ch - im.height) // 2
        sheet.paste(im, (x, y))
    out = os.path.join(OUT, "_gallery.png")
    sheet.save(out)
    return out


def main():
    paths = []
    failed = []
    for name, fn in CHARTS:
        try:
            p = fn()
            paths.append(p)
            print("OK  ", name, os.path.getsize(p))
        except Exception as e:
            failed.append((name, type(e).__name__, str(e)[:120]))
            print("FAIL", name, type(e).__name__, str(e)[:120])
    sheet = contact_sheet(paths) if paths else None
    if sheet:
        print("SHEET", os.path.getsize(sheet))
    print("SUMMARY", len(paths), "ok,", len(failed), "failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())