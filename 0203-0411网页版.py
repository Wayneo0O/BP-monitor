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
st.title("Blood Pressure & Heart Rate Monitor")
st.divider()

# 1. 展示原始数据
st.subheader("Original Data (2026-02-03 to 2026-04-11)")
st.dataframe(original_df, width='stretch')

# 2. 新增数据输入区域
st.subheader("Add New Data")
col1, col2, col3, col4 = st.columns(4)
with col1:
    new_date = st.text_input("Date (YYYY-MM-DD)", placeholder="e.g., 2026-04-12")
with col2:
    new_systolic = st.number_input("Systolic (mmHg)", min_value=0.0, step=0.5, value=0.0)
with col3:
    new_diastolic = st.number_input("Diastolic (mmHg)", min_value=0.0, step=0.5, value=0.0)
with col4:
    new_heart = st.number_input("Heart Rate (bpm)", min_value=0.0, step=0.5, value=0.0)

# 初始化会话状态
if 'new_data_list' not in st.session_state:
    st.session_state.new_data_list = []

# 新增数据添加按钮
if st.button("Add This Data", type="primary"):
    if not new_date:
        st.error("Please enter a date (YYYY-MM-DD)!")
    elif new_systolic == 0 or new_diastolic == 0 or new_heart == 0:
        st.error("All fields must be greater than 0!")
    else:
        try:
            datetime.strptime(new_date, '%Y-%m-%d')
            st.session_state.new_data_list.append({
                'Date': new_date,
                'Systolic (mmHg)': new_systolic,
                'Diastolic (mmHg)': new_diastolic,
                'Heart Rate (bpm)': new_heart
            })
            st.success(f"Data for {new_date} added!")
            st.experimental_rerun()
        except ValueError:
            st.error("Invalid date format! Use YYYY-MM-DD")

# 展示已添加的新增数据
if st.session_state.new_data_list:
    st.subheader("New Data Added")
    new_df = pd.DataFrame(st.session_state.new_data_list)
    st.dataframe(new_df, width='stretch')
    if st.button("Clear All"):
        st.session_state.new_data_list = []
        st.experimental_rerun()

# 3. 生成图表
st.subheader("Generate Trend Chart")
if st.button("Generate Chart", type="primary"):
    combined_df = pd.concat([original_df, pd.DataFrame(st.session_state.new_data_list)], ignore_index=True)
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)

    dates = combined_df['Date'].dt.strftime('%Y-%m-%d').tolist()
    systolic = combined_df['Systolic (mmHg)'].tolist()
    diastolic = combined_df['Diastolic (mmHg)'].tolist()
    heart_rate = combined_df['Heart Rate (bpm)'].tolist()

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

    st.subheader("Export Data")
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    st.download_button(
        label="Download Chart (PNG)",
        data=buf,
        file_name=f'bp_hr_chart_{start_date}-{end_date}.png',
        mime='image/png'
    )

    csv_data = combined_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="Download Data (CSV)",
        data=csv_data,
        file_name=f'bp_hr_data_{start_date}-{end_date}.csv',
        mime='text/csv'
    )
