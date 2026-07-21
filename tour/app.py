import datetime
import random
import requests
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="🎉 전국 축제 탐험대", page_icon="🎈", layout="wide"
)

# Secrets에서 API Key 불러오기
try:
    API_KEY = st.secrets["TOUR_API_KEY"]
except KeyError:
    st.error(
        "API Key 설정이 필요합니다. Streamlit Secrets에 TOUR_API_KEY를 추가해주세요."
    )
    st.stop()


# 한국관광공사 API 호출 함수
@st.cache_data(ttl=3600)
def get_festival_data(event_start_date):
    url = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": "100",
        "pageNo": "1",
        "MobileOS": "ETC",
        "MobileApp": "FestivalApp",
        "_type": "json",
        "listYN": "Y",
        "arrange": "A",  # 정렬: 대표이미지가 있는 정렬
        "eventStartDate": event_start_date,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        res_data = response.json()
        items = res_data["response"]["body"]["items"]["item"]
        return pd.DataFrame(items)
    except Exception as e:
        st.error("데이터를 불러오는 중 오류가 발생했습니다.")
        return pd.DataFrame()


# 헤더 영역
st.title("🎈 전국 축제 어디까지 가봤니?")
st.caption("한국관광공사 Open API 기반 실시간 축제 안내 앱")

# 데이터 로드 (오늘 날짜 기준 이후 축제 검색)
today_str = datetime.datetime.now().strftime("%Y%m%d")
df = get_festival_data(today_str)

if df.empty:
    st.warning("현재 조회 가능한 축제 데이터가 없습니다.")
    st.stop()

# 좌표 데이터 처리 (Streamlit 지도용)
df["mapx"] = pd.to_numeric(df["mapx"], errors="coerce")
df["mapy"] = pd.to_numeric(df["mapy"], errors="coerce")
df_map = df.dropna(subset=["mapx", "mapy"]).rename(
    columns={"mapx": "lon", "mapy": "lat"}
)

# --- 사이드바 ---
st.sidebar.header("🔍 검색 및 필터")
search_keyword = st.sidebar.text_input("축제명 검색", "")

if search_keyword:
    df_filtered = df[df["title"].str.contains(search_keyword, na=False)]
else:
    df_filtered = df

# --- 메인 탭 구성 ---
tab1, tab2, tab3 = st.tabs(
    ["🎰 축제 렌덤 뽑기", "📋 축제 목록 & 지도", "💬 한 줄 방명록"]
)

# [Tab 1] 재밌는 기능: 랜덤 추천
with tab1:
    st.subheader("🎲 결정장애 해결! 오늘 갈 축제 랜덤 추천")
    st.write("버튼을 누르면 전국 축제 중 하나를 무작위로 추천해 드립니다.")

    if st.button("🎉 아무 축제나 하나 뽑아줘!", use_container_width=True):
        selected = df.sample(n=1).iloc[0]

        st.balloons()  # 스트림릿 풍선 애니메이션 효과
        st.success(f"🎉 **{selected['title']}** (으)로 떠나보는 건 어떨까요?")

        col1, col2 = st.columns([1, 2])
        with col1:
            img_url = selected.get("firstimage")
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.info("🖼️ 이미지가 제공되지 않는 축제입니다.")
        with col2:
            st.markdown(f"**📍 위치:** {selected.get('addr1', '정보 없음')}")
            st.markdown(
                f"**📅 기간:** {selected.get('eventstartdate')} ~ {selected.get('eventenddate')}"
            )
            st.markdown(f"**📞 문의:** {selected.get('tel', '정보 없음')}")

# [Tab 2] 전체 축제 목록 및 지도
with tab2:
    st.subheader("📍 축제 위치 살펴보기")
    if not df_map.empty:
        st.map(df_map[["lat", "lon"]])

    st.subheader(f"📋 축제 리스트 ({len(df_filtered)}건)")

    for idx, row in df_filtered.iterrows():
        with st.expander(f"🎪 {row['title']}"):
            c1, c2 = st.columns([1, 3])
            with c1:
                if row.get("firstimage2"):
                    st.image(row["firstimage2"])
            with c2:
                st.write(f"**주소:** {row.get('addr1', '정보 없음')}")
                st.write(
                    f"**일정:** {row.get('eventstartdate')} ~ {row.get('eventenddate')}"
                )
                if row.get("tel"):
                    st.write(f"**전화번호:** {row.get('tel')}")

# [Tab 3] 커뮤니티 방명록
with tab3:
    st.subheader("💬 다녀온 축제 후기 or 기대평")

    if "comments" not in st.session_state:
        st.session_state.comments = [
            {"name": "여행가", "text": "주말에 가볼 만한 곳 찾아서 기뻐요!"}
        ]

    with st.form("comment_form"):
        name = st.text_input("닉네임", max_chars=10)
        text = st.text_area("메시지", max_chars=100)
        submitted = st.form_submit_button("등록하기")

        if submitted and name and text:
            st.session_state.comments.append({"name": name, "text": text})
            st.success("댓글이 등록되었습니다!")

    st.divider()
    for comment in reversed(st.session_state.comments):
        st.write(f"**{comment['name']}**: {comment['text']}")
