import streamlit as st
import google.generativeai as genai

# 1. 페이지 스타일 설정 (블랙 & 골드 + 하얀색 입력창)
st.set_page_config(page_title="WithMember AI 마스터", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #D4AF37; }
    div.stButton > button:first-child { background-color: #D4AF37; color: black; border: None; font-weight: bold; }
    label { color: #D4AF37 !important; }
    /* 입력창 하얀색 고정 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #FFFFFF !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 WithMember AI 리뷰 마스터")

# 2. API 키 시스템 연동
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key 등록", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            st.error("현재 등록된 API 키에 연결된 모델이 없습니다.")
        else:
            target_model = None
            for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                if preferred in available_models:
                    target_model = preferred
                    break
            
            if not target_model:
                target_model = available_models[0]

            st.success("AI 시스템 연동 완료 🟢")
            
            with st.form("review_form"):
                st.subheader("📝 플레이어 정보 등록")
                store_region = st.text_input("매장 지역", placeholder="예: 대구 달서구 장기동")
                store_name = st.text_input("매장명", placeholder="예: 동경생고기")
                place_link = st.text_input("플레이스 링크", placeholder="예: https://map.naver.com/v5/...")
                main_keywords = st.text_input("메인 키워드 (제목용, 2개 권장)", placeholder="예: 대구 장기동 맛집, 장기동 육회")
                detail_keywords = st.text_area("상세 키워드 (본문용, 5개 권장)", placeholder="예: 당일 도축, 신선함, 친절한 사장님, 주차 편리, 프라이빗 룸")
                
                submitted = st.form_submit_button("리뷰 데이터 등록")

            if submitted:
                if not store_region or not store_name or not place_link or not main_keywords or not detail_keywords:
                    st.warning("매장 지역, 매장명, 플레이스 링크, 메인/상세 키워드를 모두 등록해 주세요.")
                else:
                    with st.spinner("자연스러운 말투로 리뷰를 작성 중입니다..."):
                        try:
                            model = genai.GenerativeModel(target_model)
                            prompt = f"""
                            너는 평소 맛집과 핫플을 즐겨 찾는 20~30대 네이버 블로거야.
                            아래 정보를 바탕으로 직접 다녀온 것처럼 생생하고 자연스러운 네이버 블로그 리뷰 초안을 작성해줘.
                            
                            [정보]
                            - 매장 지역: {store_region}
                            - 매장명: {store_name}
                            - 플레이스 링크: {place_link}
                            - 메인 키워드 (반드시 제목에 포함): {main_keywords}
                            - 상세 키워드 (반드시 본문에 자연스럽게 포함): {detail_keywords}
                            
                            [작성 조건]
                            1. 제목: '{main_keywords}'를 포함하여 사람들의 눈길을 끄는 제목 1개를 최상단에 제시해.
                            2. 본문: 기계적인 AI 느낌은 완전히 빼고, 친하고 편안한 말투로 자연스럽게 작성해. 
                                     글 중간이나 끝부분에 '매장 지역({store_region})'의 위치 정보와 '플레이스 링크({place_link})'를 자연스럽게 소개해줘.
                            3. 구성: 서론-본론-결론의 구조를 갖추고, 가독성을 위해 적절한 이모지를 섞어줘.
                            4. 제한: 글씨를 굵게 만드는 마크다운 기호(**)는 절대 사용하지 마. 특수기호 없이 깔끔한 텍스트로만 출력해.
                            5. 해시태그: 리뷰가 모두 끝난 맨 마지막 줄에 메인 키워드와 상세 키워드 단어들을 활용해서 '#키워드' 형태로 전부 나열해줘.
                            """
                            response = model.generate_content(prompt)
                            
                            # 🚨 추가: AI가 혹시라도 ** 기호를 썼다면 파이썬이 강제로 싹 지워버립니다.
                            clean_text = response.text.replace("**", "")
                            
                            st.success("리뷰 데이터 등록 완료 🟢")
                            st.markdown("---")
                            
                            st.text_area("✨ 완성된 리뷰 (박스 안쪽을 클릭하고 전체 복사하세요)", value=clean_text, height=500)
                            
                        except Exception as e:
                            st.error(f"리뷰 등록 중 오류가 발생했습니다: {e}")
    except Exception as e:
        st.error(f"API 연결 초기화 중 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 등록해 주세요.")
