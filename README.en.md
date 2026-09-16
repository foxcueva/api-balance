════════════════════════════════════════════════
 Snail Mail 仓库 · 电脑操作指引（2026-09-14）
 前提：手机上已完成改名 envelope-templates → snail-mail
 上传包：snail-mail_全量上传包_20260914.zip（已解压）
════════════════════════════════════════════════

【第 1 步 · 打开上传页】
浏览器进 https://github.com/foxcueva/snail-mail
→ 右上 Add file ▾ → Upload files

【第 2 步 · 拖入 4 样】
打开解压出来的 snail-mail 文件夹，把里面这 4 样
一起选中，拖进上传区：
  ① envelope 文件夹（整个拖，自动带路径）
  ② README.md
  ③ README.zh-CN.md
  ④ LICENSE
⚠️ 拖的是「snail-mail 文件夹里面的东西」，
   不要拖 snail-mail 外壳本身（会套娃）。

【第 3 步 · Commit 前检查】
□ 共 9 个文件（3 SVG + 3 PDF + 2 README + 1 LICENSE）
□ 六个模板文件前带 envelope/c6/、envelope/dl/、envelope/c5/ 前缀
□ 没有出现 snail-mail/envelope/… 双层前缀
→ Commit message 填：
Restructure to envelope/{c6,dl,c5}; relicense to CC BY 4.0
→ 点 Commit changes

【第 4 步 · 删旧文件（6 个，2-3 分钟）】
回到仓库主页，逐个打开旧顶层目录 c6/、dl/、c5/
里的 6 个旧文件：
→ 右上 ··· → Delete file → Commit changes
（每删一个 commit 一次，正常现象）
删完主页只剩 envelope/ 一个文件夹 + 2 README + LICENSE。

【第 5 步 · 建 3 个 Release】
页面右侧 Releases → Draft a new release：
  · Choose a tag → 输入 tag 名 → 选 "Create new tag on publish"
  · 填 Title、粘贴下方对应描述
  · Publish release
重复三次，tag 分别为：
  c6-v1.1.0 / dl-v1.1.0 / c5-v1.0.0

────────────────────────────────────────
【Release 文案 ①】tag: c6-v1.1.0
Title: c6-v1.1.0
────────────────────────────────────────
## License change: CC BY-NC-SA 4.0 → CC BY 4.0

All templates are now licensed under CC BY 4.0 — commercial use allowed with attribution (credit 湫黎 · github.com/foxcueva, keep embedded dc:creator/dc:rights metadata).

Files downloaded under v1.0.0 remain governed by CC BY-NC-SA 4.0.

- [C6-envelope-die-line_editable.svg](https://raw.githubusercontent.com/foxcueva/snail-mail/main/envelope/c6/C6-envelope-die-line_editable.svg)
- [C6-envelope-die-line_print.pdf](https://raw.githubusercontent.com/foxcueva/snail-mail/main/envelope/c6/C6-envelope-die-line_print.pdf)

────────────────────────────────────────
【Release 文案 ②】tag: dl-v1.1.0
Title: dl-v1.1.0
────────────────────────────────────────
## License change: CC BY-NC-SA 4.0 → CC BY 4.0

All templates are now licensed under CC BY 4.0 — commercial use allowed with attribution (credit 湫黎 · github.com/foxcueva, keep embedded dc:creator/dc:rights metadata).

Files downloaded under v1.0.0 remain governed by CC BY-NC-SA 4.0.

- [DL-envelope-die-line_editable.svg](https://raw.githubusercontent.com/foxcueva/snail-mail/main/envelope/dl/DL-envelope-die-line_editable.svg)
- [DL-envelope-die-line_print.pdf](https://raw.githubusercontent.com/foxcueva/snail-mail/main/envelope/dl/DL-envelope-die-line_print.pdf)

────────────────────────────────────────
【Release 文案 ③】tag: c5-v1.0.0
Title: c5-v1.0.0
────────────────────────────────────────
## Initial release: C5 (GB/T 1416 size 7)

ISO C5 envelope, 229 × 162 mm, holds A4 half-fold (A5 flat). A3 paper, true 1:1.
54 mm closure flap (R10) · 12 mm side gussets · 100 mm calibration ruler · CC BY 4.0.

- [C5-envelope-die-line_editable.svg](https://raw.githubusercontent.com/foxcueva/snail-mail/main/envelope/c5/C5-envelope-die-line_editable.svg)
- [C5-envelope-die-line_print.pdf](https://raw.githubusercontent.com/foxcueva/snail-mail/main/envelope/c5/C5-envelope-die-line_print.pdf)

────────────────────────────────────────
【第 6 步 · About 与 Topics】
仓库右上 About 齿轮：
  Description:
Print-ready envelope & postcard die-line templates — 1:1, cut & fold, CC BY 4.0
  Topics 加：snailmail  postcard  print
（原有 envelope、template 等保留）

【第 7 步 · 喊 Sam 终检】
全部完成后回到聊天里说一声，我会拉取远端
6 个文件做 SHA-256 逐字节终检 + README 渲染检查。

预期指纹（供对照，终检以远端实算为准）：
09bb0759…a01b9a9cad77159e85122  envelope/c5/C5-envelope-die-line_editable.svg
b18bd29f…026aee0362157d        envelope/c5/C5-envelope-die-line_print.pdf
c88a8030…98f84f73e             envelope/c6/C6-envelope-die-line_editable.svg
478d0ab0…00d6d17f40            envelope/c6/C6-envelope-die-line_print.pdf
f2389d71…f6645f66              envelope/dl/DL-envelope-die-line_editable.svg
02cc20de…eb2a81410be9604ede5e  envelope/dl/DL-envelope-die-line_print.pdf
════════════════════════════════════════════════
