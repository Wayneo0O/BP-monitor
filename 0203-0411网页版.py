import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
from io import BytesIO, StringIO

# ===================== 全局配置 =====================
# 配置中文字体（解决网页绘图中文乱码）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(page_title="血压心率监测工具", layout="wide")  # 网页宽屏显示

# ===================== 原始数据初始化 =====================
# 原始日期、收缩压、舒张压、心率数据（完全复用你的数据）
original_dates = [
    '2026-02-03', '2026-02-04', '2026-02-05', '2026-02-06', '2026-02-07',
    '2026-02-08', '2026-02-09', '2026-02-10', '2026-02-11', '2026-02-12',
    '2026-02-13', '2026-02-14', '2026-02-15', '2026-02-16', '2026-02-18',
    '2026-02-19', '2026-02-20', '2026-02-22', '2026-02-23', '2026-02-24',
    '2026-02-25', '2026-02-28', '2026-03-01', '2026-03-02', '2026-03-04',
    '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08', '2026-03-09',
    '2026-03-10', '2026-03-11', '2026-03-12', '2026-03-13', '2026-03-14',
    '2026-03-15', '2026-03-16', '2026-03-17', '2026-03-18', '2026-03-19',
    '2026-03-20', '2026-03-21', '2026-03-22', '2026-03-23', '2026-03-24',
    '2026-03-25', '2026-03-26', '2026-03-27', '2026-03-28', '2026-03-29',
    '2026-03-30', '2026-03-31', '2026-04-01', '2026-04-02', '2026-04-03',
    '2026-04-04', '2026-04-05', '2026-04-07', '2026-04-08', '2026-04-09',
    '2026-04-10', '2026-04-11'
]
original_systolic = [
    127.5, 134, 133, 126, 127.5, 128.5, 143, 133, 131.6, 155,
    136.5, 129.25, 136, 139, 145, 135, 127, 137, 134, 135,
    133, 127, 136, 136, 126, 128, 135, 120, 125, 135, 122,
    129.5, 120, 121.5, 120.5, 119, 118, 113.5, 118.5, 116,
    115, 117, 114, 119, 118, 113, 118, 120, 116, 114,
    115.5, 117, 120, 120.5, 109, 113, 114, 117, 109, 116.5,
    115, 118
]
original_diastolic = [
    86.5, 83, 87, 87, 88.5, 89.5, 90, 90, 86, 89, 89, 84,
    91, 92, 78, 99, 87, 87, 85, 89, 80, 81, 77, 79, 83,
    77, 79, 79, 77, 80, 82, 76.5, 76, 80.5, 77.5, 74,
    78.5, 75.5, 72, 68, 78, 73, 75, 75, 76, 69.5, 73,
    70, 74, 70, 72.5, 71, 76.5, 71.5, 68, 77, 73,
    75, 60, 72, 74.7, 72
]
original_heart_rate = [
    76, 95, 94.25, 83, 78.67, 84.5, 105, 94, 90.4, 104, 89, 87,
    94, 76, 77, 85, 94, 76, 83, 90, 66, 69, 76, 81, 73, 76,
    73, 86, 76, 72, 100, 83, 103, 92.5, 88.5, 82, 84.5, 89,
    82.5, 81, 83, 84, 82, 79, 90, 78.5, 78.5, 93, 74, 82,
    88, 87, 81.5, 91, 94, 82, 93, 119.5, 106, 107.5, 110.3, 102
]

# 原始数据转DataFrame（方便展示和合并）
original_df = pd.DataFrame({
    '日期': original_dates,
    '收缩压(mmHg)': original_systolic,
    '舒张压(mmHg)': original_diastolic,
    '心率(次/分)': original_heart_rate
})

# ===================== 核心绘图函数（完全复用你的逻辑） =====================
def plot_smooth_with_breaks(x_days, y_vals, date_objects, color, label):
    continuous_segments = []
    break_points = []
    start_idx = 0
    for i in range(1, len(x_days)):
        if x_days[i] - x_days[i-1] > 1:
            continuous_segments.append((start_idx, i))
            break_points.append({
                'date_start': date_objects[i-1],
                'date_end': date_objects[i],
                'y_start': y_vals[i-1],
                'y_end': y_vals[i]
            })
            start_idx = i
    continuous_segments.append((start_idx, len(x_days)))
    
    for (s_idx, e_idx) in continuous_segments:
        if e_idx - s_idx < 2:
            continue
        x_segment = x_days[s_idx:e_idx]
        y_segment = y_vals[s_idx:e_idx]
        x_smooth = np.linspace(x_segment.min(), x_segment.max(), 500)
        f_smooth = interp1d(x_segment, y_segment, kind='quadratic', fill_value='extrapolate')
        y_smooth = f_smooth(x_smooth)
        date_smooth = [date_objects[0] + timedelta(days=x) for x in x_smooth]
        plt.plot(date_smooth, y_smooth, color=color, linewidth=2, antialiased=True)
    
    for bp in break_points:
        plt.plot([bp['date_start'], bp['date_end']], [bp['y_start'], bp['y_end']],
                 color=color, linestyle='--', linewidth=1.5, alpha=0.7)
    
    marker = 'o' if '收缩压' in label else ('s' if '舒张压' in label else '^')
    plt.scatter(date_objects, y_vals, color=color, marker=marker, s=30, zorder=5, label=label)

# ===================== 网页界面构建 =====================
st.title("血压与心率变化监测工具")
st.divider()

# 1. 展示原始数据
st.subheader("📊 原始数据（2026-02-03 至 2026-04-11）")
st.dataframe(original_df, use_container_width=True)

# 2. 新增数据输入区域
st.subheader("✏️ 新增血压/心率数据")
col1, col2, col3, col4 = st.columns(4)
with col1:
    new_date = st.text_input("日期（格式：YYYY-MM-DD）", placeholder="例如：2026-04-12")
with col2:
    new_systolic = st.number_input("收缩压 (mmHg)", min_value=0.0, step=0.5, placeholder="例如：118")
with col3:
    new_diastolic = st.number_input("舒张压 (mmHg)", min_value=0.0, step=0.5, placeholder="例如：73")
with col4:
    new_heart = st.number_input("心率 (次/分)", min_value=0.0, step=0.5, placeholder="例如：98")

# 初始化会话状态（保存新增数据，避免刷新丢失）
if 'new_data_list' not in st.session_state:
    st.session_state.new_data_list = []

# 新增数据添加按钮
if st.button("➕ 添加本条数据", type="primary"):
    # 基础校验
    if not new_date:
        st.error("请输入日期（格式：YYYY-MM-DD）！")
    elif new_systolic == 0 or new_diastolic == 0 or new_heart == 0:
        st.error("收缩压/舒张压/心率不能为空（请输入大于0的数值）！")
    else:
        # 校验日期格式
        try:
            datetime.strptime(new_date, '%Y-%m-%d')
            # 添加数据到会话状态
            st.session_state.new_data_list.append({
                '日期': new_date,
                '收缩压(mmHg)': new_systolic,
                '舒张压(mmHg)': new_diastolic,
                '心率(次/分)': new_heart
            })
            st.success(f"✅ 已添加 {new_date} 的数据！")
            # 清空输入框（通过刷新组件值）
            st.experimental_rerun()
        except ValueError:
            st.error("日期格式错误！请输入 YYYY-MM-DD 格式（例如：2026-04-12）")

# 展示已添加的新增数据
if st.session_state.new_data_list:
    st.subheader("📝 已添加的新增数据")
    new_df = pd.DataFrame(st.session_state.new_data_list)
    st.dataframe(new_df, use_container_width=True)
    # 清空新增数据按钮
    if st.button("🗑️ 清空所有新增数据"):
        st.session_state.new_data_list = []
        st.experimental_rerun()

# 3. 生成图表
st.subheader("🎨 生成趋势图表")
if st.button("🚀 生成合并数据后的趋势图", type="primary"):
    # 合并原始数据和新增数据
    combined_df = pd.concat([original_df, pd.DataFrame(st.session_state.new_data_list)], ignore_index=True)
    # 按日期排序（关键：避免日期乱序导致绘图错误）
    combined_df['日期'] = pd.to_datetime(combined_df['日期'])
    combined_df = combined_df.sort_values('日期').reset_index(drop=True)
    
    # 提取合并后的数据
    dates = combined_df['日期'].dt.strftime('%Y-%m-%d').tolist()
    systolic = combined_df['收缩压(mmHg)'].tolist()
    diastolic = combined_df['舒张压(mmHg)'].tolist()
    heart_rate = combined_df['心率(次/分)'].tolist()
    
    # 日期处理（和原代码一致）
    date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
    x_days = np.array([(d - date_objects[0]).days for d in date_objects])
    
    # 绘制高清图表（和原代码一致）
    plt.figure(figsize=(28, 10), dpi=300)
    # 绘制三条曲线
    plot_smooth_with_breaks(x_days, systolic, date_objects, 'red', '收缩压 (mmHg)')
    plot_smooth_with_breaks(x_days, diastolic, date_objects, 'blue', '舒张压 (mmHg)')
    plot_smooth_with_breaks(x_days, heart_rate, date_objects, 'green', '心率 (次/分)')
    # 绘制趋势线（3次多项式）
    coeff_s = np.polyfit(x_days, systolic, 3)
    trend_s = np.poly1d(coeff_s)(x_days)
    plt.plot(date_objects, trend_s, color='red', linestyle='--', linewidth=2, alpha=0.9, label='收缩压趋势线')
    
    coeff_d = np.polyfit(x_days, diastolic, 3)
    trend_d = np.poly1d(coeff_d)(x_days)
    plt.plot(date_objects, trend_d, color='blue', linestyle='--', linewidth=2, alpha=0.9, label='舒张压趋势线')
    
    coeff_h = np.polyfit(x_days, heart_rate, 3)
    trend_h = np.poly1d(coeff_h)(x_days)
    plt.plot(date_objects, trend_h, color='green', linestyle='--', linewidth=2, alpha=0.9, label='心率趋势线')
    
    # 数据标注（和原代码一致）
    for i, (x, y) in enumerate(zip(date_objects, systolic)):
        plt.annotate(f'{y:.1f}', (x, y), xytext=(0, 8), textcoords="offset points", ha='center', fontsize=7, color='red')
    for i, (x, y) in enumerate(zip(date_objects, diastolic)):
        plt.annotate(f'{y:.1f}', (x, y), xytext=(0, -12), textcoords="offset points", ha='center', fontsize=7, color='blue')
    for i, (x, y) in enumerate(zip(date_objects, heart_rate)):
        plt.annotate(f'{y:.1f}', (x, y), xytext=(8, 0), textcoords="offset points", ha='left', fontsize=7, color='green')
    
    # 标题和标签（自动更新时间范围）
    start_date = date_objects[0].strftime('%Y年%m月%d日')
    end_date = date_objects[-1].strftime('%Y年%m月%d日')
    plt.title(f'血压与心率变化记录表（{start_date}-{end_date}）', fontsize=18, pad=20)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('数值', fontsize=14)
    plt.xticks(date_objects, [d.strftime('%Y-%m-%d') for d in date_objects], rotation=70, fontsize=8, ha='right')
    plt.legend(fontsize=13)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    # 在网页显示图表
    st.pyplot(plt)
    
    # 图表导出功能
    st.subheader("💾 导出图表/数据")
    # 导出图表为PNG
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    st.download_button(
        label="📥 下载高清图表（PNG）",
        data=buf,
        file_name=f'血压心率趋势图_{start_date.replace("年","").replace("月","").replace("日","")}-{end_date.replace("年","").replace("月","").replace("日","")}.png',
        mime='image/png'
    )
    # 导出合并后的数据为CSV
    csv_buf = StringIO()
    combined_df['日期'] = combined_df['日期'].dt.strftime('%Y-%m-%d')
    combined_df.to_csv(csv_buf, index=False, encoding='utf-8-sig')
    csv_buf.seek(0)
    st.download_button(
        label="📥 下载合并后的数据（CSV）",
        data=csv_buf,
        file_name=f'血压心率数据_{start_date.replace("年","").replace("月","").replace("日","")}-{end_date.replace("年","").replace("月","").replace("日","")}.csv',
        mime='text/csv'
    )
