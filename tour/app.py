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
    url = "https://apis.data.go.kr/B551011/KorService1/searchFestival1"

    # requests가 params를 전달할 때 자동 인코딩하므로 API_KEY는 디코딩 키여야 합니다.
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
        response = requests.get(url, params=params, timeout=10)

        # HTTP 응답 상태 체크
        if response.status_code != 200:
            st.error(f"API 요청 실패 (HTTP {response.status_code})")
            return pd.DataFrame()

        # JSON 디코딩 테스트
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

    except requests.exceptions.JSONDecodeError:
        st.error(
            "❌ API 응답을 해석할 수 없습니다.\n"
            "Secrets에 등록된 TOUR_API_KEY가 '디코딩(Decoding)' 키인지, "
            "또는 공공데이터포털에서 API 승인이 완료되었는지 확인해 주세요."
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
    df_filtered = df

# --- 탭 구성 ---
tab1, tab2, tab3 = st.tabs(
    ["🎰 축제 랜덤 뽑기", "📋 축제 목록 & 지도", "💬 한 줄 방명록"]
)

# [Tab 1] 축제 랜덤 뽑기
with tab1:
    st.subheader("🎲 결정장애 해결! 오늘 갈 축제 랜덤 추천")
    st.write("버튼을 누르면 전국 축제 중 하나를 무작위로 추천해 드립니다.")

    if st.button("🎉 아무 축제나 하나 뽑아줘!", use_container_width=True):
        selected = df.sample(n=1).iloc[0]

        st.balloons()
        st.success(f"🎉 **{selected['title']}** (으)로 떠나보는 건 어떨까요?")

        col1, col2 = st.columns([1, 2])
        with col1:
            img_url = selected.get("firstimage")
            if img_url and str(img_url).startswith("http"):
                st.image(img_url, use_container_width=True)
            else:
                st.info("🖼️ 대표 이미지가 없는 축제입니다.")
        with col2:
            st.markdown(f"**📍 위치:** {selected.get('addr1', '정보 없음')}")
            st.markdown(
                f"**📅 기간:** {selected.get('eventstartdate', '')} ~ {selected.get('eventenddate', '')}"
            )
            st.markdown(f"**📞 문의:** {selected.get('tel', '정보 없음')}")

# [Tab 2] 목록 및 지도
with tab2:
    st.subheader("📍 축제 위치 지도")
    if not df_map.empty:
        st.map(df_map[["lat", "lon"]])
    else:
        st.caption("위치 데이터가 제공되지 않습니다.")

    st.subheader(f"📋 축제 리스트 ({len(df_filtered)}건)")

    for idx, row in df_filtered.iterrows():
        with st.expander(f"🎪 {row['title']}"):
            c1, c2 = st.columns([1, 3])
            with c1:
                img_url = row.get("firstimage2") or row.get("firstimage")
                if img_url and str(img_url).startswith("http"):
                    st.image(img_url, use_container_width=True)
            with c2:
                st.write(f"**주소:** {row.get('addr1', '정보 없음')}")
                st.write(
                    f"**일정:** {row.get('eventstartdate', '')} ~ {row.get('eventenddate', '')}"
                )
                if row.get("tel"):
                    st.write(f"**전화번호:** {row.get('tel')}")

# [Tab 3] 커뮤니티 방명록
with tab3:
    st.subheader("💬 축제 이야기 나누기")

    if "comments" not in st.session_state:
        st.session_state.comments = [
            {"name": "여행가", "text": "주말에 가볼 만한 축제 보러 왔어요!"}
        ]

    with st.form("comment_form"):
        name = st.text_input("닉네임", max_chars=10)
        text = st.text_area("방명록 작성", max_chars=100)
        submitted = st.form_submit_button("등록하기")

        if submitted and name and text:
            st.session_state.comments.append({"name": name, "text": text})
            st.success("댓글이 등록되었습니다!")

    st.divider()
    for comment in reversed(st.session_state.comments):
        st.write(f"**{comment['name']}**: {comment['text']}")
