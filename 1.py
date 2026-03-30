import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from PIL import Image
import base64

# 页面配置
st.set_page_config(
    page_title="DataViz - 数据可视化工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS美化（可选）
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #165DFF 0%, #FF7D00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            color: #4E5969;
            margin-bottom: 2rem;
        }
        .chart-container {
            background-color: white;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-top: 1rem;
        }
        .preview-container {
            background-color: #F5F7FA;
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: #86909C;
            margin-top: 3rem;
            border-top: 1px solid #E5E6EB;
        }
    </style>
""", unsafe_allow_html=True)

# 初始化session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'fig' not in st.session_state:
    st.session_state.fig = None

# 颜色主题预设
COLOR_THEMES = {
    "蓝色": px.colors.sequential.Blues[2:],
    "绿色": px.colors.sequential.Greens[2:],
    "紫色": px.colors.sequential.Purples[2:],
    "红色": px.colors.sequential.Reds[2:],
    "橙色": px.colors.sequential.Oranges[2:],
    "多彩": px.colors.qualitative.Set3
}

# 侧边栏控制区
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/data-configuration.png", width=60)
    st.title("DataViz 控制台")
    st.markdown("---")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "📂 上传数据文件",
        type=["xlsx", "xls", "csv"],
        help="支持 Excel (.xlsx, .xls) 和 CSV 文件"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            st.session_state.df = df
            st.success(f"✅ 成功加载 {uploaded_file.name}", icon="✅")
            st.info(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
        except Exception as e:
            st.error(f"文件读取失败: {e}")
            st.session_state.df = None
    else:
        st.info("👈 请先上传 Excel 或 CSV 文件")
    
    st.markdown("---")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # 图表类型选择
        chart_type = st.selectbox(
            "📊 图表类型",
            ["柱状图", "折线图", "饼图", "环形图", "雷达图"],
            index=0,
            help="选择适合您数据的图表类型"
        )
        
        # 列选择器
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = df.columns.tolist()
        
        # X轴（类别）
        x_axis = st.selectbox(
            "🏷️ X轴 / 类别",
            options=all_cols,
            index=0 if all_cols else None,
            help="通常选择文本或分类列"
        )
        
        # Y轴（数值）
        if numeric_cols:
            y_axis = st.selectbox(
                "📈 Y轴 / 数值",
                options=numeric_cols,
                index=0 if numeric_cols else None,
                help="选择数值列"
            )
        else:
            st.warning("⚠️ 未检测到数值列，请检查数据")
            y_axis = None
        
        st.markdown("---")
        
        # 图表样式选项
        st.subheader("🎨 样式设置")
        chart_title = st.text_input("图表标题", value="数据可视化图表")
        theme = st.selectbox("颜色主题", list(COLOR_THEMES.keys()), index=0)
        show_legend = st.checkbox("显示图例", value=True)
        show_grid = st.checkbox("显示网格线", value=True)
        
        st.markdown("---")
        
        # 导出设置
        st.subheader("💾 导出设置")
        export_format = st.selectbox("导出格式", ["PNG", "JPG", "SVG"], index=0)
        export_width = st.number_input("宽度 (px)", min_value=400, max_value=3000, value=800, step=50)
        export_height = st.number_input("高度 (px)", min_value=300, max_value=2000, value=600, step=50)
        bg_color = st.radio("背景色", ["白色", "透明"], index=0, horizontal=True)
        
        # 生成图表按钮
        generate_btn = st.button("✨ 生成图表", type="primary", use_container_width=True)

# 主区域
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<p class="main-header">数据可视化工具</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">上传您的数据文件，快速生成专业图表</p>', unsafe_allow_html=True)

# 数据预览区域
if st.session_state.df is not None:
    df = st.session_state.df
    with st.expander("📋 数据预览", expanded=True):
        st.dataframe(df.head(100), use_container_width=True, height=300)
        st.caption(f"显示前100行数据，共 {len(df)} 行")
else:
    st.info("📌 请从左侧边栏上传数据文件")
    st.stop()

# 图表生成逻辑
if generate_btn and y_axis is not None and x_axis is not None:
    try:
        # 准备数据
        df_clean = df[[x_axis, y_axis]].dropna()
        
        if len(df_clean) == 0:
            st.error("所选列中没有有效数据，请检查缺失值")
            st.stop()
        
        # 限制饼图/环形图的类别数量（避免过多）
        if chart_type in ["饼图", "环形图"] and len(df_clean) > 50:
            st.warning(f"数据类别过多 ({len(df_clean)})，饼图将只显示前50个类别")
            df_clean = df_clean.head(50)
        
        # 颜色序列
        colors = COLOR_THEMES[theme]
        color_discrete_sequence = colors if len(colors) >= len(df_clean) else colors * (len(df_clean) // len(colors) + 1)
        
        # 根据类型创建图表
        if chart_type == "柱状图":
            fig = px.bar(
                df_clean, x=x_axis, y=y_axis,
                title=chart_title,
                color_discrete_sequence=[color_discrete_sequence[0]],
                labels={x_axis: x_axis, y_axis: y_axis}
            )
        
        elif chart_type == "折线图":
            fig = px.line(
                df_clean, x=x_axis, y=y_axis,
                title=chart_title,
                color_discrete_sequence=[color_discrete_sequence[0]],
                labels={x_axis: x_axis, y_axis: y_axis}
            )
        
        elif chart_type == "饼图":
            fig = px.pie(
                df_clean, names=x_axis, values=y_axis,
                title=chart_title,
                color_discrete_sequence=color_discrete_sequence
            )
        
        elif chart_type == "环形图":
            fig = px.pie(
                df_clean, names=x_axis, values=y_axis,
                title=chart_title,
                hole=0.6,
                color_discrete_sequence=color_discrete_sequence
            )
        
        elif chart_type == "雷达图":
            # 雷达图需要多个指标，但为了单一系列的可视化，我们使用极坐标展示
            # 将X轴作为角度，Y轴作为半径
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=df_clean[y_axis].values,
                theta=df_clean[x_axis].astype(str).values,
                fill='toself',
                name=y_axis,
                line_color=color_discrete_sequence[0],
                fillcolor=f'rgba({",".join(map(str, px.colors.hex_to_rgb(color_discrete_sequence[0])))},0.3)'
            ))
            fig.update_layout(
                title=chart_title,
                polar=dict(
                    radialaxis=dict(visible=True, gridcolor='lightgray' if show_grid else 'white'),
                    angularaxis=dict(gridcolor='lightgray' if show_grid else 'white')
                ),
                showlegend=show_legend
            )
        
        # 通用样式更新
        if chart_type not in ["雷达图"]:
            fig.update_layout(
                title=chart_title,
                xaxis_title=x_axis,
                yaxis_title=y_axis,
                showlegend=show_legend,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#1D2129")
            )
            
            # 网格线控制
            if not show_grid:
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=False)
            else:
                fig.update_xaxes(showgrid=True, gridcolor='#E5E6EB')
                fig.update_yaxes(showgrid=True, gridcolor='#E5E6EB')
        
        # 保存图表到session
        st.session_state.fig = fig
        
        # 显示图表
        with col2:
            st.markdown("### 📈 图表展示")
            st.plotly_chart(fig, use_container_width=True, key="live_chart")
        
        st.success("✅ 图表生成成功！", icon="🎉")
        
    except Exception as e:
        st.error(f"图表生成失败: {e}")
        st.session_state.fig = None

else:
    if st.session_state.fig is not None:
        with col2:
            st.markdown("### 📈 图表展示")
            st.plotly_chart(st.session_state.fig, use_container_width=True, key="existing_chart")
    else:
        with col2:
            st.info("👈 请先在左侧选择X轴和Y轴，然后点击「生成图表」")

# 导出功能（使用独立的按钮）
if st.session_state.fig is not None:
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns([1, 1, 2])
    with col_export1:
        export_btn = st.button("💾 导出图表", type="secondary", use_container_width=True)
    
    if export_btn:
        try:
            # 检查kaleido是否可用
            import plotly.io as pio
            pio.kaleido.scope.default_format = "png"
            
            # 设置背景
            bg_rgba = "white" if bg_color == "白色" else "rgba(0,0,0,0)"
            fig = st.session_state.fig
            fig.update_layout(
                paper_bgcolor=bg_rgba,
                plot_bgcolor=bg_rgba
            )
            
            # 导出格式
            fmt = export_format.lower()
            if fmt == "svg":
                img_bytes = fig.to_image(format="svg", width=export_width, height=export_height)
                mime = "image/svg+xml"
                ext = "svg"
            elif fmt == "jpg":
                img_bytes = fig.to_image(format="jpg", width=export_width, height=export_height, scale=2)
                mime = "image/jpeg"
                ext = "jpg"
            else:  # png
                img_bytes = fig.to_image(format="png", width=export_width, height=export_height, scale=2)
                mime = "image/png"
                ext = "png"
            
            # 提供下载按钮
            st.download_button(
                label="📥 点击下载图片",
                data=img_bytes,
                file_name=f"chart_export.{ext}",
                mime=mime,
                key="download_btn"
            )
            st.success("图片准备就绪，点击下载即可保存")
            
        except Exception as e:
            st.error(f"导出失败，请确保已安装 kaleido 库。\n错误信息: {e}")
            st.info("💡 提示: 在终端运行 `pip install kaleido` 即可支持导出功能")

# 辅助信息区域
with st.expander("ℹ️ 使用说明"):
    st.markdown("""
    - **数据要求**: 第一行为列名，至少包含一列数值数据用于Y轴
    - **图表类型**: 
        - 柱状图/折线图: 适合展示趋势和对比
        - 饼图/环形图: 适合展示占比，建议类别不超过10个
        - 雷达图: 展示多维度数据，此处将X轴作为角度，Y轴作为半径
    - **导出图片**: 需要安装 `kaleido` 库 (`pip install kaleido`)
    - **颜色主题**: 可在侧边栏选择不同配色方案
    - **网格线/图例**: 根据需求开关
    """)

# 页脚
st.markdown("---")
st.markdown(
    "<footer>© 2025 DataViz | 数据可视化工具 | 支持 Excel/CSV · 多种图表 · 一键导出</footer>",
    unsafe_allow_html=True
)