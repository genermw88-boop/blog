import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 (블랙 & 골드 스타일)
st.set_page_config(page_title="WithMember AI 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; font-weight: bold; }
    label { color: #D4AF37 !important; }
    .stSelectbox, .stTextInput, .stTextArea { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 WithMember AI 리뷰 마스터")

# 2. API 키 및 모델 설정
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key 등록", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 모델 이름을 시도할 리스트 (가장 최신순)
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        # 작동하는 모델을 자동으로 찾아 설정
        selected_model = None
        for name in model_names:
            try:
                test_model = genai.GenerativeModel(name)
                # 가벼운 테스트 호출로 확인
                selected_model = test_model
                break
            except:
                continue

        if not selected_model:
            st.error("사용 가능한 AI 모델을 찾을 수 없습니다. API 키를 다시 확인해 주세요.")
        else:
            with st.form("review_form"):
                st.subheader("📝 매장 정보 입력")
                store_name = st.text_input("매장 이름", placeholder="예: 동경생고기")
                visit_purpose = st.selectbox("방문 목적", ["데이트", "가족 모임", "회식", "친구와 방문"])
                keywords = st.text_area("핵심 키워드", placeholder="예: 대구 장기동 육회, 친절한 서비스")
                tone = st.radio("문체 선택", ["따뜻하고 친절하게", "전문적이고 신뢰감 있게", "내돈내산 스타일"])
                
                submitted = st.form_submit_button("리뷰 생성하기")

            if submitted:
                if not store_name or not keywords:
                    st.warning("정보를 모두 입력해 주세요.")
                else:
                    with st.spinner("전문 마케터의 시선으로 작성 중입니다..."):
                        try:
                            prompt = f"""
                            너는 전문 마케팅 대행사 'WithMember'의 AI 콘텐츠 에디터야.
                            매장 '{store_name}'에 '{visit_purpose}' 목적으로 방문한 자연스러운 블로그 리뷰를 작성해줘.
                            포함할 키워드: {keywords}
                            말투: {tone} (사람이 쓴 것처럼 따뜻하고 자연스럽게)
                            
                            [구성 가이드]
                            1. 눈길을 끄는 제목 1개
                            2. 서론-본론-결론 구조
                            3. 이모지를 적절히 섞어서 생동감 있게
                            """
                            response = selected_model.generate_content(prompt)
                            st.success("리뷰 작성이 완료되었습니다! 🟢")
                            st.markdown("---")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"생성 실패: {e}")

    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력하거나 Secrets에 등록해 주세요.")
