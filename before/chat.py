import streamlit as st
from dotenv import load_dotenv
from llm import get_ai_response



# 기본 설정
st.set_page_config(layout="wide", page_title="Tune Wizard")

load_dotenv()

# 페이지 전체 레이아웃 구성
with st.sidebar:
    st.markdown("## 🎵 Tune Wizard")
    st.image("logo.jpg", width=100)  # 로고 위치 (파일 필요 시 same folder)

    st.markdown("### Prompt")
    st.button("Make Prompt")
    st.button("Chat Window")

    st.markdown("### Log")
    st.button("Prompt History")
    st.button("SQL History")

# 상단 바
st.markdown(
    """
    <div style="background-color:#60a5a3;padding:10px;height:50px;display:flex;justify-content:space-between;align-items:center;">
        <span style="color:white;font-size:20px;padding-left:10px;"></span>
        <div style="background-color:#4B5563;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
            <span style="color:white;font-size:24px;">☰</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 메인 컨텐츠 영역
st.set_page_config(page_title="튜닝마법사 챗봇", page_icon="🧙🏻")


st.title("🧙🏻 튜닝마법사 챗봇")
st.caption("튜닝마법사 챗봇은 Oracle SQL 튜닝에 대한 질문에 답변합니다.")

load_dotenv()

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if user_question := st.chat_input("튜닝마법사에게 튜닝할 SQL을 알려주세요."):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("답변을 생성하는 중입니다"):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
            st.session_state.message_list.append({"role": "ai", "content": ai_message})