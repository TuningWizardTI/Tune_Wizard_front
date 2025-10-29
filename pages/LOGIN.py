# pages/0_로그인.py
import streamlit as st
from auth.session import login, logout, is_authenticated, touch_activity, current_user

hide_pages_style = """
<style>
/* 사이드바 네비게이션 목록 중 특정 페이지 숨기기 */
[data-testid="stSidebarNav"] ul li a[href$="SIGNUP"] {
    display: none;
}
[data-testid="stSidebarNav"] ul li a[href$="LOGIN"] {
    display: none;
}
</style>
"""

st.markdown(hide_pages_style, unsafe_allow_html=True)

st.set_page_config(page_title="로그인", page_icon="🔐", layout="centered")

st.title("🔐 로그인")
st.caption("튜닝 마법사 로그인 페이지 입니다.")

if is_authenticated():
    user = current_user()
    st.success(f"이미 로그인됨: {st.session_state['auth']['user']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("메인으로 이동", use_container_width=True):
            touch_activity()
            st.switch_page("main.py")
    with col2:
        if st.button("로그아웃", use_container_width=True):
            logout(st.session_state['auth']['user'])
            st.rerun()
    st.stop()

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    submitted = st.form_submit_button("로그인")

if submitted:
    ok, err = login(username, password)
    if ok:
        st.success("로그인 성공!")
        st.switch_page("main.py")
    else:
        st.error(err or "로그인에 실패했습니다.")

st.divider()
st.caption("아직 계정이 없으신가요?")
st.page_link("pages/SIGNUP.py", label="회원가입 하러 가기", icon="📝")