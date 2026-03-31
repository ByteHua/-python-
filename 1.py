import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="DataViz 数据可视化工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 常量定义
MAX_ROWS_FOR_DETAIL = 5000      # 超过此行数将启用大数据处理模式
MAX_PIE_CATEGORIES = 50          # 饼图/环形图最大类别数
MAX_RADAR_POINTS = 50            # 雷达图最大点数

st.markdown("""
    <style>
        .main-header {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #165DFF 0%, #FF7D00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            color: #4E5969;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# 缓存数据加载
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df

# 大数据处理函数
def handle_large_data(df, x_col, y_col, chart_type, sample_method, agg_method):
    """
    根据用户选择对大数据进行采样或聚合
    返回处理后的 DataFrame（最多 MAX_ROWS_FOR_DETAIL 行）
    """
    original_len = len(df)
    if original_len <= MAX_ROWS_FOR_DETAIL:
        return df, original_len
    
    st.info(f"⚠️ 数据量较大（{original_len} 行），已启用大数据处理模式。")
    
    if sample_method == "随机采样":
        frac = min(1.0, MAX_ROWS_FOR_DETAIL / original_len)
        df_sampled = df.sample(frac=frac, random_state=42)
        st.success(f"随机采样至 {len(df_sampled)} 行")
        return df_sampled, len(df_sampled)
    
    elif sample_method == "分组聚合":
        # 按 x_col 分组，对 y_col 进行聚合（求和/平均）
        if agg_method == "求和":
            df_agg = df.groupby(x_col)[y_col].sum().reset_index()
        else:  # 平均
            df_agg = df.groupby(x_col)[y_col].mean().reset_index()
        st.success(f"分组聚合后共 {len(df_agg)} 个类别")
        return df_agg, len(df_agg)
    
    else:
        # 默认截断
        df_trunc = df.head(MAX_ROWS_FOR_DETAIL)
        st.warning(f"截断至前 {MAX_ROWS_FOR_DETAIL} 行")
        return df_trunc, MAX_ROWS_FOR_DETAIL

# 颜色主题
COLOR_THEMES = {
    "蓝色": px.colors.sequential.Blues[2:],
    "绿色": px.colors.sequential.Greens[2:],
    "紫色": px.colors.sequential.Purples[2:],
    "红色": px.colors.sequential.Reds[2:],
    "橙色": px.colors.sequential.Oranges[2:],
    "多彩": px.colors.qualitative.Set3
}

# 侧边栏
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/data-configuration.png", width=60)
    st.title("DataViz 控制台")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 上传数据文件", type=["xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        try:
            df = load_data(uploaded_file)
            st.session_state.df = df
            st.success(f"✅ 成功加载 {uploaded_file.name}")
            st.info(f"原始数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
        except Exception as e:
            st.error(f"文件读取失败: {e}")
            st.session_state.df = None
    else:
        st.info("👈 请先上传 Excel 或 CSV 文件")
        st.session_state.df = None
    
    st.markdown("---")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = df.columns.tolist()
        
        chart_type = st.selectbox("📊 图表类型", ["柱状图", "折线图", "饼图", "环形图", "雷达图"])
        x_axis = st.selectbox("🏷️ X轴 / 类别", options=all_cols, index=0 if all_cols else None)
        
        if numeric_cols:
            y_axis = st.selectbox("📈 Y轴 / 数值", options=numeric_cols, index=0 if numeric_cols else None)
        else:
            st.warning("⚠️ 未检测到数值列")
            y_axis = None
        
        # 大数据处理选项（仅在数据量超过阈值时显示）
        if len(df) > MAX_ROWS_FOR_DETAIL:
            st.markdown("---")
            st.subheader("⚙️ 大数据处理")
            sample_method = st.radio(
                "数据量过大时处理方式",
                ["随机采样", "分组聚合", "截断前N行"],
                index=0,
                help="随机采样保留代表性数据；分组聚合按X轴类别合并数值（求和/平均）；截断仅取前N行。"
            )
            if sample_method == "分组聚合":
                agg_method = st.radio("聚合方式", ["求和", "平均"], index=0)
            else:
                agg_method = None
        else:
            sample_method = "无处理"
            agg_method = None
        
        st.markdown("---")
        st.subheader("🎨 样式设置")
        chart_title = st.text_input("图表标题", value="数据可视化图表")
        theme = st.selectbox("颜色主题", list(COLOR_THEMES.keys()), index=0)
        show_legend = st.checkbox("显示图例", value=True)
        show_grid = st.checkbox("显示网格线", value=True)
        
        st.markdown("---")
        st.subheader("💾 导出设置")
        export_format = st.selectbox("导出格式", ["PNG", "JPG", "SVG"], index=0)
        export_width = st.number_input("宽度 (px)", min_value=400, max_value=3000, value=800, step=50)
        export_height = st.number_input("高度 (px)", min_value=300, max_value=2000, value=600, step=50)
        bg_color = st.radio("背景色", ["白色", "透明"], index=0, horizontal=True)
        
        generate_btn = st.button("✨ 生成图表", type="primary", use_container_width=True)

# 主区域
st.markdown('<p class="main-header">数据可视化工具</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">上传您的数据文件，快速生成专业图表，支持大数据处理</p>', unsafe_allow_html=True)

if st.session_state.df is not None:
    df = st.session_state.df
    with st.expander("📋 原始数据预览", expanded=True):
        st.dataframe(df.head(100), use_container_width=True, height=300)
        st.caption(f"显示前100行，共 {len(df)} 行")
    
    col1, col2 = st.columns([2, 1])
    
    if generate_btn and y_axis is not None and x_axis is not None:
        try:
            # 初始数据清理
            df_clean = df[[x_axis, y_axis]].dropna()
            if len(df_clean) == 0:
                st.error("所选列中没有有效数据")
                st.stop()
            
            # 大数据处理
            if len(df_clean) > MAX_ROWS_FOR_DETAIL and sample_method != "无处理":
                df_clean, processed_rows = handle_large_data(
                    df_clean, x_axis, y_axis, chart_type,
                    sample_method, agg_method if sample_method == "分组聚合" else None
                )
            else:
                processed_rows = len(df_clean)
            
            # 针对饼图/环形图/雷达图的类别数量限制
            if chart_type in ["饼图", "环形图"] and len(df_clean) > MAX_PIE_CATEGORIES:
                st.warning(f"饼图/环形图最多显示 {MAX_PIE_CATEGORIES} 个类别，将仅显示前 {MAX_PIE_CATEGORIES} 个")
                df_clean = df_clean.head(MAX_PIE_CATEGORIES)
            
            if chart_type == "雷达图" and len(df_clean) > MAX_RADAR_POINTS:
                st.warning(f"雷达图最多显示 {MAX_RADAR_POINTS} 个点，将仅显示前 {MAX_RADAR_POINTS} 个")
                df_clean = df_clean.head(MAX_RADAR_POINTS)
            
            # 颜色
            colors = COLOR_THEMES[theme]
            color_seq = colors if len(colors) >= len(df_clean) else colors * (len(df_clean) // len(colors) + 1)
            
            # 生成图表
            if chart_type == "柱状图":
                fig = px.bar(df_clean, x=x_axis, y=y_axis, title=chart_title,
                             color_discrete_sequence=[color_seq[0]],
                             labels={x_axis: x_axis, y_axis: y_axis})
            elif chart_type == "折线图":
                fig = px.line(df_clean, x=x_axis, y=y_axis, title=chart_title,
                              color_discrete_sequence=[color_seq[0]],
                              labels={x_axis: x_axis, y_axis: y_axis})
            elif chart_type == "饼图":
                fig = px.pie(df_clean, names=x_axis, values=y_axis, title=chart_title,
                             color_discrete_sequence=color_seq)
            elif chart_type == "环形图":
                fig = px.pie(df_clean, names=x_axis, values=y_axis, title=chart_title,
                             hole=0.6, color_discrete_sequence=color_seq)
            elif chart_type == "雷达图":
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=df_clean[y_axis].values,
                    theta=df_clean[x_axis].astype(str).values,
                    fill='toself',
                    name=y_axis,
                    line_color=color_seq[0],
                    fillcolor=f'rgba({",".join(map(str, px.colors.hex_to_rgb(color_seq[0])))},0.3)'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, gridcolor='lightgray' if show_grid else 'white'),
                        angularaxis=dict(gridcolor='lightgray' if show_grid else 'white')
                    )
                )
            
            # 通用布局（雷达图除外）
            if chart_type not in ["雷达图"]:
                fig.update_layout(
                    title=chart_title,
                    xaxis_title=x_axis,
                    yaxis_title=y_axis,
                    showlegend=show_legend,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Noto Sans CJK SC, Microsoft YaHei, SimHei, Arial", size=12)
                )
                if not show_grid:
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=False)
                else:
                    fig.update_xaxes(showgrid=True, gridcolor='#E5E6EB')
                    fig.update_yaxes(showgrid=True, gridcolor='#E5E6EB')
            else:
                fig.update_layout(
                    title=chart_title,
                    showlegend=show_legend,
                    font=dict(family="Noto Sans CJK SC, Microsoft YaHei, SimHei, Arial", size=12)
                )
            
            st.session_state.fig = fig
            
            with col2:
                st.markdown("### 📈 图表展示")
                st.plotly_chart(fig, use_container_width=True, key="live_chart")
            
            st.success(f"✅ 图表生成成功！使用数据行数: {processed_rows}", icon="🎉")
            
        except Exception as e:
            st.error(f"图表生成失败: {e}")
            st.session_state.fig = None
    else:
        if st.session_state.get('fig') is not None:
            with col2:
                st.markdown("### 📈 图表展示")
                st.plotly_chart(st.session_state.fig, use_container_width=True, key="existing_chart")
        else:
            with col2:
                st.info("👈 请先在左侧选择X轴和Y轴，然后点击「生成图表」")
    
    # 导出功能
    if st.session_state.get('fig') is not None:
        st.markdown("---")
        col_export1, col_export2, _ = st.columns([1, 1, 2])
        with col_export1:
            export_btn = st.button("💾 导出图表", type="secondary", use_container_width=True)
        
        if export_btn:
            try:
                import plotly.io as pio
                pio.kaleido.scope.default_format = "png"
                fig = st.session_state.fig
                bg_rgba = "white" if bg_color == "白色" else "rgba(0,0,0,0)"
                fig.update_layout(paper_bgcolor=bg_rgba, plot_bgcolor=bg_rgba)
                
                fmt = export_format.lower()
                if fmt == "svg":
                    img_bytes = fig.to_image(format="svg", width=export_width, height=export_height)
                    mime = "image/svg+xml"
                    ext = "svg"
                elif fmt == "jpg":
                    img_bytes = fig.to_image(format="jpg", width=export_width, height=export_height, scale=2)
                    mime = "image/jpeg"
                    ext = "jpg"
                else:
                    img_bytes = fig.to_image(format="png", width=export_width, height=export_height, scale=2)
                    mime = "image/png"
                    ext = "png"
                
                st.download_button(
                    label="📥 点击下载图片",
                    data=img_bytes,
                    file_name=f"chart_export.{ext}",
                    mime=mime,
                    key="download_btn"
                )
                st.success("图片已准备就绪，点击下载即可保存")
            except Exception as e:
                st.error(f"导出失败，请确保已安装 kaleido 和 Chromium。\n错误信息: {e}")
                st.info("💡 提示：在终端运行 `pip install kaleido`，并在部署环境中安装 `chromium` 和 `fonts-noto-cjk` 可解决。")
else:
    st.info("📌 请从左侧边栏上传数据文件")

# 帮助说明
with st.expander("ℹ️ 使用说明"):
    st.markdown("""
    - **大数据支持**：当数据超过 5000 行时，自动启用大数据处理模式，提供随机采样、分组聚合（求和/平均）、截断等选项。
    - **图表类型**：柱状图/折线图适合趋势对比；饼图/环形图适合占比（建议不超过50个类别）；雷达图展示多维度数据。
    - **导出图片**：需要安装 `kaleido` 库，并在部署环境中安装 `chromium` 和 `fonts-noto-cjk` 以支持中文。
    - **性能提示**：分组聚合可大幅减少数据量，适合按类别汇总的场景。
    """)

st.markdown("---")
st.markdown(
    "<footer style='text-align: center; color: #86909C; padding: 1rem;'>© 2025 DataViz | 数据可视化工具 | 支持大数据处理 · 多种图表 · 一键导出</footer>",
    unsafe_allow_html=True
)