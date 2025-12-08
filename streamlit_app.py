import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------
# 0. 페이지 기본 설정
# ------------------------
st.set_page_config(
    page_title="2024년 화재 대시보드",
    layout="wide"
)

st.title("2024년 시도별 화재 발생 현황")

# ------------------------
# 1. 데이터 로드 & 전처리
# ------------------------
@st.cache_data
def load_data():
    # 엑셀 파일 읽기 (파일 이름/경로는 상황에 맞게 수정)
    df = pd.read_excel("2024_fire.xlsx")

    # 날짜 컬럼 datetime으로 변환
    df["화재발생년원일"] = pd.to_datetime(df["화재발생년원일"])

    # 혹시 여러 연도가 섞여 있을 수 있으니 2024년만 필터
    df["year"] = df["화재발생년원일"].dt.year
    df_2024 = df[df["year"] == 2024].copy()

    # 시도별 집계: 화재건수, 인명피해, 재산피해
    df_sido = df_2024.groupby("시도", as_index=False).agg({
        "화재발생년원일": "count",        # 화재 건수
        "인명피해(명)소계": "sum",
        "재산피해소계": "sum"
    })

    df_sido = df_sido.rename(columns={
        "화재발생년원일": "화재건수",
        "재산피해소계": "재산피해"
    })

    # 시도별 위도/경도(대략 중심 좌표) 딕셔너리
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
        "강원도": (37.8228, 128.1555),
        "강원특별자치도": (37.8228, 128.1555),  # 데이터에 이렇게 들어가 있을 수도 있어서
        "충청북도": (36.6357, 127.4917),
        "충청남도": (36.5184, 126.8000),
        "충청남도": (36.5184, 126.8000),
        "충청남도": (36.5184, 126.8000),
        "충청남도": (36.5184, 126.8000),
        "충청남도": (36.5184, 126.8000),
        "전라북도": (35.7175, 127.1530),
        "전라남도": (34.8194, 126.8930),
        "경상북도": (36.5760, 128.5056),
        "경상남도": (35.2598, 128.6647),
        "제주특별자치도": (33.4996, 126.5312),
        "제주도": (33.4996, 126.5312)  # 혹시 이름 다르게 들어가 있으면 대비
    }

    # 위도/경도 컬럼 추가
    df_sido["lat"] = df_sido["시도"].map(lambda x: sido_coords.get(x, (None, None))[0])
    df_sido["lon"] = df_sido["시도"].map(lambda x: sido_coords.get(x, (None, None))[1])

    # 좌표가 없는 시도(이름이 딕셔너리에 없는 경우) 제거
    df_sido = df_sido.dropna(subset=["lat", "lon"])

    return df_sido

df_sido = load_data()

# 전체 전국 중심 좌표 (대충 대한민국 가운데)
center_lat, center_lon = 36.5, 127.8

# ------------------------
# 2. 레이아웃: 왼쪽에 지도
# ------------------------
col_map, col_right = st.columns([2, 1])

with col_map:
    st.subheader("시도별 화재 발생 분포 (점 크기 = 화재 건수)")

    fig = px.scatter_mapbox(
        df_sido,
        lat="lat",
        lon="lon",
        size="화재건수",               # 원 크기
        size_max=50,                   # 최대 원 크기 (조절 가능)
        hover_name="시도",
        hover_data={
            "화재건수": True,
            "인명피해(명)소계": True,
            "재산피해": True,
            "lat": False,
            "lon": False
        },
        zoom=5,
        center={"lat": center_lat, "lon": center_lon},
    )

    fig.update_layout(
        mapbox_style="carto-positron",   # 토큰 없이 쓸 수 있는 스타일
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("간단 설명 / 추후 추가 영역")
    st.write(
        """
        - 왼쪽 지도에서 시도별 화재 위험도를 한눈에 볼 수 있습니다.  
        - 마우스를 각 동그라미 위에 올리면  
          **화재건수, 인명피해(명)소계, 재산피해소계**를 확인할 수 있습니다.  
        - 이 영역에는 나중에 TOP 5 시도, 간단 통계 등을 추가할 수 있습니다.
        """
    )

