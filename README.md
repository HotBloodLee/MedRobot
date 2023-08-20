# 爬虫小工具

目前仅针对PubMed爬取

## 版本
### v0.1

基础UI实现

基础功能设计如下：
- 可手动输入关键词文本（一行表示一次检索，同一行的多个检索词用分号隔开，可多行输入）
- 可导入文件（拖拽/手动选择）
- 可选择检索范围（全球/国内）
- 可选择检索数量
- 可选择导出文件位置

### v0.2

基础功能实现

不足:
- 仅支持txt输入关键词
- 仅支持导出xlsx
- 仅支持国内国外两种范围
- 仅支持PubMed

问题:
- v0.2-1 exe运行多线程失败（ui没有更新）

### v0.3

修复问题v0.2-1

不足:
- 仅支持txt输入关键词
- 仅支持导出xlsx
- 仅支持国内国外两种范围
- 仅支持PubMed
- 缺少错误输入提示
- 爬取过程信息提示