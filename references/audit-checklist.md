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
