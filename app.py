import streamlit as st
import google.generativeai as genai

# 1. 페이지 스타일 (WithMember 블랙 & 골드)
st.set_page_config(page_title="WithMember AI 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; font-weight: bold; }
    label { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 WithMember AI 리뷰 마스터")

# 2. API 설정 및 모델 자동 찾기
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # [핵심] 사용 가능한 모델 목록을 가져와서 가장 적합한 것을 고릅니다.
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1.5 Flash -> 1.5 Pro -> Pro 순서로 우선순위를 둡니다.
        target_model = None
        for name in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if name in available_models:
                target_model = name
                break
        
        # 만약 위 이름들이 없다면 목록 중 첫 번째 모델을 선택합니다.
        if not target_model and available_models:
            target_model = available_models[0]

        if target_model:
            model = genai.GenerativeModel(target_model)
            # 사이드바에 현재 사용 중인 모델 표시 (확인용)
            st.sidebar.success(f"사용 모델: {target_model.split('/')[-1]}")
            
            with st.form("review_form"):
                st.subheader("📝 매장 정보 입력")
                store_name = st.text_input("매장 이름", placeholder="예: 동경생고기")
                visit_purpose = st.selectbox("방문 목적", ["데이트", "가족 모임", "회식", "친구와 방문"])
                keywords = st.text_area("핵심 키워드", placeholder="예: 대구 장기동 육회, 친절한 서비스")
                tone = st.radio("문체 선택", ["따뜻하게", "전문적으로", "내돈내산"])
                
                submitted = st.form_submit_button("리뷰 생성하기")

            if submitted:
                if not store_name or not keywords:
                    st.warning("정보를 입력해 주세요.")
                else:
                    with st.spinner("AI 에디터가 작성 중입니다..."):
                        try:
                            prompt = f"{store_name} 매장에 {visit_purpose}로 다녀온 블로그 리뷰를 써줘. 키워드는 {keywords}야. 말투는 {tone}로 해줘."
                            response = model.generate_content(prompt)
                            st.success("작성 완료! 🟢")
                            st.markdown("---")
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"생성 중 오류: {e}")
        else:
            st.error("사용 가능한 모델을 찾을 수 없습니다. API 키를 확인해 주세요.")

    except Exception as e:
        st.error(f"모델 목록을 가져오는 데 실패했습니다: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력하거나 Secrets에 등록해 주세요.")
