import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 안내 시스템")
st.write("CSV 파일을 업로드하면 주소별 주차요금을 확인할 수 있습니다.")

uploaded_file = st.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    # 여러 인코딩 자동 시도
    encodings = ["utf-8", "utf-8-sig", "cp949", "euc-kr"]

    df = None

    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"✅ {enc} 인코딩으로 파일을 읽었습니다.")
            break
        except Exception:
            pass

    if df is None:
        st.error("❌ CSV 파일을 읽을 수 없습니다. 인코딩 또는 파일 형식을 확인하세요.")
        st.stop()

    # 필수 컬럼 확인
    required_columns = ["주차장명", "주소", "위도", "경도", "기본요금"]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"다음 컬럼이 없습니다: {', '.join(missing_columns)}")
        st.write("현재 컬럼 목록")
        st.write(df.columns.tolist())
        st.stop()

    # 데이터 미리보기
    st.subheader("📋 주차장 데이터")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # 주소 검색
    st.subheader("🔍 주소 검색")

    keyword = st.text_input("주소를 입력하세요.")

    if keyword:

        result = df[df["주소"].astype(str).str.contains(keyword, case=False, na=False)]

        if len(result) > 0:

            st.success(f"{len(result)}개의 주차장을 찾았습니다.")

            for _, row in result.iterrows():

                st.markdown(f"""
### 🚗 {row['주차장명']}

**주소**

{row['주소']}

**기본요금**

{row['기본요금']}

---
""")

        else:
            st.warning("검색 결과가 없습니다.")

    st.divider()

    # 지도
    st.subheader("🗺️ 공영주차장 지도")

    df["tooltip"] = (
        "<b>주차장명</b> : "
        + df["주차장명"].astype(str)
        + "<br><b>주소</b> : "
        + df["주소"].astype(str)
        + "<br><b>요금</b> : "
        + df["기본요금"].astype(str)
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[경도, 위도]",
        get_radius=60,
        get_fill_color=[255, 0, 0, 180],
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df["위도"].mean(),
        longitude=df["경도"].mean(),
        zoom=11,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "{tooltip}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        },
    )

    st.pydeck_chart(deck)

else:
    st.info("⬆️ CSV 파일을 업로드하세요.")
