import streamlit as st
import pandas as pd
import plotly.express as px

# 기본 설정 & 제목
st.set_page_config(page_title="2024년도 화재 대시보드", layout="wide")

st.markdown(
    "<h1 style='text-align:center;'> 2024년도 화재 발생 현황 대시보드 🔥</h1>",
    unsafe_allow_html=True
)
st.write("")  # 여백

# 데이터 로드 
@st.cache_data
def load_data():
    df = pd.read_excel("2024_fire.xlsx")

    # 날짜 처리
    df["화재발생년원일"] = pd.to_datetime(df["화재발생년원일"])
    df["year"] = df["화재발생년원일"].dt.year

    # 2024년만 사용
    df_2024 = df[df["year"] == 2024].copy()

    # 시도 이름 정리 (옛 이름 → 새 이름 통일)
    df_2024["시도"] = df_2024["시도"].replace({
        "강원도": "강원특별자치도",
        "전라북도": "전북특별자치도"
    })

    # 월 / 시간 파생 컬럼 (2페이지에서 쓸 예정)
    df_2024["월"] = df_2024["화재발생년원일"].dt.to_period("M").astype(str)
    df_2024["시간"] = df_2024["화재발생년원일"].dt.hour

    # 시도 단위 집계 (1페이지 지도용)
    df_sido = df_2024.groupby("시도", as_index=False).agg({
        "화재발생년원일": "count",
        "인명피해(명)소계": "sum",
        "재산피해소계": "sum"
    })

    df_sido = df_sido.rename(columns={
        "화재발생년원일": "화재건수",
        "재산피해소계": "재산피해"
    })

    # 시도별 좌표
    sido_coords = {
        "서울특별시": (37.5665, 126.9780),
        "부산광역시": (35.1796, 129.0756),
        "대구광역시": (35.8714, 128.6014),
        "인천광역시": (37.4563, 126.7052),
        "광주광역시": (35.1595, 126.8526),
        "대전광역시": (36.3504, 127.3845),
        "울산광역시": (35.5384, 129.3114),
        "세종특별자치시": (36.4800, 127.2890),
        "경기도": (37.4138, 127.5183),
        "강원특별자치도": (37.8228, 128.1555),
        "충청북도": (36.6357, 127.4917),
        "충청남도": (36.5184, 126.8000),
        "전북특별자치도": (35.7175, 127.1530),
        "전라남도": (34.8194, 126.8930),
        "경상북도": (36.5760, 128.5056),
        "경상남도": (35.2598, 128.6647),
        "제주특별자치도": (33.4996, 126.5312)
    }

    df_sido["lat"] = df_sido["시도"].map(lambda x: sido_coords.get(x, (None, None))[0])
    df_sido["lon"] = df_sido["시도"].map(lambda x: sido_coords.get(x, (None, None))[1])
    df_sido = df_sido.dropna(subset=["lat", "lon"])

    return df_2024, df_sido

# 데이터 불러오기
df_raw, df_sido = load_data()

# 공통 사이드바 필터
st.sidebar.header("필터")
sido_list = sorted(df_sido["시도"].unique().tolist())
sido_options = ["전체"] + sido_list
selected_sido = st.sidebar.selectbox("시도 선택", sido_options, index=0)

# 선택에 따라 데이터 필터링
default_center_lat = 36.3
default_center_lon = 127.8

if selected_sido == "전체":
    plot_df = df_sido.copy()
    center_lat = default_center_lat
    center_lon = default_center_lon
    df_filtered = df_raw.copy()
else:
    plot_df = df_sido[df_sido["시도"] == selected_sido].copy()
    center_lat = plot_df["lat"].iloc[0]
    center_lon = plot_df["lon"].iloc[0]
    df_filtered = df_raw[df_raw["시도"] == selected_sido].copy()

red_scale = ["#ffb3b3", "#ff8080", "#ff4d4d", "#ff1a1a", "#e60000", "#b30000"]


# 탭(페이지) 구성
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "🗺️ 시도별 현황",
    "📅 월별 / 시간대별",
    "🔥 화재 원인"
])

# 1️⃣ 탭 1 : 시도별 지도 
with tab1:
    col_map, col_right = st.columns([2, 1])

    with col_map:
        st.subheader("시도별 화재 발생 분포")

        fig = px.scatter_mapbox(
            plot_df,
            lat="lat",
            lon="lon",
            size="화재건수",
            size_max=45,
            color="화재건수",
            color_continuous_scale=red_scale,
            hover_name="시도",
            hover_data={
                "화재건수": True,
                "인명피해(명)소계": True,
                "재산피해": True,
                "lat": False,
                "lon": False
            },
            zoom=6.4,
            center={"lat": center_lat, "lon": center_lon}
        )

        fig.update_traces(marker={"opacity": 0.9})

        fig.update_layout(
            mapbox={
                "style": "white-bg",
                "layers": [
                    {
                        "sourcetype": "raster",
                        "source": ["https://xdworld.vworld.kr/2d/Base/202002/{z}/{x}/{y}.png"],
                        "below": "traces",
                        "opacity": 0.6
                    }
                ]
            },
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            height=650,
            width=650
        )

        st.plotly_chart(fig, use_container_width=False)

    # 오른쪽 : 지표별 TOP 10 랭킹
with col_right:
    st.markdown(
        "<div style='margin-left:-40px;'>",  # 값은 -20 ~ -80 사이에서 조절해봐
        unsafe_allow_html=True
    )

    st.subheader("지역별 TOP 10")

    # 지표 선택
    metric_option = st.radio(
        "정렬 기준 지표 선택",
        ("화재건수", "인명피해(명)소계", "재산피해"),
        horizontal=True
    )

    metric_label = {
        "화재건수": "화재 건수",
        "인명피해(명)소계": "인명 피해",
        "재산피해": "재산 피해"
    }

    # df_sido 전체 기준 TOP 10
    top10 = (
        df_sido[["시도", "화재건수", "인명피해(명)소계", "재산피해"]]
        .sort_values(metric_option, ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    # 순위 컬럼 추가
    top10.insert(0, "순위", top10.index + 1)

    st.markdown(f"**{metric_label[metric_option]} 기준 상위 10개 시도**")

    # 인덱스 제거 + 테이블 크기 확대 + 폰트 사이즈 증가
    st.dataframe(
        top10.style.set_properties(**{
            "font-size": "16px"
        }).format({
            "화재건수": "{:,}",
            "인명피해(명)소계": "{:,}",
            "재산피해": "{:,}"
        }),
        use_container_width=True,
        height=500,  # 더 크게 보이도록 확대
        hide_index=True  # 🔥 인덱스 제거
    )

    st.caption(
        f"선택한 지표({metric_label[metric_option]}) 기준으로 시도별 상위 10개 지역을 정렬한 표입니다."
    )

# =============================
# 2️⃣ 탭 2 : 월별 / 시간대별 (형식만 잡아둔 상태)
# =============================
with tab2:
    st.subheader("월별 / 시간대별 화재 발생 분석")

    col_month, col_hour = st.columns(2)

    with col_month:
        st.markdown("### 📅 월별 추세")
        st.info("여기에 월별 화재 건수 / 인명피해 / 재산피해 추세 그래프를 넣을 거야.")

    with col_hour:
        st.markdown("### ⏰ 시간대별 분포")
        st.info("여기에 시간대별(0~23시) 화재 발생 분포 그래프를 넣을 거야.")

# =============================
# 3️⃣ 탭 3 : 화재 원인 (형식만 잡아둔 상태)
# =============================
with tab3:
    st.subheader("화재 원인 분석")

    st.markdown("### 🔥 원인별 화재 비중")
    st.info(
        "여기에는 화재 원인(예: 전기, 부주의, 방화, 기계적 요인 등)을 기준으로 "
        "파이차트 / bar 차트 등을 넣어서 시각화할 예정이야."
    )

    st.markdown("### 📊 지역별 주요 원인 비교")
    st.info("시도별로 어떤 원인이 더 많이 발생하는지 비교하는 그래프도 추가할 수 있어.")
