import streamlit as st
import pandas as pd
import pydeck as pdk

# 페이지 설정
st.set_page_config(page_title="공영주차장 정보 안내", layout="wide")

st.title("🚗 공영주차장 정보 안내 앱")
st.markdown("공영주차장 CSV 데이터를 업로드하고 지도에서 주차요금과 위치를 확인하세요.")

# --- 데이터 업로드 섹션 ---
uploaded_file = st.file_uploader("주차장 데이터 CSV 파일을 업로드해주세요.", type=["csv"])

if uploaded_file is not None:
    try:
        # 데이터 불러오기 (인코딩 문제는 환경에 맞게 'utf-8' 또는 'cp949'로 변경 가능)
        df = pd.read_csv(uploaded_file, encoding='cp949')
        
        # 필수 컬럼 존재 여부 확인 데이터 가이드라인 제공
        required_columns = ['주차장명', '위도', '경도', '주소', '주차요금']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"CSV 파일에 다음 컬럼이 부족합니다: {', '.join(missing_columns)}")
            st.info("CSV 파일은 '주차장명', '위도', '경도', '주소', '주차요금' 컬럼을 포함해야 합니다.")
        else:
            # 데이터 전처리: 위도, 경도 결측치 제거 및 숫자 변환
            df = df.dropna(subset=['위도', '경도'])
            df['위도'] = pd.to_numeric(df['위도'])
            df['경도'] = pd.to_numeric(df['경도'])
            
            # --- 데이터 요약 정보 ---
            st.success("데이터 업로드 성공!")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("총 주차장 수", f"{len(df)} 개")
            with col2:
                st.dataframe(df[['주차장명', '주소', '주차요금']].head(), use_container_width=True)
            
            st.divider()
            
            # --- 지도 시각화 섹션 (Pydeck 사용) ---
            st.subheader("📍 주차장 위치 및 요금 안내 지도")
            
            # 지도의 초기 중심점 설정 (데이터의 평균 위/경도)
            mid_lat = df['위도'].mean()
            mid_lon = df['경도'].mean()
            
            # Pydeck 레이어 설정 (산점도 레이어)
            layer = pdk.Layer(
                "ScatterplotLayer",
                df,
                get_position=["경도", "위도"],
                get_color="[0, 128, 255, 160]",  # 파란색 (RGBA)
                get_radius=80,                  # 점의 크기 (미터 단위)
                pickable=True,                  # 마우스 오버/클릭 상호작용 활성화
                auto_highlight=True,
            )
            
            # 지도 뷰 상태 설정
            view_state = pdk.ViewState(
                latitude=mid_lat,
                longitude=mid_lon,
                zoom=12,
                pitch=0
            )
            
            # 툴팁 설정 (마우스를 올렸을 때 보여줄 정보)
            tooltip = {
                "html": "<b>주차장명:</b> {주차장명}<br/>"
                        "<b>주소:</b> {주소}<br/>"
                        "<b>주차요금:</b> {주차요금}",
                "style": {
                    "backgroundColor": "purple",
                    "color": "white",
                    "font-family": '"Helvetica Neue", Arial',
                    "z-index": "10000"
                }
            }
            
            # 스트림릿에 지도 렌더링
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip
            ))

    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        st.info("파일 인코딩(utf-8 또는 cp949) 및 데이터 형식을 확인해주세요.")

else:
    # 파일을 업로드하기 전 보여주는 가이드라인 샘플 템플릿
    st.info("💡 아래와 같은 형식의 CSV 파일을 업로드하시면 됩니다.")
    sample_data = pd.DataFrame({
        '주차장명': ['서울공영주차장', '강남주차빌딩'],
        '위도': [37.5665, 37.4979],
        '경도': [126.9780, 127.0276],
        '주소': ['서울특별시 중구 태평로1가', '서울특별시 강남구 역삼동'],
        '주차요금': ['5분당 250원', '무료 / 기본 1시간 3,000원']
    })
    st.dataframe(sample_data)
