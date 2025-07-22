import pandas as pd
import numpy as np
import streamlit as st # streamlit 가져오기

# 1. 데이터 불러오기 및 전처리
# '혼잡도_통계_요약 (1).csv'가 Streamlit 앱과 같은 디렉토리에 있다고 가정합니다.
try:
    df = pd.read_csv("혼잡도_통계_요약 (1).csv", encoding="cp949")
    df["역명"] = df["역명"].astype(str).str.replace(r"\\s+", "", regex=True)
    df["주말여부"] = df["요일"].apply(lambda x: "주말" if x in ["토요일", "일요일"] else "평일")

    # 실제 열 이름에 맞게 수정
    if 'mean' in df.columns and 'std' in df.columns:
        df.rename(columns={'mean': '혼잡도평균', 'std': '혼잡도표준편차'}, inplace=True)
except FileNotFoundError:
    st.error("오류: '혼잡도_통계_요약 (1).csv' 파일을 찾을 수 없습니다. CSV 파일이 같은 디렉토리에 있는지 확인하세요.")
    st.stop() # 파일을 찾을 수 없으면 앱을 중지합니다.

# 대전 지하철 맞춤 혼잡도 색상 구분
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

# 2. 혼잡도 예측 함수 (시간대 문자열 변환 포함)
def get_congestion_level(station, weekday, hour, df):
    def convert_hour_to_range_string(hour):
        end_hour = (hour + 1) % 24
        return f"{hour:02d}-{end_hour:02d}시"

    hour_range = convert_hour_to_range_string(hour)
    day_type = "주말" if weekday in ["토요일", "일요일"] else "평일"

    filtered = df[
        (df["역명"] == station) &
        (df["주말여부"] == day_type) &
        (df["시간대"] == hour_range)
    ]

    if filtered.empty:
        return f"[❗] 데이터 없음: {station}, {weekday}, {hour_range}"

    row = filtered.iloc[0]
    if '혼잡도평균' not in row or '혼잡도표준편차' not in row:
        return "[❗] '혼잡도평균' 또는 '혼잡도표준편차' 열이 없습니다. 열 이름을 확인하세요."

    mu, sigma = row["혼잡도평균"], row["혼잡도표준편차"]
    congestion = np.clip(np.random.normal(mu, sigma), 0, 100)
    color = get_color(congestion)

    return f"[{station}역 | {weekday} {hour_range}]\\n예상 혼잡도: {congestion:.1f}%\\n혼잡도 수준: {color}"

# --- Streamlit UI ---
st.title("대전 지하철 혼잡도 예측 앱")

# 드롭다운을 위한 고유 역 이름과 요일 가져오기
if 'df' in locals(): # df가 성공적으로 로드되었는지 확인
    station_options = sorted(df["역명"].unique().tolist())
    weekday_options = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
else: # df 로드 실패 시 대체
    station_options = ["대동", "시청", "대전역"] # 예시 역
    weekday_options = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]


station = st.selectbox("역명을 선택하세요:", station_options)
weekday = st.selectbox("요일을 선택하세요:", weekday_options)
hour = st.slider("시간대를 선택하세요 (0-23시):", 0, 23, 7) # 기본값은 오전 7시

if st.button("혼잡도 예측하기"):
    if 'df' in locals(): # df가 로드된 경우에만 예측 실행
        result = get_congestion_level(station, weekday, hour, df)
        st.markdown(result.replace("\\n", "  \n")) # 새 줄을 위해 마크다운 사용
    else:
        st.warning("데이터 파일을 불러오지 못하여 예측을 수행할 수 없습니다.")