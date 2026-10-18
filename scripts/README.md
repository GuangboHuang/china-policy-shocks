# 数据维护

以 `data/policy_shock_library_v0_1.xlsx` 为维护源。官方链接需核实网页内容及适用范围，并同步更新 `data/official_source_audit.csv`；多个链接以英文分号分隔。

运行 `python scripts/build_appendix.py` 生成CSV及附录，再运行 `python scripts/check_data.py` 执行离线一致性检查。来源范围与待补证据见 `data/SOURCE_AUDIT.md`。GitHub Actions在push和PR时执行同样检查。
