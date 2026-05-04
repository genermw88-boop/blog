import streamlit as st
import google.generativeai as genai
from PIL import Image # 이미지 처리를 위한 필수 라이브러리 추가

# 1. 페이지 스타일 설정 (위드멤버 스타일)
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

# 2. API 키 등록 (Secrets 우선 확인)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key 등록", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            st.error("현재 발급받으신 API 키에 연결된 AI 모델이 없습니다.")
        else:
            target_model = None
            # 이미지 분석 능력이 뛰어난 1.5 버전을 최우선으로 잡습니다.
            for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                if preferred in available_models:
                    target_model = preferred
                    break
            
            if not target_model:
                target_model = available_models[0]

            st.success(f"AI 시스템 연동 완료 🟢 (모델: {target_model.split('/')[-1]})")
            
            with st.form("review_form"):
                st.subheader("📝 플레이어 정보 등록")
                store_name = st.text_input("매장명", placeholder="예: 동경생고기")
                
                # 키워드 입력 세분화
                main_keywords = st.text_input("메인 키워드 (제목용, 2개 권장)", placeholder="예: 대구 장기동 맛집, 장기동 육회")
                detail_keywords = st.text_area("상세 키워드 (본문용, 5개 권장)", placeholder="예: 당일 도축, 신선함, 친절한 사장님, 주차 편리, 프라이빗 룸")
                
                # 이미지 등록 기능 추가
                uploaded_file = st.file_uploader("매장/음식 사진 등록 (선택)", type=["jpg", "jpeg", "png"])
                
                submitted = st.form_submit_button("리뷰 초안 등록하기")

            if submitted:
                if not store_name or not main_keywords or not detail_keywords:
                    st.warning("매장명, 메인 키워드, 상세 키워드를 모두 등록해 주세요.")
                else:
                    with st.spinner("사진과 키워드를 분석하여 리뷰를 작성 중입니다..."):
                        try:
                            model = genai.GenerativeModel(target_model)
                            
                            # 자연스러운 사람의 말투를 강조한 프롬프트
                            prompt = f"""
                            너는 마케팅 대행사 '위드멤버'의 수석 카피라이터야.
                            아래 정보를 바탕으로 네이버 블로그 리뷰 초안을 작성해줘.
                            
                            [정보]
                            - 매장명: {store_name}
                            - 메인 키워드 (반드시 제목에 포함): {main_keywords}
                            - 상세 키워드 (반드시 본문에 자연스럽게 포함): {detail_keywords}
                            
                            [작성 조건]
                            1. 제목: '{main_keywords}'를 포함하여 클릭을 유도하는 매력적인 제목 1개를 최상단에 제시해.
                            2. 본문: 사람(20~30대)이 직접 다녀온 것처럼 매우 자연스럽고 따뜻한 말투로 작성해. 기계적이거나 어색한 AI 번역투는 절대 금지야.
                            3. 구성: 서론-본론-결론의 구조를 갖추고, 문단 사이에 적절히 이모지를 섞어 가독성을 높여.
                            """
                            
                            # 사진이 등록되었을 경우 AI에게 사진 분석 지시 추가
                            if uploaded_file is not None:
                                img = Image.open(uploaded_file)
                                prompt += "\n4. 첨부된 사진을 꼼꼼히 분석해서, 사진에 보이는 음식의 질감이나 매장의 특징을 글에 아주 생생하고 자연스럽게 녹여내줘."
                                response = model.generate_content([prompt, img])
                            else:
                                response = model.generate_content(prompt)
                            
                            st.success("리뷰 데이터 등록 완료 🟢")
                            st.markdown("---")
                            
                            # 분석이 끝난 후 화면에 이미지 출력
                            if uploaded_file is not None:
                                st.image(img, caption="등록된 기준 사진", use_container_width=True)
                            
                            st.write(response.text)
                            
                        except Exception as e:
                            st.error(f"리뷰 등록 중 오류가 발생했습니다: {e}")
    except Exception as e:
        st.error(f"API 연결 초기화 중 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 등록해 주세요.")
