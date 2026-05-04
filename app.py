import streamlit as st
import google.generativeai as genai

# 페이지 스타일 설정 (위드멤버 스타일)
st.set_page_config(page_title="WithMember AI 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; font-weight: bold; }
    label { color: #D4AF37 !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1E1E1E; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 WithMember AI 리뷰 마스터")

# API 키 등록 (Secrets 우선 확인)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key 등록", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    with st.form("review_form"):
        st.subheader("📝 플레이어 입력")
        store_name = st.text_input("그 이름", placeholder="예: 동경생고기")
        keywords = st.text_area("핵심 키워드", placeholder="예: 대구 장기동 육회, 신선함, 친절한 분위기")
        submitted = st.form_submit_button("리뷰 작성하기")

    if submitted:
        if not store_name or not keywords:
            st.warning("매장 이름과 키워드를 모두 입력해 주세요.")
        else:
            with st.spinner("전문 마케터의 시선으로 블로그 리뷰를 작성 중입니다..."):
                try:
                    # 🚨 에러 해결의 핵심: 가장 호환성이 높은 안정적인 모델로 고정
                    model = genai.GenerativeModel('gemini-pro')
                    
                    prompt = f"""
                    너는 마케팅 대행사 '위드멤버'의 수석 카피라이터야.
                    매장명 '{store_name}'에 대한 네이버 블로그 리뷰 초안을 작성해줘.
                    반드시 포함할 키워드: {keywords}
                    
                    [작성 조건]
                    1. 글은 사람(20~30대)이 직접 다녀온 것처럼 자연스럽고 친근한 말투로 써줘.
                    2. 서론-본론-결론 구조를 갖추고 이모지를 적절히 사용해줘.
                    3. 글에서 AI가 쓴 것 같은 어색한 번역투나 딱딱한 문장은 절대 쓰지 마.
                    """
                    response = model.generate_content(prompt)
                    
                    st.success("리뷰 초안 작성 완료! 🟢")
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI 응답 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 등록해 주세요.")
