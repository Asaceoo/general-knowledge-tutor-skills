# -*- coding: utf-8 -*-
"""按需调用图表：只渲染你点名的那一张，不必跑全部。

用法：
  python scripts/chart.py --list                # 全部图表（按分类）
  python scripts/chart.py --list 分布           # 按分类筛选
  python scripts/chart.py --search 相关         # 按关键词搜索
  python scripts/chart.py --json                # 机器可读清单
  python scripts/chart.py 箱线图                 # 渲染一张到 docs/images/charts/
  python scripts/chart.py 箱线图 --out ./box.png # 渲染并复制到指定路径
  python scripts/chart.py --all                 # 全量渲染 + 拼版（等价 chart_gallery.py）

退出码：0 成功 / 1 名称未知 / 2 运行错误
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chart_gallery as cg


def print_list(keyword=None):
    kw = keyword or None
    shown = 0
    for cat, names in cg.CATEGORY_GROUPS.items():
        rows = [n for n in names if (kw is None or kw in cat or kw in n)]
        if not rows:
            continue
        print(f"\n[{cat}]  ({len(rows)})")
        for n in rows:
            item = cg.REGISTRY.get(n)
            f = (item or {}).get("file") or "-"
            print(f"  {n:<12} -> {f}.png")
            shown += 1
    print(f"\n共 {shown} 种（总注册 {len(cg.REGISTRY)} 种）")
    return 0 if shown else 3


def main(argv):
    args = [a for a in argv[1:]]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if "--list" in args:
        i = args.index("--list")
        kw = args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("-") else None
        return print_list(kw)

    if "--json" in args:
        import json
        payload = {
            "total": len(cg.REGISTRY),
            "categories": {c: [n for n in ns if n in cg.REGISTRY]
                           for c, ns in cg.CATEGORY_GROUPS.items()},
            "charts": {n: {"category": v["category"], "file": v["file"]}
                       for n, v in cg.REGISTRY.items()},
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if "--search" in args:
        i = args.index("--search")
        if i + 1 >= len(args):
            print("[FAIL] --search 后缺少关键词")
            return 2
        return print_list(args[i + 1])

    if "--all" in args:
        return cg.main()

    out = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            print("[FAIL] --out 后缺少路径")
            return 2
        out = args[i + 1]

    names = [a for a in args if not a.startswith("-")]
    if "--out" in args:
        j = args.index("--out")
        names = [a for a in args[:j] + args[j + 2:] if not a.startswith("-")]
    if not names:
        print("[FAIL] 未指定图表名；用 --list 查看可用名称")
        return 2

    name = names[0]
    if name not in cg.REGISTRY:
        close = [n for n in cg.REGISTRY if name in n or n in name]
        print(f"[FAIL] 未知图表: {name}")
        if close:
            print("       相近: " + "、".join(close[:5]))
        else:
            print("       用 --list 查看全部可用名称")
        return 1

    try:
        path = cg.render_one(name, out)
    except Exception as e:
        print(f"[FAIL] 渲染失败 {name}: {type(e).__name__}: {e}")
        return 2
    size = os.path.getsize(path)
    if size < 1024:
        print(f"[FAIL] 产物过小（{size} 字节），可能空白: {path}")
        return 2
    print(f"[OK] {name} -> {path} ({size} 字节)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))