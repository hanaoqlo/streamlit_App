import datetime
import random
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🎉 전국 축제 탐험대", page_icon="🎈", layout="wide"
)

# 2. 깃허브의 .streamlit/secrets.toml 에서 API Key 로드
try:
    API_KEY = st.secrets["TOUR_API_KEY"]
except KeyError:
    st.error(
        "❌ API Key를 찾을 수 없습니다. .streamlit/secrets.toml 파일에 TOUR_API_KEY가 설정되어 있는지 확인해주세요."
    )
    st.stop()


# 3. 한국관광공사 API 호출 함수
@st.cache_data(ttl=3600)
def get_festival_data(event_start_date):
    #공공데이터포털 https 타임아웃 방지를 위해 http 사용
    url = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"

    # requests가 params 전달 시 자동 인코딩하므로 API_KEY는 디코딩 키여야 합니다.
    params = {
        "serviceKey": API_KEY,
        "numOfRows": "100",
        "pageNo": "1",
        "MobileOS": "ETC",
        "MobileApp": "FestivalApp",
        "_type": "json",
        "listYN": "Y",
        "arrange": "A",  # 대표이미지가 있는 순으로 정렬
        "eventStartDate": event_start_date,
    }

    try:
        # 서버 응답 지연을 대비해 timeout을 30초로 설정
        response = requests.get(url, params=params, timeout=30)

        # HTTP 응답 상태 체크
        if response.status_code != 200:
            st.error(f"API 요청 실패 (HTTP 상태 코드: {response.status_code})")
            return pd.DataFrame()

        # JSON 디코딩
        res_data = response.json()

        # API 내부 헤더 결과 검증
        header = res_data.get("response", {}).get("header", {})
        if header.get("resultCode") != "0000":
            st.error(
                f"API 오류 발생: {header.get('resultMsg')} (코드: {header.get('resultCode')})"
            )
            return pd.DataFrame()

        items = res_data["response"]["body"]["items"]["item"]
        return pd.DataFrame(items)

    except requests.exceptions.Timeout:
        st.error(
            "⏱️ 공공데이터포털 서버의 응답이 지연되고 있습니다. 잠시 후 새로고침해 주세요."
        )
        return pd.DataFrame()
    except requests.exceptions.JSONDecodeError:
        st.error(
            "❌ API 응답을 해석할 수 없습니다.\n"
            "Secrets의 TOUR_API_KEY가 '디코딩(Decoding)' 키인지 확인해 주세요."
        )
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()


# --- 메인 화면 UI ---
st.title("🎈 전국 축제 어디까지 가봤니?")
st.caption("한국관광공사 Open API 기반 실시간 축제 안내 앱")

# 오늘 날짜 기준으로 진행 중/예정된 축제 조회 (YYYYMMDD 형식)
today_str = datetime.datetime.now().strftime("%Y%m%d")
df = get_festival_data(today_str)

if df.empty:
    st.info("조회된 축제 데이터가 없거나 API 연결 확인이 필요합니다.")
    st.stop()

# 좌표 데이터 전처리 (지도 표시용)
if "mapx" in df.columns and "mapy" in df.columns:
    df["mapx"] = pd.to_numeric(df["mapx"], errors="coerce")
    df["mapy"] = pd.to_numeric(df["mapy"], errors="coerce")
    df_map = df.dropna(subset=["mapx", "mapy"]).rename(
        columns={"mapx": "lon", "mapy": "lat"}
    )
else:
    df_map = pd.DataFrame()

# --- 사이드바 필터 ---
st.sidebar.header("🔍 검색 및 필터")
search_keyword = st.sidebar.text_input("축제명 검색", "")

if search_keyword:
    df_filtered = df[df["title"].str.contains(search_keyword, na=False)]
else:
