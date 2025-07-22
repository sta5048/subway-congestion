import streamlit as st
import pandas as pd
import numpy as np

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("혼잡도_통계_요약 (1).csv", encoding="cp949")
    df["역명"] = df["역명"].astype(str).str.replace(r"\s+", "", regex=True)
    df["주말여부"] = df["요일"].apply(lambda x: "주말" if x in ["토요일", "일요일"] else "평일")
    if 'mean' in df.columns and 'std' in df.columns:
        df.rename(columns={'mean': '혼잡도평균', 'std': '혼잡도표준편차'}, inplace=True)
    return df

df = load_data()

# 최고/최저 혼잡도 시간대 표시 함수
def get_peak_hours(station, weekday):
    day_type = "주말" if weekday in ["토요일", "일요일"] else "평일"
    subset = df[(df["역명"] == station) & (df["주말여부"] == day_type)]

    if subset.empty:
        return "❗ 관련 데이터가 없습니다."

    max_row = subset.loc[subset["혼잡도평균"].idxmax()]
    min_row = subset.loc[subset["혼잡도평균"].idxmin()]

    return (
        f"📊 **[{station}역 | {weekday} 기준 혼잡도 요약]**\n\n"
        f"🔴 가장 혼잡한 시간대: {max_row['시간대']} (예상 혼잡도: {max_row['혼잡도평균']:.1f}%)  \n"
        f"🔵 가장 여유로운 시간대: {min_row['시간대']} (예상 혼잡도: {min_row['혼잡도평균']:.1f}%)"
    )


# 혼잡도 색상 구분 함수
def get_color(val):
    if val <= 20:
        return "🔵 매우 여유"
    elif val <= 40:
        return "🟢 여유"
    elif val <= 60:
        return "🟡 보통"
    elif val <= 80:
        return "🟠 약간 혼잡"
    else:
        return "🔴 혼잡"

# 예측 함수
def get_congestion_level(station, weekday, hour):
    def hour_range(h):
        return f"{h:02d}-{(h + 1) % 24:02d}시"
    hr = hour_range(hour)
    day_type = "주말" if weekday in ["토요일", "일요일"] else "평일"

    filtered = df[
        (df["역명"] == station) &
        (df["주말여부"] == day_type) &
        (df["시간대"] == hr)
    ]

    if filtered.empty:
        return f"❗ 데이터 없음: {station}, {weekday}, {hr}", None

    row = filtered.iloc[0]
    mu, sigma = row["혼잡도평균"], row["혼잡도표준편차"]
    congestion = np.clip(np.random.normal(mu, sigma), 0, 100)
    return f"[{station}역 | {weekday} {hr}]\n예상 혼잡도: {congestion:.1f}%\n혼잡도 수준: {get_color(congestion)}", congestion

# ------------------- Streamlit UI -------------------

st.title("🚇 대전 지하철 혼잡도 예측")

station = st.selectbox("📍 역명을 선택하세요", sorted(df["역명"].unique()))
weekday = st.selectbox("📅 요일을 선택하세요", ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"])
hour = st.slider("⏰ 시간대를 선택하세요", 5, 23, 7)

if st.button("예측하기"):
    result_text, congestion = get_congestion_level(station, weekday, hour)
    st.markdown(result_text)
    if congestion is not None:
        st.progress(int(congestion))

    peak_info = get_peak_hours(station, weekday)
    st.markdown("---")
    st.markdown(peak_info)
    st.markdown("---")

