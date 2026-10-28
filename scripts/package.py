# -*- coding: utf-8 -*-
"""一键打包：版本号单一来源 VERSION，自动递增，产物带版本号后缀
用法：
  python scripts/package.py                # 按 VERSION 当前值打包
  python scripts/package.py --bump patch   # 递增 patch 位再打包（1.2.1 -> 1.2.2）
  python scripts/package.py --bump minor   # 1.2.1 -> 1.3.0
  python scripts/package.py --bump minor --note "变更一句话"
--bump 时自动同步版本号到三处手册（用户手册 / 技术手册 / 测试用例）：
  1. README.md   「> 当前版本：vX.Y.Z（YYYY-MM-DD）」锚点行（无则插入）
  2. TECHNICAL.md §7 版本史顶部插入条目（描述取 --note，缺省为自动登记说明）
  3. test-prompts.json  "version" 字段
"""
import datetime, json, os, re, sys, zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(BASE, "VERSION")
DIST = os.path.join(BASE, "dist")

INCLUDE = [
    "SKILL.md", "README.md", "USER_GUIDE.md", "TECHNICAL.md",
    "LICENSE", "test-prompts.json", "VERSION",
]

def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def read_version():
    try:
        ver = open(VERSION_FILE, encoding="utf-8").read().strip()
    except FileNotFoundError:
        fail(f"VERSION 文件不存在: {VERSION_FILE}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
        fail(f"VERSION 内容格式非法（应为 X.Y.Z）: {ver!r}")
    return ver

def bump(ver, level):
    if level not in ("patch", "minor", "major"):
        fail(f"--bump 仅支持 patch / minor / major，收到: {level!r}")
    a, b, c = (int(x) for x in ver.split("."))
    new = {"major": f"{a+1}.0.0", "minor": f"{a}.{b+1}.0", "patch": f"{a}.{b}.{c+1}"}[level]
    if new == ver:  # 防御：任何档位都必须产生变化，避免静默打同名产物
        fail(f"版本递增失败：{level} 档计算后仍为 {ver}（禁止静默复用旧版本号）")
    return new


def opt_val(flag):
    """安全取 `--flag <值>`：缺值 / 置于末位 / 后接另一个 flag 时优雅报错，不抛 IndexError。"""
    if flag not in sys.argv:
        return None
    i = sys.argv.index(flag)
    if i + 1 >= len(sys.argv) or sys.argv[i + 1].startswith("--"):
        fail(f"{flag} 后缺少取值（正确用法：{flag} <值>）")
    return sys.argv[i + 1]

def preflight_manuals():
    """递增前预检：三份手册的锚点必须可定位。

    历史缺陷（回归 T6 复现）：旧实现先写 VERSION 再同步手册，同步失败时留下
    「VERSION 已递增、手册没更新」的半成品，且技术手册版本史出现断档
    （实测 1.5.11 -> 1.5.9，缺 1.5.10）。现在所有预检都在任何写入之前完成。
    """
    for name in ("README.md", "USER_GUIDE.md"):
        path = os.path.join(BASE, name)
        if not os.path.isfile(path):
            fail(f"缺少手册文件: {name}（三份手册缺一不可：README / USER_GUIDE / TECHNICAL）")
        txt = open(path, encoding="utf-8").read()
        has_anchor = re.search(r"> 当前版本：v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）", txt)
        if not has_anchor and "\n---\n" not in txt:
            fail(f"{name} 找不到「> 当前版本：」锚点，也找不到 '---' 插入位")
    tech_path = os.path.join(BASE, "TECHNICAL.md")
    if not os.path.isfile(tech_path):
        fail("缺少手册文件: TECHNICAL.md")
    if "## 7. 版本" not in open(tech_path, encoding="utf-8").read():
        fail("TECHNICAL.md 找不到 '## 7. 版本' 标题（版本史插入会失败）")


def sync_manuals(new_ver, note):
    """--bump 后把新版本号同步进用户手册 / 技术手册 / 测试用例。"""
    date = datetime.date.today().isoformat()
    tag = f"v{new_ver}"

    # 1) README.md / USER_GUIDE.md 锚点行（门面 + 用户手册，各自独立版本锚点）
    anchor = f"> 当前版本：{tag}（{date}）· 更新日志见 [TECHNICAL.md](TECHNICAL.md) §7"
    for name in ("README.md", "USER_GUIDE.md"):
        p = os.path.join(BASE, name)
        txt = open(p, encoding="utf-8").read()
        if re.search(r"> 当前版本：v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）", txt):
            txt = re.sub(r"> 当前版本：v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）[^\n]*", anchor, txt, count=1)
        else:  # 无锚点 → 插入到首个水平分隔线前
            idx = txt.find("\n---\n")
            if idx < 0:
                fail(f"{name} 找不到锚点替换位，也找不到 '---' 插入位")
            txt = txt[:idx] + "\n" + anchor + txt[idx:]
        open(p, "w", encoding="utf-8", newline="\n").write(txt)
        print(f"[SYNC] {name} -> {anchor}")

    # 2) TECHNICAL.md §7 版本史顶部插入
    p = os.path.join(BASE, "TECHNICAL.md")
    txt = open(p, encoding="utf-8").read()
    entry = f"- {tag}（{date}）：{note}"
    if re.search(rf"- {re.escape(tag)}（\d{{4}}-\d{{2}}-\d{{2}}）", txt):
        print(f"[SYNC] TECHNICAL.md 已含 {tag} 条目，跳过插入")
    else:
        txt2, n = re.subn(r"(## 7\. 版本\n\n)", rf"\g<1>{entry}\n", txt, count=1)
        if n != 1:
            fail("TECHNICAL.md 找不到 '## 7. 版本' 标题（版本史插入失败）")
        open(p, "w", encoding="utf-8", newline="\n").write(txt2)
        print(f"[SYNC] TECHNICAL.md §7 -> {entry}")

    # 3) test-prompts.json version 字段
    p = os.path.join(BASE, "test-prompts.json")
    data = json.load(open(p, encoding="utf-8"))
    if data.get("version") != new_ver:
        data["version"] = new_ver
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[SYNC] test-prompts.json version -> {new_ver}")
    else:
        print(f"[SYNC] test-prompts.json 已是 {new_ver}，跳过")

def collect_files():
    files = list(INCLUDE)
    for sub in ("references", os.path.join("references", "templates"), "scripts"):
        d = os.path.join(BASE, sub)
        for f in sorted(os.listdir(d)):
            if f.endswith((".md", ".json", ".py", ".html")) and not f.startswith("_"):
                files.append(os.path.join(sub, f))
    # 文档配图递归入包（README 概念图 / 图表画廊），避免包内文档图片链接失效。
    # 早期实现只扫一层，导致 docs/images/charts/* 全部漏包（v1.6.0 修复）。
    img_root = os.path.join(BASE, "docs", "images")
    for dirpath, _dirs, fnames in os.walk(img_root):
        for f in sorted(fnames):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".webp")):
                full = os.path.join(dirpath, f)
                files.append(os.path.relpath(full, BASE))
    return files

def main():
    note = "版本发布（package.py 自动登记，变更摘要见 git log 与 audit-checklist）"
    nv = opt_val("--note")
    if nv is not None:
        note = nv
    if "--bump" in sys.argv:
        level = opt_val("--bump")
        old = read_version()
        new = bump(old, level)
        preflight_manuals()      # 预检：锚点缺失在这里失败，磁盘未被改动
        sync_manuals(new, note)  # 再同步三份手册 + test-prompts
        open(VERSION_FILE, "w", encoding="utf-8").write(new + "\n")  # VERSION 最后落盘
        print(f"版本递增 {level}: {old} -> {new}")
    ver = read_version()
    name = f"general-knowledge-tutor-skills-v{ver}.zip"
    out = os.path.join(DIST, name)
    os.makedirs(DIST, exist_ok=True)
    files = collect_files()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            p = os.path.join(BASE, rel)
            if not os.path.isfile(p):
                fail(f"清单文件缺失: {rel}")
            z.write(p, f"general-knowledge-tutor-skills-{ver}/{rel}")
    with zipfile.ZipFile(out) as z:  # 完整性自校验
        bad = z.testzip()
        names = z.namelist()
    print(f"[OK] {name}: {os.path.getsize(out)} bytes, {len(names)} files, testzip={'PASS' if bad is None else 'FAIL:'+str(bad)}")
    print("产物清单:")
    for n in names: print("  ", n)

if __name__ == "__main__":
    main()
