import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="WithMember AI 리뷰 생성기", layout="centered")
st.title("✍️ AI 블로그 리뷰 생성기")

# API 키 입력 (사이드바 혹은 Streamlit Secrets 사용)
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    with st.form("review_form"):
        store_name = st.text_input("매장 이름", placeholder="예: 구름카페 성수점")
        visit_purpose = st.selectbox("방문 목적", ["데이트", "가족 모임", "회식", "혼밥", "친구와 방문"])
        keywords = st.text_area("핵심 키워드", placeholder="예: 친절함, 주차 편함, 시그니처 라떼")
        tone = st.radio("문체", ["발랄하게", "차분하게", "내돈내산 스타일"])
        
        submitted = st.form_submit_button("리뷰 생성")

    if submitted:
        if not store_name or not keywords:
            st.error("정보를 모두 입력해주세요.")
        else:
            with st.spinner("작성 중..."):
                prompt = f"너는 블로거야. {store_name} 방문 리뷰를 {visit_purpose} 목적으로, {keywords} 키워드를 넣어 {tone} 말투로 네이버 블로그 형식으로 써줘. 이모지도 섞어줘."
                response = model.generate_content(prompt)
                st.subheader("✅ 완성된 리뷰")
                st.write(response.text)
else:
    st.info("왼쪽 사이드바에 Gemini API Key를 입력해주세요.")