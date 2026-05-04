import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 페이지 스타일 설정 (위드멤버 스타일)
st.set_page_config(page_title="WithMember AI 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; font-weight: bold; }
    label { color: #D4AF37 !important; }
    /* 🚨 수정: 입력창 배경을 하얀색으로, 글씨를 검은색으로 변경 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #FFFFFF !important; color: #000000 !important; }
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
            for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                if preferred in available_models:
                    target_model = preferred
                    break
            
            if not target_model:
                target_model = available_models[0]

            st.success(f"AI 시스템 연동 완료 🟢")
            
            with st.form("review_form"):
                st.subheader("📝 플레이어 정보 등록")
                store_name = st.text_input("매장명", placeholder="예: 동경생고기")
                
                main_keywords = st.text_input("메인 키워드 (제목용, 2개 권장)", placeholder="예: 대구 장기동 맛집, 장기동 육회")
                detail_keywords = st.text_area("상세 키워드 (본문용, 5개 권장)", placeholder="예: 당일 도축, 신선함, 친절한 사장님, 주차 편리, 프라이빗 룸")
                
                # 🚨 수정: 사진을 여러 장 등록할 수 있도록 설정
                uploaded_files = st.file_uploader("매장/음식 사진 등록 (선택, 여러 장 가능)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
                
                submitted = st.form_submit_button("리뷰 데이터 등록하기")

            if submitted:
                if not store_name or not main_keywords or not detail_keywords:
                    st.warning("매장명, 메인 키워드, 상세 키워드를 모두 등록해 주세요.")
                else:
                    with st.spinner("사진과 키워드를 꼼꼼히 분석하여 리뷰를 작성 중입니다..."):
                        try:
                            model = genai.GenerativeModel(target_model)
                            
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
                            
                            # 사진이 등록되었을 경우의 로직
                            if uploaded_files:
                                imgs = [Image.open(f) for f in uploaded_files]
                                photo_count = len(imgs)
                                
                                # AI에게 사진 위치를 지정하도록 명령
                                prompt += f"""
                                4. 첨부된 사진 {photo_count}장을 모두 분석해서 글에 생생하게 녹여내줘. 
                                5. 가장 중요한 규칙: 글을 작성하면서 사진이 들어갈 가장 자연스러운 문단과 문단 사이마다 정확히 '[사진 등록 위치]' 라는 태그를 적어줘. 이 태그는 전체 글에서 딱 {photo_count}번만 나타나야 해.
                                """
                                response = model.generate_content([prompt] + imgs)
                                
                                st.success("리뷰 데이터 등록 완료 🟢")
                                st.markdown("---")
                                
                                # '[사진 등록 위치]' 태그를 기준으로 텍스트를 조각내서 이미지와 번갈아 출력
                                text_parts = response.text.split("[사진 등록 위치]")
                                
                                for i in range(len(text_parts)):
                                    # 텍스트 출력
                                    st.write(text_parts[i])
                                    # 사진이 남아있다면 텍스트 아래에 사진 출력
                                    if i < len(imgs):
                                        st.image(imgs[i], use_container_width=True)

                            # 사진이 없을 경우의 로직
                            else:
                                response = model.generate_content(prompt)
                                st.success("리뷰 데이터 등록 완료 🟢")
                                st.markdown("---")
                                st.write(response.text)
                            
                        except Exception as e:
                            st.error(f"리뷰 등록 중 오류가 발생했습니다: {e}")
    except Exception as e:
        st.error(f"API 연결 초기화 중 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 등록해 주세요.")
