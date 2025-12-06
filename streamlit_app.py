import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path


# -----------------------
# 0. 기본 설정
# -----------------------
st.set_page_config(
    page_title="서울·경기 화재 발생 현황 대시보드",
    layout="wide"
)

DATA_PATH = Path("소방청_화재발생 정보_20241231.csv")   # 🔹 네 CSV 파일 이름
GEOJSON_PATH = Path("korea_sgg.json")                  # 🔹 GitHub에서 받은 시군구 GeoJSON


# -----------------------
# 1. 데이터 로딩 함수
# -----------------------
@st.cache_data
def load_fire_data(path: Path) -> pd.DataFrame:
    # 한글 CSV → cp949 인코딩
    df = pd.read_csv(path, encoding="cp949")
    
    # 서울 + 경기만 필터링
    df = df[df["시도"].isin(["서울특별시", "경기도"])].copy()
    
    # 날짜/시간 컬럼 datetime으로 변환
    df["화재발생년원일"] = pd.to_datetime(df["화재발생년원일"])
    df["year"] = df["화재발생년원일"].dt.year
    
    return df


@st.cache_data
def load_geojson(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        geojson = json.load(f)
    return geojson


# 실제 데이터 로딩
df = load_fire_data(DATA_PATH)
geojson = load_geojson(GEOJSON_PATH)


# -----------------------
# 2. 지도용 집계 데이터 / 연도별 집계 데이터 만들기
# -----------------------
# (1) 시군구별 화재 건수
df_map = (
    df.groupby("시군구")
      .size()
      .reset_index(name="화재건수")
)

# (2) 연도별 화재 건수
df_yearly = (
    df.groupby("year")
      .size()
      .reset_index(name="화재건수")
      .sort_values("year")
)


# -----------------------
# 3. KPI(요약 지표) 계산
# -----------------------
total_fires = int(df.shape[0])
period_start = int(df["year"].min())
period_end = int(df["year"].max())

top_row = df_map.sort_values("화재건수", ascending=False).iloc[0]
top_region = top_row["시군구"]
top_region_count = int(top_row["화재건수"])


# -----------------------
# 4. 화면 상단 타이틀 + KPI 카드
# -----------------------
st.title("서울·경기 화재 발생 현황 대시보드 (Overview)")
st.caption(f"{period_start}–{period_end}년 소방청 화재발생 정보(서울·경기)를 기반으로 제작한 개요 화면입니다.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 화재 건수", f"{total_fires:,}건")

with col2:
    st.metric("분석 기간", f"{period_start}년 ~ {period_end}년")

with col3:
    st.metric("최다 발생 시·군·구", f"{top_region}", f"{top_region_count:,}건")


# -----------------------
# 5. 시군구별 화재 분포 지도(Choropleth)
# -----------------------
st.markdown("### 🗺️ 시군구별 화재 발생 분포 (서울·경기)")

fig_map = px.choropleth(
    df_map,
    geojson=geojson,
    locations="시군구",                     # 🔹 df_map의 기준 컬럼
    featureidkey="properties.SIG_KOR_NM",   # 🔹 GeoJSON 안에서 시군구 이름이 들어있는 컬럼 경로
    color="화재건수",
    color_continuous_scale="Reds",
    labels={"화재건수": "화재 건수"},
)

# 지도 레이아웃 정리
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(
    margin=dict(r=0, l=0, b=0, t=30),
    coloraxis_colorbar=dict(title="건수")
)

st.plotly_chart(fig_map, use_container_width=True)


# -----------------------
# 6. 연도별 화재 발생 추세 그래프
# -----------------------
st.markdown("### 📈 연도별 화재 발생 추세 (서울·경기)")

fig_line = px.line(
    df_yearly,
    x="year",
    y="화재건수",
    markers=True,
    labels={"year": "연도", "화재건수": "화재 건수"},
)

fig_line.update_layout(
    xaxis=dict(dtick=1),
    margin=dict(r=0, l=0, b=0, t=30)
)

st.plotly_chart(fig_line, use_container_width=True)
