import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import koreanize_matplotlib
import re

# 페이지 기본 설정
st.set_page_config(
    page_title="유튜브 댓글 분석기",
    page_icon="🎬",
    layout="wide"
)

# --- 사이드바: API 키 및 설정 ---
st.sidebar.title("⚙️ 설정")
api_key = st.sidebar.text_input("YouTube Data API v3 Key 입력", type="password")
max_comments = st.sidebar.slider("수집할 댓글 개수", min_value=10, max_value=500, value=100, step=10)

st.title("🎬 유튜브 댓글 분석기")
st.caption("유튜브 영상 링크를 입력하여 댓글의 시간대별 추이와 키워드 워드클라우드를 확인해보세요.")

# --- 함수: 유튜브 영상 ID 추출 ---
def extract_video_id(url):
    pattern = r'(?:v=|\/([0-9A-Za-z_-]{11}).*|near\/|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(pattern, url)
    return match.group(2) if match else None

# --- 함수: 댓글 수집 ---
def get_youtube_comments(api_key, video_id, max_results=100):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        next_page_token = None

        while len(comments) < max_results:
            # 한번에 최대 100개까지 요청 가능
            request_count = min(100, max_results - len(comments))
            
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=request_count,
                pageToken=next_page_token,
                order="time"
            ).execute()

            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': snippet['authorDisplayName'],
                    'comment': snippet['textOriginal'],
                    'published_at': snippet['publishedAt'],
                    'like_count': snippet['likeCount']
                })

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return pd.DataFrame(comments)
    except Exception as e:
        st.error(f"댓글을 불러오는 중 오류가 발생했습니다: {e}")
        return None

# --- 메인 실행 로직 ---
video_url = st.text_input("유튜브 영상 URL을 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    video_id = extract_video_id(video_url)
    
    if not video_id:
        st.warning("유효한 유튜브 URL이 아닙니다. 다시 확인해 주세요.")
    else:
        # 1. 영상 임베드 및 기본 정보
        st.subheader("📺 영상 확인")
        st.video(video_url)
        
        if not api_key:
            st.info("👈 사이드바에서 YouTube Data API 키를 입력하면 분석을 시작합니다.")
        else:
            if st.button("댓글 수집 및 분석 시작 🚀"):
                with st.spinner("댓글 데이터를 수집하고 분석 중입니다..."):
                    df = get_youtube_comments(api_key, video_id, max_comments)

                if df is not None and not df.empty:
                    # 날짜 데이터 정형화
                    df['published_at'] = pd.to_datetime(df['published_at'])
                    
                    st.success(f"성공적으로 {len(df)}개의 댓글을 수집했습니다!")
                    st.markdown("---")

                    # --- 메트릭 요약 ---
                    col1, col2, col3 = st.columns(3)
                    col1.metric("총 수집 댓글 수", f"{len(df)}개")
                    col2.metric("총 좋아요 수", f"{df['like_count'].sum()}개")
                    col3.metric("최대 좋아요 댓글", f"{df['like_count'].max()}개")

                    st.markdown("---")

                    # --- 2. 시간대별 댓글 작성 추이 ---
                    st.subheader("📈 시간대별 댓글 작성 추이")
                    # 일별 댓글 작성량 집계
                    df_time = df.set_index('published_at').resample('D').size().reset_index(name='count')
                    
                    fig_time = px.line(
                        df_time, 
                        x='published_at', 
                        y='count',
                        title='일자별 댓글 작성 빈도',
                        labels={'published_at': '날짜', 'count': '댓글 수'},
                        markers=True
                    )
                    st.plotly_chart(fig_time, use_container_width=True)

                    # --- 3. 댓글 반응도 (좋아요 분포) ---
                    st.subheader("👍 댓글 좋아요(반응도) TOP 5")
                    top_liked = df.sort_values(by='like_count', ascending=False).head(5)
                    st.dataframe(
                        top_liked[['author', 'comment', 'like_count', 'published_at']],
                        use_container_width=True,
                        hide_index=True
                    )

                    # --- 4. 한글 워드클라우드 ---
                    st.subheader("☁️ 댓글 키워드 워드클라우드")
                    
                    # 텍스트 전처리 (간단한 한글 및 공백 추출)
                    all_text = " ".join(df['comment'].tolist())
                    clean_text = re.sub(r'[^가-힣\s]', '', all_text)

                    if clean_text.strip():
                        # 스트림릿 클라우드 환경에서 한글 폰트 적용 (koreanize_matplotlib 연동)
                        wc = WordCloud(
                            font_path=koreanize_matplotlib.fonts.get_font_path(),
                            background_color='white',
                            width=800,
                            height=400,
                            max_words=100
                        ).generate(clean_text)

                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        st.pyplot(fig)
                    else:
                        st.info("워드클라우드를 생성할 한글 텍스트 데이터가 부족합니다.")

                    # --- 5. 원본 데이터 보기 ---
                    with st.expander("📄 수집된 댓글 데이터 전체 보기"):
                        st.dataframe(df)
