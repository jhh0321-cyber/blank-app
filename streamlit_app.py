pip install streamlit pandas plotly
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🌤 날씨 대시보드", page_icon="🌤", layout="wide")

st.title("🌤 서울시 최근 일주일 날씨 대시보드")
st.markdown("기온, 습도, 체감온도 변화를 시각화해보세요.")

# --- 샘플 데이터 (실제 API 안 써도 됨) ---
data = {
    "날짜": pd.date_range("2025-10-30", periods=7, freq="D"),
    "기온(°C)": [18, 20, 22, 19, 17, 15, 16],
    "체감온도(°C)": [17, 19, 21, 18, 16, 14, 15],
    "습도(%)": [60, 55, 58, 65, 70, 72, 68],
    "강수량(mm)": [0, 0, 1.5, 0, 2.0, 5.2, 0]
}
df = pd.DataFrame(data)

# --- 필터 ---
metric = st.selectbox("📊 보고 싶은 지표 선택", ["기온(°C)", "체감온도(°C)", "습도(%)", "강수량(mm)"])

# --- 시각화 ---
fig = px.line(df, x="날짜", y=metric, markers=True, title=f"{metric} 변화 추이", line_shape="spline")
st.plotly_chart(fig, use_container_width=True)

# --- 요약 통계 ---
st.subheader("📈 요약 통계")
col1, col2, col3 = st.columns(3)
col1.metric("최고", f"{df[metric].max():.1f}")
col2.metric("최저", f"{df[metric].min():.1f}")
col3.metric("평균", f"{df[metric].mean():.1f}")

# --- 원본 데이터 ---
with st.expander("🗂 원본 데이터 보기"):
    st.dataframe(df, use_container_width=True)

st.success("✅ 완성! 이걸 기반으로 디자인만 조금 바꾸면 제출용 대시보드 완성입니다.")
