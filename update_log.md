# 更新日志

## v0.2.1 数据质量修复

- 修复Excel来源/备注字段别名遗漏；同步Excel、CSV及自动生成附录。
- 逐条核验33条候选来源：25条部分范围验证，8条读取失败待人工核实；保留候选URL及证据范围台账。
- 修正文档Python/Stata字段名及14字段说明。
- 新增离线数据一致性检查和PR/push CI；保留v0.1数据文件路径兼容下载。

## v0.2

- 将四张示范政策卡片扩展为完整详情页；
- 新增 `templates/policy_card_template.qmd`；
- 更新 `README.md`、`methods.qmd`、`cards.qmd` 和 `references.qmd`；
- 新增 `CONTRIBUTING.md` 和 GitHub issue 模板；
- 保留 `v0.1` 的 Excel / CSV 主表。

## v0.1

- 建立政策冲击主表；
- 初步整理 33 条中国近年重要政策冲击；
- 建立 Quarto + GitHub Pages 基础网站结构。
