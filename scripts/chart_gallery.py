# -*- coding: utf-8 -*-
"""图表画廊：真实渲染 24 种常用图表，作为 references/chart-catalog.md 的可执行证据。

用法：python scripts/chart_gallery.py
输出：docs/images/charts/<类型>.png + docs/images/charts/_gallery.png（拼版）
"""
import os
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
]


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
    cols = 5
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