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
    "CSV 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("데이터 업로드 완료!")

    st.subheader("주차장 데이터")

    st.dataframe(df, use_container_width=True)

    st.divider()

    st.subheader("주소 검색")

    keyword = st.text_input("주소 입력")

    if keyword:

        result = df[df["주소"].str.contains(keyword, case=False, na=False)]

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

            st.error("검색 결과가 없습니다.")

    st.divider()

    st.subheader("주차장 위치")

    df["tooltip"] = (
        "<b>주차장명</b> : "
        + df["주차장명"]
        + "<br><b>주소</b> : "
        + df["주소"]
        + "<br><b>요금</b> : "
        + df["기본요금"]
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[경도, 위도]',
        get_radius=60,
        get_fill_color=[255,0,0,180],
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df["위도"].mean(),
        longitude=df["경도"].mean(),
        zoom=11
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html":"{tooltip}",
            "style":{
                "backgroundColor":"steelblue",
                "color":"white"
            }
        }
    )

    st.pydeck_chart(deck)

else:

    st.info("CSV 파일을 업로드하세요.")
