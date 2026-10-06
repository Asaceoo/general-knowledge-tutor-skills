# -*- coding: utf-8 -*-
"""一键打包：版本号单一来源 VERSION，自动递增，产物带版本号后缀
用法：
  python scripts/package.py                # 按 VERSION 当前值打包
  python scripts/package.py --bump patch   # 递增 patch 位再打包（1.2.1 -> 1.2.2）
  python scripts/package.py --bump minor   # 1.2.1 -> 1.3.0
"""
import os, sys, zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(BASE, "VERSION")
DIST = os.path.join(BASE, "dist")

INCLUDE = [
    "SKILL.md", "README.md", "TECHNICAL.md", "LICENSE", "test-prompts.json", "VERSION",
]

def read_version():
    return open(VERSION_FILE, encoding="utf-8").read().strip()

def bump(ver, level):
    a, b, c = (int(x) for x in ver.split("."))
    return {"major": f"{a+1}.0.0", "minor": f"{a}.{b+1}.0", "patch": f"{a}.{b}.{c+1}"}[level]

def collect_files():
    files = list(INCLUDE)
    for sub in ("references", os.path.join("references", "templates"), "scripts"):
        d = os.path.join(BASE, sub)
        for f in sorted(os.listdir(d)):
            if f.endswith((".md", ".json", ".py", ".html")) and not f.startswith("_"):
                files.append(os.path.join(sub, f))
    return files

def main():
    if "--bump" in sys.argv:
        level = sys.argv[sys.argv.index("--bump") + 1]
        new = bump(read_version(), level)
        open(VERSION_FILE, "w", encoding="utf-8").write(new + "\n")
        print(f"版本递增 {level}: -> {new}")
    ver = read_version()
    name = f"general-knowledge-tutor-skills-v{ver}.zip"
    out = os.path.join(DIST, name)
    os.makedirs(DIST, exist_ok=True)
    files = collect_files()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            p = os.path.join(BASE, rel)
            if not os.path.isfile(p):
                print(f"[FAIL] 清单文件缺失: {rel}"); sys.exit(1)
            z.write(p, f"general-knowledge-tutor-skills-{ver}/{rel}")
    with zipfile.ZipFile(out) as z:  # 完整性自校验
        bad = z.testzip()
        names = z.namelist()
    print(f"[OK] {name}: {os.path.getsize(out)} bytes, {len(names)} files, testzip={'PASS' if bad is None else 'FAIL:'+str(bad)}")
    print("产物清单:")
    for n in names: print("  ", n)

if __name__ == "__main__":
    main()
