# -*- coding: utf-8 -*-
"""general-knowledge-tutor-skills 全量回归（audit-loop 清单兜底）
用法：python scripts/regression.py
覆盖：①references 全部 python 代码块真机执行（SKIP 名单显式豁免）
     ②quiz 模板 headless 判分断言  ③双文档命名/篇幅/元词汇 ④版本一致性
"""
import ast, json, os, re, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(BASE, "references")
PY_DEFAULT = r"C:/Users/iamly/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
PY_MANIM = r"C:/Users/iamly/.workbuddy/binaries/python/envs/deeptutor/Scripts/python.exe"
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_reg_work")
os.makedirs(WORK, exist_ok=True)

# 显式豁免名单：(文件, 块号, 原因)
SKIP = {
    ("extended-viz", 2): "graphviz 需 dot.exe 系统二进制（坑已记入模板，无则降级 pyvis/Mermaid）",
    ("3d-animation", 5): "bpy 依赖 Blender wheel(330MB)，环境未装",
}
results = []  # (项, 状态, 说明)


def run_blocks():
    for md in sorted(os.listdir(REF)):
        if not md.endswith(".md"):
            continue
        text = open(os.path.join(REF, md), encoding="utf-8").read()
        for i, m in enumerate(re.finditer(r"```python\n(.*?)```", text, re.S), 1):
            key = (md[:-3], i)
            code = m.group(1)
            label = f"{key[0]}#{i}"
            if key in SKIP:
                results.append((label, "SKIP", SKIP[key])); continue
            try:
                ast.parse(code)
            except SyntaxError as e:
                results.append((label, "FAIL", f"SyntaxError L{e.lineno}")); continue
            py = PY_MANIM if re.search(r"\b(from manim|import manim)\b", code) else PY_DEFAULT
            src = os.path.join(WORK, f"{key[0]}_b{i}.py")
            open(src, "w", encoding="utf-8").write(code)
            p = subprocess.run([py, src], capture_output=True, timeout=180, cwd=WORK,
                               text=True, encoding="utf-8", errors="replace")
            if p.returncode == 0:
                results.append((label, "PASS", (p.stdout.strip().splitlines() or [""])[-1][:80]))
            else:
                results.append((label, "FAIL", (p.stderr.strip().splitlines() or [""])[-1][:140]))


def run_quiz():
    quiz = os.path.join(REF, "templates", "quiz-template.html")
    if not os.path.isfile(quiz):
        results.append(("quiz-headless", "FAIL", "templates/quiz-template.html 不存在")); return
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=6000", "--dump-dom",
                        f"file:///{quiz.replace(chr(92), '/')}#selftest"],
                       capture_output=True, timeout=60, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"SELFTEST score=(\d)/5 pass=(true|false)", p.stdout)
    if m and m.group(1) == "5" and m.group(2) == "true":
        results.append(("quiz-headless", "PASS", "SELFTEST score=5/5 pass=true"))
    else:
        results.append(("quiz-headless", "FAIL", p.stdout[-120:]))


def run_dualdoc():
    cur = r"D:/skills/electric-current"
    card = os.path.join(cur, "电流—通识可视化学习卡.md")
    plain = os.path.join(cur, "电流—通俗版.md")
    for f in (card, plain):
        if not os.path.isfile(f):
            results.append(("dualdoc-命名", "FAIL", f"缺 {f}")); return
    results.append(("dualdoc-命名", "PASS", "中文命名两件齐全"))
    cs, ps = os.path.getsize(card), os.path.getsize(plain)
    ratio = ps / cs * 100
    results.append(("dualdoc-篇幅", "PASS" if ratio <= 40 else "FAIL", f"通俗版/主卡 = {ratio:.1f}% (≤40%)"))
    meta = ["第一性原理", "原子事实", "推理链"]
    t = open(plain, encoding="utf-8").read()
    hit = [w for w in meta if w in t]
    results.append(("dualdoc-元词汇", "PASS" if not hit else "FAIL", f"禁用词命中: {hit or '无'}"))


def run_version():
    tech = open(os.path.join(BASE, "TECHNICAL.md"), encoding="utf-8").read()
    m = re.search(r"- (v\d+\.\d+\.\d+)（(\d{4}-\d{2}-\d{2})）", tech)
    latest = m.group(1) if m else "?"
    skill = open(os.path.join(BASE, "SKILL.md"), encoding="utf-8").read()
    mism = []
    if "3.10–3.12" in skill:
        mism.append("SKILL.md 仍含旧 Manim 版本断言 3.10–3.12")
    if "release 附件或示例目录" in open(os.path.join(REF, "extended-viz-2.md"), encoding="utf-8").read():
        mism.append("extended-viz-2.md 仍引用不存在的 release 附件")
    for f in ("manim-patterns.md", "visualization-cookbook.md", "3d-animation.md",
              "extended-viz.md", "extended-viz-2.md"):
        if not os.path.isfile(os.path.join(REF, f)):
            mism.append(f"缺 references/{f}")
    if not os.path.isfile(os.path.join(REF, "templates", "quiz-template.html")):
        mism.append("缺 references/templates/quiz-template.html")
    results.append(("version-consistency", "PASS" if not mism else "FAIL",
                    f"最新版本 {latest}；" + ("; ".join(mism) if mism else "断言全一致")))


run_blocks(); run_quiz(); run_dualdoc(); run_version()

print(f"{'回归项':<26}{'状态':<6}说明")
for label, st, note in results:
    print(f"{label:<26}{st:<6}{note}")
fails = [r for r in results if r[1] == "FAIL"]
print("\n汇总: PASS", sum(1 for r in results if r[1] == "PASS"),
      "/ SKIP", sum(1 for r in results if r[1] == "SKIP"),
      "/ FAIL", len(fails))
if fails:
    for label, st, note in fails:
        print(f"  FAIL -> {label}: {note}")
sys.exit(1 if fails else 0)
