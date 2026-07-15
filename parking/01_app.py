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
        # 한글 인코딩 에러 방지 (utf-8 실패 시 cp949로 읽기)
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='cp949')
        
        # 파일에 실제로 들어있는 컬럼명 확인
        cols = df.columns.tolist()
        
        # 데이터에 존재하는 적절한 컬럼 매핑하기
        # (서울시 데이터 컬럼명을 유연하게 찾습니다)
        name_col = next((c for c in cols if '주차장명' in c or '명칭' in c), None)
        lat_col = next((c for c in cols if '위도' in c or 'Y좌표' in c), None)
        lon_col = next((c for c in cols if '경도' in c or 'X좌표' in c), None)
        addr_col = next((c for c in cols if '주소' in c or '위치' in c), None)
        
        # 요금 컬럼 찾기 (기본주차요금, 주차요금, 요금 등 포함된 단어 찾기)
        fee_col = next((c for c in cols if '요금' in c or '유무료' in c), None)

        # 필수 정보(위치 정보)가 없으면 에러 메시지 출력
        if not (name_col and lat_col and lon_col):
            st.error("CSV 파일에서 '주차장명', '위도', '경도' 정보를 찾을 수 없습니다.")
            st.info(f"현재 파일의 컬럼 목록: {cols}")
        else:
            # 주소나 요금 컬럼이 없으면 빈 값으로 채우기 (에러 방지)
            if not addr_col: 
                df['주소_임시'] = '주소 정보 없음'
                addr_col = '주소_임시'
            if not fee_col: 
                df['요금_임시'] = '요금 정보 없음'
                fee_col = '요금_임시'

            # 데이터 전처리: 위도, 경도 결측치 제거 및 숫자 변환
            df = df.dropna(subset=[lat_col, lon_col])
            df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
            df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
            df = df.dropna(subset=[lat_col, lon_col]) # 변환 실패 데이터 제거
            
            # pydeck 지도 표시용 임시 컬럼 통일 (한글 컬럼 에러 방지)
            df['map_lat'] = df[lat_col]
            df['map_lon'] = df[lon_col]
            df['map_name'] = df[name_col]
            df['map_addr'] = df[addr_col]
            df['map_fee'] = df[fee_col]

            # --- 데이터 요약 정보 ---
            st.success("데이터 로드 완료!")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("총 주차장 수", f"{len(df)} 개")
            with col2:
                st.dataframe(df[[name_col, addr_col, fee_col]].head(), use_container_width=True)
            
            st.divider()
            
            # --- 지도 시각화 섹션 (Pydeck 사용) ---
            st.subheader("📍 주차장 위치 및 요금 안내 지도")
            
            # 지도의 초기 중심점 설정
            mid_lat = df['map_lat'].mean()
            mid_lon = df['map_lon'].mean()
            
            # Pydeck 레이어 설정
            layer = pdk.Layer(
                "ScatterplotLayer",
                df,
                get_position=["map_lon", "map_lat"],
                get_color="[0, 128, 255, 160]",  # 파란색 점
                get_radius=80,
                pickable=True,
                auto_highlight=True,
            )
            
            view_state = pdk.ViewState(
                latitude=mid_lat,
                longitude=mid_lon,
                zoom=12,
                pitch=0
            )
            
            # 툴팁 설정 (마우스 올렸을 때 보여줄 정보)
            tooltip = {
                "html": "<b>주차장명:</b> {map_name}<br/>"
                        "<b>주소:</b> {map_addr}<br/>"
                        "<b>주차요금:</b> {map_fee}",
                "style": {
                    "backgroundColor": "#1E1E24",
                    "color": "white",
                    "font-family": '"Helvetica Neue", Arial',
                    "z-index": "10000"
                }
            }
            
            # 지도 렌더링
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip
            ))

    except Exception as e:
        st.error(f"파일을 처리하는 중 예기치 못한 오류가 발생했습니다: {e}")

else:
    st.info("💡 준비하신 '서울시 공영주차장 안내 정보.csv' 파일을 위 창에 업로드해 주세요.")
