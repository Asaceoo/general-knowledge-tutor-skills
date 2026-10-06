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
    "SKILL.md", "README.md", "TECHNICAL.md", "LICENSE", "test-prompts.json", "VERSION",
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
    return {"major": f"{a+1}.0.0", "minor": f"{a}.{b+1}.0", "patch": f"{a}.{b}.{c}"}[level]

def sync_manuals(new_ver, note):
    """--bump 后把新版本号同步进用户手册 / 技术手册 / 测试用例。"""
    date = datetime.date.today().isoformat()
    tag = f"v{new_ver}"

    # 1) README.md 锚点行
    p = os.path.join(BASE, "README.md")
    txt = open(p, encoding="utf-8").read()
    anchor = f"> 当前版本：{tag}（{date}）· 更新日志见 [TECHNICAL.md](TECHNICAL.md) §7"
    if re.search(r"> 当前版本：v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）", txt):
        txt = re.sub(r"> 当前版本：v\d+\.\d+\.\d+（\d{4}-\d{2}-\d{2}）[^\n]*", anchor, txt, count=1)
    else:  # 无锚点 → 插入到首个水平分隔线前
        idx = txt.find("\n---\n")
        if idx < 0:
            fail("README.md 找不到锚点替换位，也找不到 '---' 插入位")
        txt = txt[:idx] + "\n" + anchor + txt[idx:]
    open(p, "w", encoding="utf-8", newline="\n").write(txt)
    print(f"[SYNC] README.md -> {anchor}")

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
    return files

def main():
    note = "版本发布（package.py 自动登记，变更摘要见 git log 与 audit-checklist）"
    if "--note" in sys.argv:
        note = sys.argv[sys.argv.index("--note") + 1]
    if "--bump" in sys.argv:
        level = sys.argv[sys.argv.index("--bump") + 1]
        old = read_version()
        new = bump(old, level)
        open(VERSION_FILE, "w", encoding="utf-8").write(new + "\n")
        print(f"版本递增 {level}: {old} -> {new}")
        sync_manuals(new, note)
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
