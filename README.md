# DataViz 数据可视化工具

一个基于 Streamlit 构建的轻量级数据可视化 Web 应用，支持上传 Excel/CSV 文件，快速生成柱状图、折线图、饼图、环形图、雷达图等多种图表，并可导出为图片。

## ✨ 功能特性

- 📁 **数据上传**：支持 `.xlsx`、`.xls`、`.csv` 格式
- 📊 **多种图表类型**：柱状图、折线图、饼图、环形图、雷达图
- 🎨 **样式自定义**：图表标题、颜色主题、图例、网格线开关
- 💾 **一键导出**：图表可导出为 PNG / JPG / SVG 图片
- 🖥️ **交互式界面**：实时预览数据，动态调整图表

## 🚀 快速开始

### 1. 环境要求
- Python 3.8 或更高版本
- 推荐使用虚拟环境（venv 或 conda）

### 2. 安装依赖
克隆或下载本项目后，在终端执行：

```bash
pip install -r requirements.txt
或者手动安装：
pip install streamlit pandas plotly openpyxl kaleido

###3. 运行应用
bash
streamlit run 1.py
或使用 Python 模块方式（推荐）：

bash
python -m streamlit run 1.py
浏览器将自动打开 http://localhost:8501，即可使用工具。

📊 使用说明
上传数据：点击左侧“浏览文件”或拖拽文件到指定区域，支持 Excel 和 CSV 格式。

选择 X/Y 轴：从下拉菜单中选择用于类别轴和数值轴的列。

选择图表类型：在侧边栏选择柱状图、折线图等。

调整样式：设置标题、颜色主题、图例、网格线等。

生成图表：点击“生成图表”按钮，图表将显示在主区域。

❗ 常见问题
Q: 导出图片时提示错误？
A: 请确保已安装 kaleido 库：pip install kaleido。若仍失败，可尝试重启应用。

Q: 图表显示不完整或数据过多？
A: 饼图/环形图建议类别不超过 20 个，否则可先对数据进行聚合或筛选。

Q: 雷达图如何解读？
A: 雷达图将 X 轴作为角度，Y 轴作为半径，适用于展示单个系列的多个指标对比。

📝 依赖项
项目依赖以下 Python 库（详见 requirements.txt）：

streamlit

pandas

plotly

openpyxl

kaleido

📄 开源协议
本项目遵循 MIT 协议，欢迎自由使用和修改。

👤 作者
如果您有任何问题或建议，欢迎提交 Issue 或 Pull Request。