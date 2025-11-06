import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(page_title="🌤 서울 실시간 날씨 대시보드", page_icon="🌤", layout="wide")
st.title("🌤 서울 최근 7일 실시간 날씨 대시보드")
st.caption("데이터 출처: Open-Meteo API (실제 관측 데이터, 예측 제외)")

# --- 위치 및 변수 설정 ---
LAT, LON = 37.5665, 126.9780   # 서울 시청 좌표
TIMEZONE = "Asia/Seoul"
HOURLY_VARS = ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "precipitation"]
DAILY_VARS = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]

# --- 데이터 불러오기 함수 ---
@st.cache_data(ttl=600)
def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly={','.join(HOURLY_VARS)}"
        f"&daily={','.join(DAILY_VARS)}"
        f"&past_days=7&forecast_days=0"  # ✅ 예측 데이터 제외!
        f"&timezone={TIMEZONE}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    js = r.json()

    # 시간별 데이터
    h = pd.DataFrame(js["hourly"])
    h["time"] = pd.to_datetime(h["time"])
    h = h.rename(columns={
        "temperature_2m": "기온(°C)",
        "apparent_temperature": "체감온도(°C)",
        "relative_humidity_2m": "습도(%)",
        "precipitation": "강수량(mm)"
    })

    # 일별 데이터
    d = pd.DataFrame(js["daily"])
    d["time"] = pd.to_datetime(d["time"])
    d = d.rename(columns={
        "temperature_2m_max": "최고기온(°C)",
        "temperature_2m_min": "최저기온(°C)",
        "precipitation_sum": "일강수량(mm)"
    })
    return h, d

# --- 데이터 불러오기 ---
try:
    hourly_df, daily_df = fetch_weather()
except Exception as e:
    st.error(f"데이터 불러오기 실패: {e}")
    st.stop()

# --- 사용자 선택 UI ---
left, right = st.columns([1.3, 1])
with left:
    metric = st.selectbox("📊 지표 선택 (시간별)", ["기온(°C)", "체감온도(°C)", "습도(%)", "강수량(mm)"])
with right:
    gran = st.radio("⏱ 데이터 단위 선택", ["시간별", "일별"], horizontal=True)

# --- 시각화 ---
if gran == "시간별":
    fig = px.line(hourly_df, x="time", y=metric, markers=True, title=f"[시간별] 최근 7일 {metric} 변화")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 요약 통계 (시간별)")
    col1, col2, col3 = st.columns(3)
    col1.metric("최고", f"{hourly_df[metric].max():.1f}")
    col2.metric("최저", f"{hourly_df[metric].min():.1f}")
    col3.metric("평균", f"{hourly_df[metric].mean():.1f}")

    with st.expander("🗂 원본 데이터 (시간별)"):
        st.dataframe(hourly_df, use_container_width=True)

else:
    d_long = daily_df.melt(id_vars=["time"], var_name="지표", value_name="값")
    fig = px.line(d_long, x="time", y="값", color="지표", markers=True, title="[일별] 최고/최저기온 및 강수량")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 요약 통계 (일별)")
    c1, c2, c3 = st.columns(3)
    c1.metric("평균 최고기온", f"{daily_df['최고기온(°C)'].mean():.1f}")
    c2.metric("평균 최저기온", f"{daily_df['최저기온(°C)'].mean():.1f}")
    c3.metric("총 강수량", f"{daily_df['일강수량(mm)'].sum():.1f}")

    with st.expander("🗂 원본 데이터 (일별)"):
        st.dataframe(daily_df, use_container_width=True)

st.success("✅ 실제 관측 데이터 기반 (미래 예보 제외)")
