import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="2024년 화재 대시보드", layout="wide")
st.title("2024년 시도별 화재 발생 현황")

@st.cache_data
def load_data():
    df = pd.read_excel("2024_fire.xlsx")

    df["화재발생년원일"] = pd.to_datetime(df["화재발생년원일"])
    df["year"] = df["화재발생년원일"].dt.year
    df_2024 = df[df["year"] == 2024].copy()

    df_sido = df_2024.groupby("시도", as_index=False).agg({
        "화재발생년원일": "count",
        "인명피해(명)소계": "sum",
        "재산피해소계": "sum"
    })

    df_sido = df_sido.rename(columns={
        "화재발생년원일": "화재건수",
        "재산피해소계": "재산피해"
    })

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
        "강원도": (37.8228, 128.1555),
        "충청북도": (36.6357, 127.4917),
        "충청남도": (36.5184, 126.8000),
        "전라북도": (35.7175, 127.1530),
        "전라남도": (34.8194, 126.8930),
        "경상북도": (36.5760, 128.5056),
        "경상남도": (35.2598, 128.6647),
        "제주특별자치도": (33.4996, 126.5312),
        "제주도": (33.4996, 126.5312)
    }

    df_sido["lat"] = df_sido["시도"].map(lambda x: sido_coords.get(x, (None, None))[0])
    df_sido["lon"] = df_sido["시도"].map(lambda x: sido_coords.get(x, (None, None))[1])
    df_sido = df_sido.dropna(subset=["lat", "lon"])

    return df_sido

df_sido = load_data()

center_lat = 36.3
center_lon = 127.8

red_scale = ["#ffb3b3", "#ff8080", "#ff4d4d", "#ff1a1a", "#e60000", "#b30000"]

col_map, col_right = st.columns([2, 1])

with col_map:
    st.subheader("시도별 화재 발생 분포 (동그라미 크기 + 색상 = 화재건수)")

    fig = px.scatter_mapbox(
        df_sido,
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
            "재산피해": True
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
                    "source": ["https://xdworld.vworld.kr/2d/gray/202002/{z}/{x}/{y}.png"],
                    "below": "traces"
                }
            ]
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=650,
        width=650
    )

    st.plotly_chart(fig, use_container_width=False)
