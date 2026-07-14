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
# 비상장 기업(예: SpaceX)이나 데이터 수집이 제한적인 기업 대신 yfinance에서 실시간 조회가 원활한 상위 10개 대표 티커 구성
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
            hist
