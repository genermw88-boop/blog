import streamlit as st

# 최상단에서 라이브러리 설치 여부 먼저 확인
try:
    import google.generativeai as genai
    LIB_INSTALLED = True
except ImportError:
    LIB_INSTALLED = False

# 페이지 스타일 설정
st.set_page_config(page_title="WithMember AI 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; font-weight: bold; }
    label { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 WithMember AI 리뷰 마스터")

if not LIB_INSTALLED:
    st.error("시스템 오류: 라이브러리가 설치되지 않았습니다. requirements.txt 파일을 확인해 주세요.")
else:
    # API 키 등록
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key 등록", type="password")

    if api_key:
        # 상태 표시
        st.sidebar.success("API 키 등록 완료 🟢")
        genai.configure(api_key=api_key)
        
        with st.form("review_form"):
            st.subheader("📝 매장 정보 입력")
            store_name = st.text_input("매장 이름")
            keywords = st.text_area("핵심 키워드")
            submitted = st.form_submit_button("리뷰 초안 생성하기")

        if submitted:
            if not store_name or not keywords:
                st.warning("매장 이름과 키워드를 모두 입력해 주세요.")
            else:
                with st.spinner("AI가 꼼꼼하게 분석하여 작성 중입니다..."):
                    try:
                        # 가장 기본적이고 안정적인 모델 사용
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"{store_name} 매장에 대한 정성적인 블로그 리뷰를 작성해줘. 강조할 키워드는 {keywords}야."
                        response = model.generate_content(prompt)
                        
                        st.success("리뷰 초안 등록 완료 🟢")
                        st.markdown("---")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"AI API 연동 오류: {e}")
    else:
        st.info("왼쪽 사이드바에 API 키를 등록해 주세요.")
