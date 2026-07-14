import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="글로벌 시가총액 Top 10 대시보드",
    page_icon="📈",
    layout="wide"
)

# 2. 글로벌 시가총액 Top 10 기업 정보 정의 (티커 기준)
TOP_10_COMPANIES = {
    "NVIDIA (NVDA)": "NVDA",
    "Apple (AAPL)": "AAPL",
    "Alphabet / Google (GOOGL)": "GOOGL",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "TSMC (TSM)": "TSM",
    "Broadcom (AVGO)": "AVGO",
    "Saudi Aramco (2222.SR)": "2222.SR",
    "Meta Platforms (META)": "META",
    "Tesla (TSLA)": "TSLA"
}

st.title("📈 글로벌 시가총액 Top 10 주식 대시보드")
st.markdown("최근 1년 동안의 글로벌 시가총액 상위 10개 기업의 주가 변화를 실시간으로 비교하고 분석합니다.")

# 3. 사이드바 구성 (사용자 입력 필터)
st.sidebar.header("🔍 대시보드 설정")

# 기업 다중 선택
selected_names = st.sidebar.multiselect(
    "시각화할 기업을 선택하세요 (다중 선택 가능):",
    options=list(TOP_10_COMPANIES.keys()),
    default=list(TOP_10_COMPANIES.keys())[:5] # 기본값으로 상위 5개 선택
)

# 시각화 기준 선택 (원래 주가 vs 첫날 대비 수익률)
chart_mode = st.sidebar.radio(
    "차트 표시 방식:",
    ("실제 주가 ($)", "누적 수익률 (%)")
)

# 데이터 수집 기간 설정 (최근 1년)
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# 4. 데이터 로드 함수 (캐싱 적용으로 속도 향상)
@st.cache_data(ttl=3600) # 1시간 동안 캐시 유지
def load_stock_data(tickers, start, end):
    data = pd.DataFrame()
    for name, ticker in tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start, end=end)
            if not hist.empty:
                # 종가(Close) 기준으로 데이터 프레임 병합
                data[name] = hist['Close']
        except Exception as e:
            st.warning(f"{name} ({ticker}) 데이터를 가져오는 중 오류가 발생했습니다.")
    return data

# 선택한 기업들의 티커 필터링
selected_tickers = {name: TOP_10_COMPANIES[name] for name in selected_names}

if selected_tickers:
    with st.spinner("데이터를 불러오는 중입니다..."):
        df = load_stock_data(selected_tickers, start_date, end_date)
    
    if not df.empty:
        # Index를 날짜 형식으로 깔끔하게 포맷팅
        df.index = df.index.date
        
        # 5. 데이터 가공 및 차트 생성 (Plotly)
        fig = go.Figure()

        if chart_mode == "실제 주가 ($)":
            for col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, 
                    y=df[col], 
                    mode='lines', 
                    name=col,
                    hovertemplate='%{x}<br>%{y:.2f} USD'
                ))
            y_title = "주가 (USD)"
            title_suffix = "실제 주가 흐름"
            
        else: # 누적 수익률 (%)
            # 첫 거래일 종가 기준 대비 변동률 계산: ((현재가격 - 첫날가격) / 첫날가격) * 100
            df_returns = df.apply(lambda x: ((x - x.iloc[0]) / x.iloc[0]) * 100)
            for col in df_returns.columns:
                fig.add_trace(go.Scatter(
                    x=df_returns.index, 
                    y=df_returns[col], 
                    mode='lines', 
                    name=col,
                    hovertemplate='%{x}<br>수익률: %{y:.2f}%'
                ))
            y_title = "누적 수익률 (%)"
            title_suffix = "첫날 대비 누적 수익률 변동"

        # 레이아웃 스타일 설정
        fig.update_layout(
            title=f"최근 1개년 {title_suffix}",
            xaxis_title="날짜",
            yaxis_title=y_title,
            hovermode="x unified",
            template="plotly_dark", # 스트림릿 테마와 잘 어울리는 다크 모드
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        # 6. 스트림릿 화면에 요소 출력
        # 메인 차트
        st.plotly_chart(fig, use_container_width=True)

        # 최근 데이터 표 보기
        st.subheader("📋 최근 주가 데이터 요약")
        st.dataframe(df.tail(10).style.format("{:.2f}"), use_container_width=True)
        
    else:
        st.error("불러온 주식 데이터가 없습니다. 티커 설정을 확인해주세요.")
else:
    st.info("시각화할 기업을 하나 이상 선택해주세요.")
