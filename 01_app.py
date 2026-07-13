import streamlit as st
from datetime import date

# 1. 페이지 기본 설정 및 디자인 (CSS 추가)
st.set_page_config(page_title="✨ 반짝반짝 별자리 궁합 ✨", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f7f9fc;
    }
    h1 {
        color: #4A0E4E;
        text-align: center;
        font-family: 'Nanum Gothic', sans-serif;
    }
    h3 {
        color: #2A2D34;
    }
    .stButton>button {
        background-color: #7B2CBF;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #9D4EDD;
        color: white;
    }
    .result-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 별자리 구하기 함수
def get_zodiac(birth_date):
    month = birth_date.month
    day = birth_date.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "양자리"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "황소자리"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "쌍둥이자리"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "게자리"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "사자자리"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 23):
        return "처녀자리"
    elif (month == 9 and day >= 24) or (month == 10 and day <= 22):
        return "천칭자리"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 22):
        return "전갈자리"
    elif (month == 11 and day >= 23) or (month == 12 and day <= 24):
        return "사수자리"
    elif (month == 12 and day >= 25) or (month == 1 and day <= 19):
        return "염소자리"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "물병자리"
    else:
        return "물고기자리"

# 3. 별자리별 데이터 (궁합 설정)
zodiac_info = {
    "양자리": {"good": ["사자자리", "사수자리"], "bad": ["게자리", "염소자리"]},
    "황소자리": {"good": ["처녀자리", "염소자리"], "bad": ["사자자리", "물병자리"]},
    "쌍둥이자리": {"good": ["천칭자리", "물병자리"], "bad": ["처녀자리", "물고기자리"]},
    "게자리": {"good": ["전갈자리", "물고기자리"], "bad": ["양자리", "천칭자리"]},
    "사자자리": {"good": ["양자리", "사수자리"], "bad": ["황소자리", "전갈자리"]},
    "처녀자리": {"good": ["황소자리", "염소자리"], "bad": ["쌍둥이자리", "사수자리"]},
    "천칭자리": {"good": ["쌍둥이자리", "물병자리"], "bad": ["게자리", "염소자리"]},
    "전갈자리": {"good": ["게자리", "물고기자리"], "bad": ["사자자리", "물병자리"]},
    "사수자리": {"good": ["양자리", "사자자리"], "bad": ["처녀자리", "물고기자리"]},
    "염소자리": {"good": ["황소자리", "처녀자리"], "bad": ["양자리", "천칭자리"]},
    "물병자리": {"good": ["쌍둥이자리", "천칭자리"], "bad": ["황소자리", "전갈자리"]},
    "물고기자리": {"good": ["게자리", "전갈자리"], "bad": ["쌍둥이자리", "사수자리"]}
}

# --- 메인 화면 UI ---
st.title("🔮 내 생일로 보는 별자리 & 친구 궁합")
st.write("생년월일을 입력하고 나의 별자리와 친구와의 숨겨진 궁합을 확인해보세요!")

st.markdown("---")

# 내 정보 입력
st.subheader("👤 나의 정보 입력")
my_name = st.text_input("당신의 이름을 입력해주세요:", "나")
my_birthday = st.date_input("당신의 생년월일을 선택해주세요:", date(2010, 1, 1))

# 친구 정보 입력
st.subheader("👥 친구의 정보 입력")
friend_name = st.text_input("친구의 이름을 입력해주세요:", "친구")
friend_birthday = st.date_input("친구의 생년월일을 선택해주세요:", date(2010, 5, 5))

st.markdown("---")

# 결과 보기 버튼
if st.button("✨ 궁합 결과 확인하기 ✨"):
    my_zodiac = get_zodiac(my_birthday)
    friend_zodiac = get_zodiac(friend_birthday)
    
    # 내 별자리 결과 출력
    st.markdown(f"### 🌟 {my_name}님의 별자리 결과")
    st.markdown(f"""
    <div class="result-box">
        <h4>당신의 별자리는 <b>[{my_zodiac}]</b> 입니다!</h4>
        <p>❤️ <b>잘 맞는 별자리:</b> {', '.join(zodiac_info[my_zodiac]['good'])}</p>
        <p>💙 <b>노력이 필요한 별자리:</b> {', '.join(zodiac_info[my_zodiac]['bad'])}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 친구 별자리 결과 출력
    st.markdown(f"### 🌟 {friend_name}님의 별자리 결과")
    st.markdown(f"""
    <div class="result-box">
        <h4>{friend_name}님의 별자리는 <b>[{friend_zodiac}]</b> 입니다!</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 두 사람의 궁합 분석
    st.markdown("### 💌 두 분의 최종 궁합은?")
    
    if friend_zodiac in zodiac_info[my_zodiac]["good"]:
        compatibility = "💖 **최고의 찰떡궁합!** 두 사람은 서로를 빛내주는 최고의 파트너입니다."
        bg_color = "#FFE5EC"
    elif friend_zodiac in zodiac_info[my_zodiac]["bad"]:
        compatibility = "⚡ **조금의 배려가 필요한 관계!** 서로 다른 매력을 가졌으니 조금 더 귀를 기울여주세요."
        bg_color = "#E8F0FE"
    else:
        compatibility = "🍏 **무난하고 평화로운 관계!** 서로 존중하며 좋은 친구가 될 수 있는 편안한 사이입니다."
        bg_color = "#F0FDF4"
        
    st.markdown(f"""
    <div class="result-box" style="background-color: {bg_color}; border: 1px solid #DDD;">
        <h4 style="text-align: center;">{my_name} 🤝 {friend_name}</h4>
        <p style="font-size: 16px; text-align: center;">{compatibility}</p>
    </div>
    """, unsafe_allow_html=True)
