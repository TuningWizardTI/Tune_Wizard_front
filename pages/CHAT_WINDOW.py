import streamlit as st
import requests
import os

# 페이지 설정
st.set_page_config(page_title="튜닝마법사 챗봇", page_icon="🧙🏻")

# 환경변수 로드
API_URL = "http://localhost:8080/api/v1/chatGPT/callPrompt"
API_TABLE_URL = "http://localhost:8080/api/v1/chatGPT/tableList"

# Content Type이 정상적으로 세팅되는 현상 해결
headers = {
    "Content-Type":"application/json"
}

# 화면 그리기
st.title("🧙🏻 튜닝마법사 챗봇")
st.caption("튜닝마법사 챗봇은 Oracle SQL 튜닝에 대한 질문에 답변합니다.")

# 테이블 목록을 가져와 테이블 선택이 가능하게 하는 Select Box생성
# Call TABLE List
try:
    table_response = requests.post(API_TABLE_URL, headers)
    table_response.raise_for_status()
    table_options = table_response.json()  # 응답 JSON에서 'tables' 키 값 추출
    if not table_options:  # 빈 배열이면 기본 옵션
        table_options = ["SQL 튜닝", "힌트 설명", "실행계획 분석"]
except Exception as e:
    st.warning(f"테이블 목록을 불러오지 못했습니다: {e}")
    table_options = ["SQL 튜닝", "힌트 설명", "실행계획 분석"]
table_options.append("기타")

st.caption("👇 사용할 테이블을 선택한 후 질문을 입력하세요.")
table_name = st.selectbox(
    "보낼 테이블을 선택하세요",
    table_options,
    index=0
)
if table_name == "기타" :
    table_name = "none"

# 채팅 기록 저장용 세션 상태 초기화
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# 채팅 기록 출력
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])



# 💬 하단 입력창 위에 selectbox 배치 (하단 고정처럼 보이게)

  # 시각적 구분선
user_question = st.chat_input("튜닝마법사에게 튜닝할 SQL을 알려주세요.")


# 📥 chat_input은 항상 하단에 고정됨
if user_question :
    # CLEAR 명령어 처리
    if user_question.strip().lower() == "clear" or user_question.strip().lower() == "/clear":
        st.session_state.message_list.clear()
        with st.chat_message("ai"):
            st.write("💬 대화가 초기화되었습니다.")
        st.stop()

    with st.chat_message("user"):
        st.write(f"**[{table_name}]** {user_question}")
    st.session_state.message_list.append({"role": "user", "content": f"[{table_name}] {user_question}"})

    with st.spinner("답변을 생성하는 중입니다..."):
        try:
            json={"query": user_question, "table": table_name}
            print(json)
            response = requests.post(API_URL,  headers=headers, json=json)
            response.raise_for_status()
            ai_answer = response.json().get("answer", "답변을 받아오지 못했습니다.")
        except Exception as e:
            ai_answer = f"API 호출 실패: {e}"

        with st.chat_message("ai"):
            st.write(ai_answer)
        st.session_state.message_list.append({"role": "ai", "content": ai_answer})