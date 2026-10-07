# -*- coding: utf-8 -*-
"""交互 / 3D 产物自测（SELFTEST 约定）——Chrome headless 真机断言

为什么需要它：静态图能靠肉眼，交互产物（canvas / WebGL / 滑块组件）必须机器断言
「真的画出来了、交互真的生效」，否则交付的可能是白屏或死控件。

用法：
  python scripts/selftest_web.py                      # 自检内置模板
  python scripts/selftest_web.py 产物.html            # 断言某产物（默认加 #selftest）
  python scripts/selftest_web.py 产物.html --hash ''  # 页面自行决定何时跑自测
  python scripts/selftest_web.py 产物.html --json     # 机器可读输出

约定（页面侧）：暴露 window.__SELFTEST__() → {pass, checks, note}；
以 #selftest 打开时把结果写入 DOM，形如 SELFTEST {"pass":true,...}。
兼容 quiz 模板的 SELFTEST score=N/M pass=true 形式。

退出码：0 = 全部通过；1 = 断言失败；2 = 环境问题（找不到 Chrome / 文件 / 超时）
"""
import argparse, json, os, re, shutil, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TARGET = os.path.join(BASE, "references", "templates", "selftest-web-template.html")
JSON_RE = re.compile(r"SELFTEST\s+(\{.*?\})\s*[<\n]")
QUIZ_RE = re.compile(r"SELFTEST score=(\d+)/(\d+) pass=(true|false)")


def find_chrome(explicit=None):
    cands = [explicit, os.environ.get("CHROME"),
             r"C:/Program Files/Google/Chrome/Application/chrome.exe",
             r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
             r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
             shutil.which("chrome"), shutil.which("chromium"), shutil.which("msedge")]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def run_selftest(target, anchor="selftest", timeout=60, budget=6000, chrome=None):
    exe = find_chrome(chrome)
    if not exe:
        return {"status": "env", "pass": False, "note": "未找到 Chrome/Edge（可用 --chrome 或 CHROME 环境变量指定）"}
    if not os.path.isfile(target):
        return {"status": "env", "pass": False, "note": f"文件不存在: {target}"}
    url = "file:///" + os.path.abspath(target).replace(os.sep, "/")
    if anchor:
        url += "#" + anchor
    # 个别 Chrome 版本需要显式允许软件 WebGL；未知该标志的版本会忽略它，故可无条件带上
    cmd = [exe, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--enable-unsafe-swiftshader",
           f"--virtual-time-budget={budget}", "--dump-dom", url]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout,
                           text=True, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return {"status": "env", "pass": False, "note": f"Chrome 超时（{timeout}s）"}
    dom = p.stdout or ""
    m = JSON_RE.search(dom) or re.search(r"SELFTEST\s+(\{.*?\})", dom)
    if m:
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            return {"status": "fail", "pass": False, "note": f"SELFTEST JSON 解析失败: {e}"}
        return {"status": "pass" if data.get("pass") else "fail",
                "pass": bool(data.get("pass")),
                "checks": data.get("checks", {}),
                "failed": data.get("failed", []),
                "note": data.get("note", ""),
                "target": target}
    q = QUIZ_RE.search(dom)
    if q:
        ok = q.group(1) == q.group(2) and q.group(3) == "true"
        return {"status": "pass" if ok else "fail", "pass": ok,
                "note": f"quiz 形式: score={q.group(1)}/{q.group(2)} pass={q.group(3)}", "target": target}
    return {"status": "fail", "pass": False,
            "note": "DOM 中没有 SELFTEST 结果——页面未实现约定，或 #selftest 分支未触发"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="交互/3D 产物 SELFTEST 断言（Chrome headless）")
    ap.add_argument("target", nargs="?", default=DEFAULT_TARGET,
                    help="待测 HTML（缺省为内置模板自检）")
    ap.add_argument("--hash", dest="anchor", default="selftest", help="URL 锚点，默认 selftest")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--budget", type=int, default=6000, help="Chrome virtual-time-budget(ms)")
    ap.add_argument("--chrome", default=None)
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    res = run_selftest(args.target, args.anchor, args.timeout, args.budget, args.chrome)
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"[{'PASS' if res['pass'] else res['status'].upper()}] {os.path.basename(args.target)}")
        for k, v in (res.get("checks") or {}).items():
            print(f"    {k}: {v}")
        if res.get("note"):
            print(f"    note: {res['note']}")
        if res.get("failed"):
            print(f"    失败项: {res['failed']}")
    return 0 if res["pass"] else (2 if res["status"] == "env" else 1)


if __name__ == "__main__":
    sys.exit(main())
