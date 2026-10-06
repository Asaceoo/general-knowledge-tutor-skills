# -*- coding: utf-8 -*-
"""general-knowledge-tutor-skills 全量回归（audit-loop 清单兜底）
用法：python scripts/regression.py
覆盖：①references 全部 python 代码块真机执行（SKIP 名单显式豁免）
     ②quiz 模板 headless 判分断言  ③双文档命名/篇幅/元词汇 ④版本一致性
"""
import ast, json, os, re, shutil, subprocess, sys, tempfile

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


def count_table_rows(sec):
    rows = []
    for ln in sec.splitlines():
        s = ln.strip()
        if s.startswith("|") and not re.fullmatch(r"\|[\s\-:|]+\|", s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and cells[0] and not re.fullmatch(r"[-: ]+", cells[0]):
                rows.append(cells)
    return rows


def run_skill_struct():
    """Phase 0 结构化选项 + 命名约定：v1.4.0 新功能的清单兜底（防改动后静默退化）"""
    skill = open(os.path.join(BASE, "SKILL.md"), encoding="utf-8").read()
    checks = [
        ("phase0-深度档枚举", all(k in skill for k in ["速览", "精通", "输出"])),
        ("phase0-覆盖范围枚举", all(k in skill for k in ["单点", "带前置", "完整体系"])),
        ("phase0-基础枚举", all(k in skill for k in ["零基础", "有相关背景", "专业"])),
        ("phase0-可视化多选", all(k in skill for k in ["动画", "交互图", "3D", "配音", "记忆卡"])),
        ("phase0-禁止开放式追问", "禁止开放式追问" in skill),
        ("phase0-组合规则", "组合规则" in skill),
        ("phase0-提问上限约束", "提问能力约束" in skill and "4 个问题" in skill),
        ("phase0-自动兜底选项", "自动（交给技能决定）" in skill),
        ("phase0-多选声明", "须声明为多选" in skill),
        ("命名-双文档中文", "—通识可视化学习卡.md" in skill and "—通俗版.md" in skill),
        ("命名-第二批次产物", all(k in skill for k in
                              ["—语音讲解.mp3", "—自测N题.html", "—记忆卡.apkg", "—3D结构.html"])),
        ("命名-主题净化规则", "主题名净化" in skill),
        ("门控-STOP存在", "🛑 STOP" in skill),
    ]
    for label, ok in checks:
        results.append((label, "PASS" if ok else "FAIL", "SKILL.md 结构断言"))


def run_doc_consistency():
    """三份文档交叉一致性：计数 / 矩阵行数 / 目录树 / 四处版本号（历史上 7→9、6→8 均漂移过）"""
    skill = open(os.path.join(BASE, "SKILL.md"), encoding="utf-8").read()
    tech = open(os.path.join(BASE, "TECHNICAL.md"), encoding="utf-8").read()
    readme = open(os.path.join(BASE, "README.md"), encoding="utf-8").read()

    # 1) 反例黑名单条数：TECHNICAL 声称数 == SKILL.md 实测行数
    m = re.search(r"\n## 反例黑名单", skill)
    bl = skill[m.end():]
    m2 = re.search(r"\n## ", bl)
    bl_rows = [r for r in count_table_rows(bl[:m2.start()] if m2 else bl) if r[0] != "反模式"]
    m3 = re.search(r"内置 \*\*(\d+) 条\*\*反模式", tech) or re.search(r"内置 (\d+) 条反模式", tech)
    claim = int(m3.group(1)) if m3 else -1
    results.append(("doc-黑名单计数", "PASS" if claim == len(bl_rows) else "FAIL",
                    f"TECHNICAL声称 {claim} vs SKILL.md 实测 {len(bl_rows)}"))

    # 2) Phase 4 选型矩阵行数：两份文档必须同构
    def matrix(text, start_re, end_re):
        m = re.search(start_re, text)
        seg = text[m.end():]
        m2 = re.search(end_re, seg)
        return [r for r in count_table_rows(seg[:m2.start()] if m2 else seg) if r[0] != "概念类型"]
    sm = matrix(skill, r"\n### Phase 4 — 可视化生产", r"\n### Phase 5")
    tm = matrix(tech, r"\n### Phase 4 可视化生产", r"\n\*\*3D 启用门槛")
    results.append(("doc-选型矩阵行数", "PASS" if len(sm) == len(tm) else "FAIL",
                    f"SKILL.md {len(sm)} 行 vs TECHNICAL {len(tm)} 行"))

    # 3) 目录树覆盖磁盘真实结构
    m = re.search(r"\n## 1\. 系统架构", tech)
    tree = tech[m.end():]
    m2 = re.search(r"\n## ", tree)
    tree = tree[:m2.start()] if m2 else tree
    miss = []
    for f in sorted(os.listdir(REF)):
        if f.endswith(".md") and f not in tree:
            miss.append(f"references/{f}")
    for f in sorted(os.listdir(os.path.join(REF, "templates"))):
        if f"{f}" not in tree:
            miss.append(f"templates/{f}")
    for f in sorted(os.listdir(os.path.join(BASE, "scripts"))):
        if f.endswith(".py") and f not in tree:
            miss.append(f"scripts/{f}")
    if "VERSION" not in tree:
        miss.append("VERSION")
    results.append(("doc-目录树覆盖", "PASS" if not miss else "FAIL", f"未提及: {miss or '无'}"))

    # 4) 版本号四处一致：VERSION / README 锚点 / TECHNICAL 版本史 / test-prompts
    ver = open(os.path.join(BASE, "VERSION"), encoding="utf-8").read().strip()
    ra = re.search(r"当前版本：v(\d+\.\d+\.\d+)", readme)
    tl = re.search(r"- v(\d+\.\d+\.\d+)（\d{4}-\d{2}-\d{2}）", tech)
    tp = json.load(open(os.path.join(BASE, "test-prompts.json"), encoding="utf-8")).get("version")
    vals = {"VERSION": ver,
            "README": ra.group(1) if ra else "?",
            "TECHNICAL": tl.group(1) if tl else "?",
            "test-prompts": tp}
    ok = len(set(vals.values())) == 1
    results.append(("doc-版本号四处一致", "PASS" if ok else "FAIL", str(vals)))


def run_package_bump():
    """package.py --bump patch 真机递增（历史缺陷：patch 分支未 +1，静默打同名 zip）"""
    tmp = os.path.join(tempfile.gettempdir(), f"_reg_pkg_{os.getpid()}")
    shutil.rmtree(tmp, ignore_errors=True)
    try:
        shutil.copytree(BASE, tmp, ignore=shutil.ignore_patterns(
            "dist", "_reg_work", "__pycache__", ".git"))
        old = open(os.path.join(tmp, "VERSION"), encoding="utf-8").read().strip()
        a, b, c = (int(x) for x in old.split("."))
        expect = f"{a}.{b}.{c + 1}"
        p = subprocess.run([sys.executable, os.path.join(tmp, "scripts", "package.py"),
                            "--bump", "patch", "--note", "regression-selftest"],
                           capture_output=True, timeout=180, cwd=tmp,
                           text=True, encoding="utf-8", errors="replace")
        new = open(os.path.join(tmp, "VERSION"), encoding="utf-8").read().strip()
        out = p.stdout + p.stderr
        ok = p.returncode == 0 and new == expect and "Traceback" not in out
        results.append(("package-bump-patch", "PASS" if ok else "FAIL",
                        f"{old} -> {new}（期望 {expect}）"))
    except Exception as e:
        results.append(("package-bump-patch", "FAIL", f"{type(e).__name__}: {e}"))
    shutil.rmtree(tmp, ignore_errors=True)


run_blocks(); run_quiz(); run_dualdoc(); run_skill_struct()
run_doc_consistency(); run_package_bump(); run_version()

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
