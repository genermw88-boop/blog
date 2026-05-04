import streamlit as st
import google.generativeai as genai

# 1. 페이지 스타일 및 설정 (WithMember 스타일)
st.set_page_config(page_title="WithMember AI 리뷰 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; }
    </style>
    """, unsafe_allow_html=True)  # <--- 이 부분이 수정되었습니다!

st.title("🏆 AI 블로그 리뷰 마스터")

# 2. API 키 '등록' 확인 로직
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key 등록", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        with st.form("review_form"):
            st.subheader("📝 매장 정보 입력")
            store_name = st.text_input("매장 이름", placeholder="예: WithMember 식당")
            visit_purpose = st.selectbox("방문 목적", ["데이트", "가족 모임", "회식", "친구와 방문"])
            keywords = st.text_area("핵심 키워드", placeholder="예: 친절함, 인테리어 고급짐, 주차 가능")
            tone = st.radio("문체 선택", ["따뜻하고 친절하게", "전문적이고 신뢰감 있게", "내돈내산 스타일"])
            
            submitted = st.form_submit_button("리뷰 생성하기")

        if submitted:
            if not store_name or not keywords:
                st.warning("모든 정보를 입력해 주세요.")
            else:
                with st.spinner("AI가 따뜻한 목소리로 리뷰를 작성 중입니다..."):
                    try:
                        prompt = f"""
                        너는 아주 따뜻하고 친근한 말투를 가진 전문 블로거야. 
                        매장 '{store_name}'에 '{visit_purpose}' 목적으로 다녀온 리뷰를 써줘.
                        포함할 키워드: {keywords}
                        전체적인 분위기: {tone}
                        
                        네이버 블로그 형식에 맞춰서 이모지도 적절히 섞어주고, 
                        사람이 쓴 것처럼 자연스럽게 작성해줘.
                        """
                        response = model.generate_content(prompt)
                        st.success("리뷰 작성이 완료되었습니다!")
                        st.markdown("---")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"리뷰 생성 중 오류가 발생했습니다: {e}")

    except Exception as e:
        st.error(f"시스템 설정 중 오류 발생: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 등록하거나 Streamlit Secrets를 설정해 주세요.")
