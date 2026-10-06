# 对抗性审查台账（audit-checklist）

> 2026-10-06 首轮三视角对抗性审查（audit-loop 工作流）。审查对象：SKILL.md + references/ 全部 5 个 md + templates/ + 电流实例交付。
> 证据纪律：每个结论有真实工具输出背书；回归命令见文末，修复后基线 **25 PASS / 2 SKIP / 0 FAIL**。

## 问题台账

| # | 视角 | 问题 | 真实证据（原文） | 修法 | 状态 |
|---|---|---|---|---|---|
| 1 | 实现者 | pymunk 模板只 `space.add(joint)` 未 add body → **摆不被模拟且无任何报错**，measure_period 无守卫返回 `0/(0-1)=-0.0`（静默错误结果） | 回归输出 `θ0=60° T=-0.0000s` | 模板改 `space.add(body, joint)`；measure_period 加 `len(zeros)<2 抛错` 守卫；坑表新增 #0 | ✅ |
| 2 | 实现者 | PyVista 体渲染模板多维标量未 ravel：新版 pyvista 严格校验，`(40,40,40)` 被判「40 个标量」；`np.c_[a,b,c]` 得 `(40,40,120)` 同炸 | `ValueError: Number of scalars (40) must match either the number of points (64000)...` | `v` 与 `vec` 均显式 `ravel(order="F")`（vec 修复曾漏，二次回归抓回） | ✅ |
| 3 | 实现者 | vpython 依赖 `pkg_resources`，**setuptools ≥81 已移除该模块**（新环境默认 84.x 直接炸） | `ModuleNotFoundError: No module named 'pkg_resources'`（装完 setuptools 84 仍复现→才定位版本根因） | 坑注：先 `pip install "setuptools<81"` 再装 vpython | ✅ |
| 4 | 实现者 | graphviz 模板声称「pip install graphviz 即可」，实际只装 Python 绑定 | `ExecutableNotFound: failed to execute WindowsPath('dot')` | 模板注释纠正：dot.exe 需单独装 Graphviz 系统包；无则降级 pyvis/Mermaid；回归显式 SKIP | ✅ |
| 5 | 实现者 | cookbook 动画块依赖上一块的 import（单独复制即 `NameError: plt`） | `NameError: name 'plt' is not defined` | 块内补独立 import | ✅ |
| 6 | AI 使用方 | quiz 完整模板写成「见本仓库 release 附件或示例目录」——**两者当时都不存在**，照文档找不到模板 | 文档检索无该文件 | 模板入库 `references/templates/quiz-template.html`，文档指向真实路径 | ✅ |
| 7 | 审查者 | SKILL.md 断言「Manim 渲染需 3.10–3.12」与真机矛盾 | `deeptutor env: Python 3.13.14 + manim 0.21.0`（傅里叶实例已渲染） | 改「3.10–3.13（0.21.0 已实测于 3.13.14）」 | ✅ |
| 8 | AI 使用方 | description 触发词未覆盖双文档/自测/记忆卡场景 | ——（文本审查） | 补「通俗版 / 讲给外行听 / 出几道题测测我 / 记忆卡」 | ✅ |
| 9 | 审查者 | test-prompts.json 停在 v1.0.0（6 用例，无新能力覆盖） | 字段 version=1.0.0, date=2026-10-05 | 升 v1.2.1：+3 should_trigger（物理模拟/双文档+自测/3D 可交互）+2 should_not_trigger | ✅ |
| 10 | 审查者 | TECHNICAL §3 章节乱序（3.3→3.5→3.4→3.6） | 标题行序检查 | 3.4/3.5 对调，README 引用同步 §3.4–3.6 | ✅ |
| 11 | 实现者 | genanki 模板 `CARDS` 未定义即使用（占位不明） | `NameError: name 'CARDS' is not defined` | 模板内嵌占位示例行 + 注释说明 | ✅ |
| 12 | 实现者 | manim-voiceover 可装不可跑：清华镜像无源；gtts 后端缺 extra 时**交互式询问安装→headless 挂死（exit 124）**；装齐后 gtts 依赖 translate.google.com 不可达（`--dry_run` 也过不了） | `Exception: gTTS gave an error...`；`Shall I install them for you? [Y/n]` 后挂死 | 文档升级为「⚠️ 实测受限」+ 完整证据链 + 绕行路径（edge-tts 独立 mp3） | ✅（受限豁免） |
| 13 | 实现者 | bpy 模板依赖 330MB Blender wheel | `ModuleNotFoundError: No module named 'bpy'` | 回归显式 SKIP + 文档保留（环境具备时执行） | ✅（SKIP 豁免） |

## 对抗性输入测试记录（Playwright 真机）

| 场景 | 注入 | 期望 | 实测 |
|---|---|---|---|
| quiz 空选提交 | 不选任何 radio 调 `grade()` | 0/5 未通过、不崩溃 | ✅ `未通过：0/5` result 可见 |
| quiz 全错提交 | 每题选错误项 | 0/5、错误项标红、正确项标绿 | ✅ wrong=5, right=5 |
| quiz 全对提交 | `#selftest` hash | 5/5 通过 | ✅ `SELFTEST score=5/5 pass=true` |
| Mermaid DAG 语法 | CDN mermaid@11 渲染模板块 | svg 生成 | ✅ `RENDER_OK nodes=6` |
| 3D 单文件 HTML | model-viewer + base64 glb | 3D 渲染 | ✅ 截图（环面/剖切导线两例） |

## 回归命令（修复后基线 25 PASS / 2 SKIP / 0 FAIL）

```bash
python scripts/regression.py   # 代码块真机执行 + quiz headless + 双文档约束 + 版本一致性
```

SKIP 豁免名单（环境受限，非模板缺陷）：graphviz#2（需 dot.exe 二进制）、3d-animation#5（需 bpy）。

---

# 第三批对抗性审查台账（2026-10-06，v1.2.2 基线 → v1.3.0）

> 对象：README/TECHNICAL 手册 + scripts/package.py + quiz 模板 + 命名规则。三视角：实现者（边界输入）/ 审查者（文档-实物一致）/ AI 使用方（照文档能走通）。修复后回归仍 **25 PASS / 2 SKIP / 0 FAIL**。

| # | 视角 | 问题 | 真实证据（原文） | 修法 | 状态 |
|---|---|---|---|---|---|
| R4-1 | 审查者 | test-prompts.json version 字段漂移（v1.2.2 发布时漏同步） | `"version": "1.2.1"` vs VERSION=1.2.2 | 纳入 package.py 自动同步（--bump 联动） | ✅ |
| R4-2 | 审查者 | TECHNICAL §3.6 物理位置在 §3.5 前（上批 3.4/3.5 对调遗留） | §3.x 顺序实测 `['3.1','3.2','3.3','3.4','3.6','3.5']` | 3.5/3.6 物理调换，编号不变 | ✅ |
| R4-8 | 审查者 | TECHNICAL §3.6 写「7 条实测坑」且漏 pymunk 静默坑、genanki 固定 ID（上批 7→9 修正只改了 SKILL.md 的姊妹遗漏） | L136 原文「第二批次实测坑（7 条…）：PillowWriter…」 | 补全为 9 条（含 pymunk `space.add(body, joint)` 与 genanki 固定 ID） | ✅ |
| R4-3 | 审查者 | README 无当前版本锚点；三手册版本号无自动递增机制 | 静态扫描 `README当前版本字段=无` | README 加「> 当前版本：」锚点行；package.py v2 `--bump` 联动递增 README/TECHNICAL §7/test-prompts.json 三处 | ✅ |
| R4-4 | AI 使用方 | README 实例 3 承诺「要手绘风」「要白板讲解」都会被采纳，但 SKILL.md 选型矩阵/工具箱无此能力 | grep SKILL.md「白板」0 命中；「手绘」仅出现在降级产物描述 | 点名说法换为真实能力：「要真实物理模拟」「要带配音讲解」 | ✅ |
| R4-5 | 实现者 | package.py 边界输入裸崩溃 | `--bump foo` → 裸 `KeyError: 'foo'`；VERSION='abc' → 裸 `ValueError` | v2 加校验：level 白名单 + VERSION 格式正则，中文报错退出。真机复测三用例全部 `[FAIL] ...优雅提示` | ✅ |
| R4-6 | 实现者 | quiz 模板 `innerHTML` 三处插值（题干/选项/解析）无转义：`<img onerror>` 可注入、`a<b` 破版式 | 双 Case 真机对照：剥 esc 后注入生效（真实 `<img>` 元素入 DOM + `document.title` 被篡改为 'XSS fired'） | 模板内置 `esc()` 包裹全部动态插值；修复后同载荷 3 判据全 PASS（注入不执行/title 不变/判分 5/5 不回归） | ✅ |
| R4-7 | AI 使用方 | 文件命名规则不覆盖主题含非法文件名字符（如 TCP/IP、含 `:` 的主题）——Windows 下直接建文件报错 | SKILL.md 命名块无净化条款 | 补「主题名净化」：非法字符替换为「－」；C++/DNA/GDP 等缩写可与中文混排 | ✅ |

## 第三批新坑回灌（不只修代码不回灌）

- TECHNICAL §3.2 坑表 + extended-viz-2.md quiz 坑表新增两条：①`esc()` 转义对策（含实测证据）；②**QUIZ 源码内联数据含字面 `</script>` 会截断 HTML `<script>` 块**（HTML 解析层截断，任何运行时转义不可防，写 `<\/script>` 绕行）——对抗过程中真实踩到（首次 probe 载荷含 `</script>` 导致整页 JS 断裂、SELFTEST NOT FOUND）。

## 第三批回归/对抗命令

```bash
python scripts/regression.py                    # 全量回归（修复后仍 25 PASS / 2 SKIP / 0 FAIL）
python _audit_v121/audit_r4_scan.py             # 审查者视角静态扫描（版本一致性/引用/语法/断言互查）
python _audit_v121/audit_r4_pkg.py              # 实现者视角：package.py 边界 4 用例
python _audit_v121/audit_r4_xss.py              # 实现者视角：quiz XSS 双 Case 真机对照
```

> 注：audit_r4_scan.py 的 B1「README 引用 MISS」为扫描器自身正则吃进反引号的假阳性（文件实际存在），已复核排除；「3D 五层」措辞差异（README「3D 分五层」）同为关键词匹配假阳性，能力链在 TECHNICAL §3.3 完整。

---

## 第四批（v1.4.0 基线，2026-10-06）

| # | 视角 | 问题 | 真机证据 | 修法 | 状态 |
|---|---|---|---|---|---|
| R5-1 | 实现者 | **`--bump patch` 静默不递增**：`bump()` 的 patch 分支写成 `f"{a}.{b}.{c}"`（c 未 +1），exit=0 且照常打包 → 打出与旧版同名的 zip 覆盖原产物，用户以为发布了新版本 | 隔离副本真机：`VERSION 1.4.0 --bump patch → VERSION=1.4.0`，exit=0，产物名 `...-v1.4.0.zip` | patch 分支改 `c+1`；并加防御断言「递增后必须 != 旧值，否则 fail（禁止静默复用旧版本号）」 | ✅ |
| R5-2 | 实现者 | `--note` / `--bump` 置于末位缺值 → 裸 `IndexError: list index out of range`（v2 新增参数未做边界校验，是 R4-5 的同类遗漏） | 真机：`['--bump','patch','--note']` 与 `['--bump']` 均抛 IndexError + Traceback | 新增 `opt_val(flag)`：缺值 / 末位 / 后接另一个 flag 一律 `[FAIL] xx 后缺少取值（正确用法：--xx <值>）` | ✅ |
| R5-3 | 实现者 | README 无版本锚点时的「自动插入」分支从未被真机验证（首轮因 R5-1 连带失败被误判） | 真机 T9：删除锚点行后跑 `--bump patch`，插入结果 False | 修 R5-1 后复测：锚点自动插入 True，9/9 用例全 PASS | ✅ |
| R5-4 | 审查者 | TECHNICAL §1 目录树严重滞后：缺 `extended-viz-2.md`、`audit-checklist.md`、`templates/`、`scripts/`、`VERSION`；且正文仍写「**纯声明式技能——不包含任何可执行脚本**」，与已存在的 `scripts/package.py`、`scripts/regression.py` 自相矛盾 | 静态扫描 A3 系列：磁盘 6 个 references + 1 模板 + 2 脚本，目录树仅列 4 个 | 目录树补全（含 `templates/`、`scripts/`、`VERSION`）；定位描述改为「声明式技能 + 两个工程脚本（仅服务打包/回归，不参与运行时交付）」 | ✅ |
| R5-5 | 审查者 | TECHNICAL §5.2 称「内置 6 条反模式」，SKILL.md 实测 **8 条**（与历史上 7→9 计数漂移同源） | 扫描 A1：`TECHNICAL=6 vs SKILL.md 实测=8` | 改为 8 条并列举；回归新增 `doc-黑名单计数` 断言永久防复发 | ✅ |
| R5-6 | 审查者 | TECHNICAL Phase 4 选型矩阵 **10 行** vs SKILL.md **13 行**（缺 Mermaid / pymunk / 配音+自测+3D 单文件三行） | 扫描 A2：`SKILL.md=13 vs TECHNICAL=10` | TECHNICAL 补 3 行；回归新增 `doc-选型矩阵行数` 断言 | ✅ |
| R5-7 | 审查者 | TECHNICAL §5.4 质量评分记录只写到第二轮（88.45），缺第三轮（94.1 + ROI 网关跳过结论） | 扫描 A5：§5.4 仅两轮表格 | 补「第三轮」小节（含 10 维明细与真机证据来源） | ✅ |
| R5-8 | AI 使用方 | **Phase 0 指令撞墙**：要求「一次性弹出五项让用户点选」，但主流结构化提问组件一次最多 4 个问题 → 模型照做会失败并退化成开放式追问（与「禁止开放式追问」自相矛盾） | 扫描 B3：需弹选项维度 ≥4（上限 4），且无任何分批/合并兜底说明 | SKILL.md 新增「提问能力约束」5 条：主题不单列、深度+覆盖范围可合并为 1 问、超限则分批（首批答完即开工）、无提问能力时走默认值；TECHNICAL §2 同步 | ✅ |
| R5-9 | AI 使用方 | 多选维度（可视化形式）未说明须声明为多选，且「可全不选」在提问组件中**无对应机制**（用户无法表达「不选」） | 扫描 B4b：仅缺省策略兜底，无选项级兜底 | 明确「须声明为多选」+ 必须提供「自动（交给技能决定）」显式选项 | ✅ |
| R5-10 | AI 使用方 | SKILL.md「深度=精通/**交付**时交付双文档」——「交付」不是深度档位名（档位为 速览/精通/**输出**），属术语漂移 | 扫描 B6 命中 `深度=精通/交付时交付` | 改为「深度=精通/输出时」 | ✅ |
| R5-11 | AI 使用方 | SKILL.md「配套资源」未列 `audit-checklist.md` 与 `templates/quiz-template.html`——AI 使用方做自测/记忆卡时不知道有现成模板，事后校验也无清单入口 | 扫描 B7：两项 MISS | 补两行引用（含 `#selftest` 断言用法与「改动后必跑回归」提示） | ✅ |
| R5-12 | AI 使用方 | 第二批次产物（mp3 / 自测 HTML / apkg / 3D HTML）**无命名约定**——「电流」实例自行命名，换会话即不一致 | 对照 `D:\skills\electric-current\` 实际命名 vs SKILL.md 命名块无相关条款 | 命名块补「第二批次产物命名」：`[主题]—语音讲解.mp3` / `—自测N题.html` / `—记忆卡.apkg` / `—3D结构.html` | ✅ |
| R5-13 | 实现者 | 回归未覆盖 v1.4.0 新功能（Phase 0 五项）与文档交叉一致性，属「常规验证未覆盖全部功能」 | 原回归仅 27 项，无 SKILL.md 结构断言 | regression.py 新增三组 18 项断言（Phase 0 结构 13 项 / 文档一致性 4 项 / package bump 真机 1 项）→ 43 PASS / 2 SKIP / 0 FAIL | ✅ |

### 第四批新坑回灌

- **静默失败比崩溃更危险**：`--bump patch` 未递增却 exit=0，会打出与旧版同名的压缩包覆盖产物。凡「版本号单一来源 + 自动递增」类脚本，必须加「递增后 != 旧值」断言（已写进 package.py 与回归用例）。
- **隔离沙箱脚本要排除 `.git`**：`shutil.rmtree` 清理含 `.git` 的临时副本会触发本机安全策略（PermissionError WinError 5）。构造隔离副本时 `ignore=ignore_patterns(".git", "dist", "_reg_work", "__pycache__")`，并给每次运行加唯一 ID，删除用 `ignore_errors=True`。
- **文档计数类漂移会反复发生**（7→9 坑、6→8 反模式、10→13 矩阵行）。根治方式不是人工核对，而是把「声称数 vs 实测数」写成回归断言（本批新增 `doc-黑名单计数`、`doc-选型矩阵行数`、`doc-目录树覆盖`、`doc-版本号四处一致`）。

### 第四批回归/对抗命令

```bash
python scripts/regression.py              # 全量回归（修复后 43 PASS / 2 SKIP / 0 FAIL）
python _audit_v121/audit_r5_scan.py        # 审查者 + AI使用方视角静态扫描（A1-A5 / B1-B7）
python _audit_v121/audit_r5_pkg.py         # 实现者视角：package.py 9 个边界用例（隔离副本真机）
```

> 注：audit_r5_scan.py 首版 B3「需弹选项 7 项」为 section 截断正则过宽（把 Phase 1–5 的编号项一并计入）导致的计数偏差，结论方向不变（5 维度 > 4 上限），已按修复后的 SKILL.md 复核。
