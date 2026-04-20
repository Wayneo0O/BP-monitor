import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
from io import BytesIO, StringIO

# ===================== 全局配置 =====================
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(page_title="Blood Pressure Monitor", layout="wide")

# ===================== 原始数据初始化 =====================
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

# 原始数据转DataFrame
original_df = pd.DataFrame({
    'Date': original_dates,
    'Systolic (mmHg)': original_systolic,
    'Diastolic (mmHg)': original_diastolic,
    'Heart Rate (bpm)': original_heart_rate
})

# ===================== 核心绘图函数 =====================
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

    marker = 'o' if 'Systolic' in label else ('s' if 'Diastolic' in label else '^')
    plt.scatter(date_objects, y_vals, color=color, marker=marker, s=30, zorder=5, label=label)

# ===================== 网页界面构建 =====================
st.title("血压与心率变化监测工具")
st.divider()

# 初始化会话状态
if 'new_data_list' not in st.session_state:
    st.session_state.new_data_list = []

# 1. 数据导入/导出功能
st.subheader("💾 数据持久化")
col_import, col_export = st.columns(2)

with col_import:
    uploaded_file = st.file_uploader("上传之前保存的新增数据（CSV格式）", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if not df.empty:
                # 验证数据格式
                required_columns = ['Date', 'Systolic (mmHg)', 'Diastolic (mmHg)', 'Heart Rate (bpm)']
                if all(col in df.columns for col in required_columns):
                    # 转换数据类型
                    df['Systolic (mmHg)'] = df['Systolic (mmHg)'].astype(float)
                    df['Diastolic (mmHg)'] = df['Diastolic (mmHg)'].astype(float)
                    df['Heart Rate (bpm)'] = df['Heart Rate (bpm)'].astype(float)
                    # 合并数据
                    new_data = df.to_dict('records')
                    st.session_state.new_data_list.extend(new_data)
                    st.success(f"✅ 成功导入 {len(new_data)} 条数据！")
                    # 重新加载页面以显示导入的数据
                    st.experimental_rerun()
                else:
                    st.error("❌ 文件格式错误，请上传正确的CSV文件")
            else:
                st.error("❌ 上传的文件为空")
        except Exception as e:
            st.error(f"❌ 导入失败：{str(e)}")

with col_export:
    if st.session_state.new_data_list:
        export_df = pd.DataFrame(st.session_state.new_data_list)
        csv_data = export_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载新增数据（CSV格式）",
            data=csv_data,
            file_name=f'新增血压数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )
    else:
        st.info("暂无数据可导出")

# 2. 展示原始数据
st.subheader("原始数据（2026-02-03 至 2026-04-11）")
st.dataframe(original_df, width='stretch')

# 3. 新增数据输入区域
st.subheader("新增血压/心率数据")
col1, col2, col3, col4 = st.columns(4)
with col1:
    new_date = st.text_input("日期（YYYY-MM-DD）", placeholder="例如：2026-04-12")
with col2:
    new_systolic = st.number_input("收缩压 (mmHg)", min_value=0.0, step=0.5, value=0.0)
with col3:
    new_diastolic = st.number_input("舒张压 (mmHg)", min_value=0.0, step=0.5, value=0.0)
with col4:
    new_heart = st.number_input("心率 (次/分)", min_value=0.0, step=0.5, value=0.0)

# 新增数据添加按钮
if st.button("添加本条数据", type="primary"):
    if not new_date:
        st.error("请输入日期（格式：YYYY-MM-DD）！")
    elif new_systolic == 0 or new_diastolic == 0 or new_heart == 0:
        st.error("收缩压/舒张压/心率不能为空（请输入大于0的数值）！")
    else:
        try:
            datetime.strptime(new_date, '%Y-%m-%d')
            st.session_state.new_data_list.append({
                'Date': new_date,
                'Systolic (mmHg)': new_systolic,
                'Diastolic (mmHg)': new_diastolic,
                'Heart Rate (bpm)': new_heart
            })
            st.success(f"✅ 已添加 {new_date} 的数据！")
            st.rerun()
        except ValueError:
            st.error("日期格式错误！请输入 YYYY-MM-DD 格式")

# 4. 展示已添加的新增数据（可编辑/删除）
if st.session_state.new_data_list:
    st.subheader("已添加的新增数据（可直接删除单条）")
    st.info("💡 使用下方的表格可以直接删除单条数据，或清空所有新增数据")
    
    # 使用 data_editor 实现内联编辑和删除
    edited_df = st.data_editor(
        pd.DataFrame(st.session_state.new_data_list),
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.TextColumn("日期", width="medium"),
            "Systolic (mmHg)": st.column_config.NumberColumn("收缩压 (mmHg)", width="small"),
            "Diastolic (mmHg)": st.column_config.NumberColumn("舒张压 (mmHg)", width="small"),
            "Heart Rate (bpm)": st.column_config.NumberColumn("心率 (次/分)", width="small"),
        }
    )
    
    # 自动保存：将编辑后的数据更新到 session_state
    # 只有当用户实际编辑了数据时才更新
    if len(edited_df) > 0:
        st.session_state.new_data_list = edited_df.to_dict('records')
    
    col_del, col_clear = st.columns(2)
    with col_del:
        pass
    with col_clear:
        if st.button("清空所有新增数据", type="secondary"):
            st.session_state.new_data_list = []
            st.rerun()
    
    # 显示当前共有多少条数据
    st.success(f"当前共有 {len(st.session_state.new_data_list)} 条新增数据")
else:
    st.info("暂无新增数据，请在上方添加")

# 5. 生成图表
st.subheader("📊 生成趋势图表")
st.info("💡 无论通过手动添加还是导入数据，点击下方按钮即可生成包含所有数据的趋势图")
if st.button("🚀 生成合并数据后的趋势图", type="primary"):
    # 合并原始数据和新增数据
    combined_df = pd.concat([original_df, pd.DataFrame(st.session_state.new_data_list)], ignore_index=True)
    # 按日期分组，计算每天的平均值
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    combined_df = combined_df.groupby('Date').mean().reset_index()
    # 按日期排序
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)

    # 提取合并后的数据
    dates = combined_df['Date'].dt.strftime('%Y-%m-%d').tolist()
    systolic = combined_df['Systolic (mmHg)'].tolist()
    diastolic = combined_df['Diastolic (mmHg)'].tolist()
    heart_rate = combined_df['Heart Rate (bpm)'].tolist()

    # 日期处理
    date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
    x_days = np.array([(d - date_objects[0]).days for d in date_objects])

    plt.figure(figsize=(28, 10), dpi=300)
    plot_smooth_with_breaks(x_days, systolic, date_objects, 'red', 'Systolic (mmHg)')
    plot_smooth_with_breaks(x_days, diastolic, date_objects, 'blue', 'Diastolic (mmHg)')
    plot_smooth_with_breaks(x_days, heart_rate, date_objects, 'green', 'Heart Rate (bpm)')

    coeff_s = np.polyfit(x_days, systolic, 3)
    trend_s = np.poly1d(coeff_s)(x_days)
    plt.plot(date_objects, trend_s, color='red', linestyle='--', linewidth=2, alpha=0.9, label='Systolic Trend')

    coeff_d = np.polyfit(x_days, diastolic, 3)
    trend_d = np.poly1d(coeff_d)(x_days)
    plt.plot(date_objects, trend_d, color='blue', linestyle='--', linewidth=2, alpha=0.9, label='Diastolic Trend')

    coeff_h = np.polyfit(x_days, heart_rate, 3)
    trend_h = np.poly1d(coeff_h)(x_days)
    plt.plot(date_objects, trend_h, color='green', linestyle='--', linewidth=2, alpha=0.9, label='Heart Rate Trend')

    for i, (x, y) in enumerate(zip(date_objects, systolic)):
        plt.annotate(f'{y:.1f}', (x, y), xytext=(0, 8), textcoords="offset points", ha='center', fontsize=7, color='red')
    for i, (x, y) in enumerate(zip(date_objects, diastolic)):
        plt.annotate(f'{y:.1f}', (x, y), xytext=(0, -12), textcoords="offset points", ha='center', fontsize=7, color='blue')
    for i, (x, y) in enumerate(zip(date_objects, heart_rate)):
        plt.annotate(f'{y:.1f}', (x, y), xytext=(8, 0), textcoords="offset points", ha='left', fontsize=7, color='green')

    start_date = date_objects[0].strftime('%Y-%m-%d')
    end_date = date_objects[-1].strftime('%Y-%m-%d')
    plt.title(f'Blood Pressure & Heart Rate ({start_date} to {end_date})', fontsize=18, pad=20)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Value', fontsize=14)
    plt.xticks(date_objects, [d.strftime('%Y-%m-%d') for d in date_objects], rotation=70, fontsize=8, ha='right')
    plt.legend(fontsize=13)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    st.pyplot(plt)

    st.subheader("💾 导出图表/数据")
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    st.download_button(
        label="📥 下载高清图表（PNG）",
        data=buf,
        file_name=f'bp_hr_chart_{start_date}-{end_date}.png',
        mime='image/png'
    )

    csv_data = combined_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载合并后的数据（CSV）",
        data=csv_data,
        file_name=f'bp_hr_data_{start_date}-{end_date}.csv',
        mime='text/csv'
    )
