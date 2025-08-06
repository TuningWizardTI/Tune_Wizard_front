import streamlit as st
import requests
from dotenv import load_dotenv
import os

# 페이지 설정
st.set_page_config(page_title="튜닝마법사 챗봇", page_icon="🧙🏻")

# 환경변수 로드
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8080/api/v1/chatGPT/flask")
API_TABLE_URL = os.getenv("TABLE_URL", "http://localhost:8080/api/v1/chatGPT/tableList")

st.title("🧙🏻 튜닝마법사 챗봇")
st.caption("튜닝마법사 챗봇은 Oracle SQL 튜닝에 대한 질문에 답변합니다.")

try:
    table_response = requests.post(API_TABLE_URL)
    table_response.raise_for_status()
    print(table_response)
    table_options = table_response.json()  # 응답 JSON에서 'tables' 키 값 추출
    if not table_options:  # 빈 배열이면 기본 옵션
        table_options = ["SQL 튜닝", "힌트 설명", "실행계획 분석"]
except Exception as e:
    st.warning(f"테이블 목록을 불러오지 못했습니다: {e}")
    table_options = ["SQL 튜닝", "힌트 설명", "실행계획 분석"]

# 채팅 기록 저장용 세션 상태 초기화
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# 채팅 기록 출력
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 💬 하단 입력창 위에 selectbox 배치 (하단 고정처럼 보이게)
query_type = st.selectbox(
    "보낼 테이블을 선택하세요",
    table_options,
    index=0
)

# 📥 chat_input은 항상 하단에 고정됨
if user_question := st.chat_input("튜닝마법사에게 튜닝할 SQL을 알려주세요."):
    with st.chat_message("user"):
        st.write(f"**[{query_type}]** {user_question}")
    st.session_state.message_list.append({"role": "user", "content": f"[{query_type}] {user_question}"})

    with st.spinner("답변을 생성하는 중입니다..."):
        try:
            response = requests.post(API_URL, json={"query": user_question, "type": query_type})
            response.raise_for_status()
            ai_answer = response.json().get("answer", "답변을 받아오지 못했습니다.")
        except Exception as e:
            ai_answer = f"API 호출 실패: {e}"

        with st.chat_message("ai"):
            st.write(ai_answer)
        st.session_state.message_list.append({"role": "ai", "content": ai_answer})