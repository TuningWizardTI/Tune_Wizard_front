import streamlit as st
import requests

st.set_page_config(page_title="API 호출 예제", layout="wide")
st.title("🌐 API 호출 데모")

# 사용자 입력
st.subheader("🔧 요청 파라미터 입력")
user_input = st.text_input("검색어 또는 요청 데이터", "SQL 튜닝")

# API 엔드포인트 입력 (예: Flask API, FastAPI, 외부 API) st.text_input("API 주소", "https://api.example.com/tune")
api_url = "http://localhost:8080/api/v1/chatGPT/flask"

# 버튼 클릭 시 API 요청
if st.button("🚀 API 호출"):
    try:
        with st.spinner("API 요청 중..."):
            # 예시: POST 요청
            response = requests.post(api_url, json={"query": user_input})
            response.raise_for_status()

            result = response.json()
            st.success("✅ 응답 수신 완료")
            st.subheader("📨 API 응답:")
            st.json(result)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 오류 발생: {e}")