# pages/1_회원가입.py
import re
import streamlit as st
from auth.session import signup, is_authenticated

st.set_page_config(page_title="SIGN UP", page_icon="📝", layout="centered")

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

st.title("📝 SIGN UP")
st.caption("튜닝 마법사 사용을 위한 계정을 생성합니다.")

if is_authenticated():
    st.info("이미 로그인 상태입니다. 로그아웃 후 다시 시도하세요.")
    st.page_link("login/LOGIN.py", label="로그인 페이지로 이동", icon="🔐")
    st.stop()

USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,20}$")

with st.form("signup_form", clear_on_submit=False):
    userId = st.text_input("아이디", placeholder="영문/숫자/._- (3~20자)")
    displayName = st.text_input("표시 이름", placeholder="예: 홍길동")
    pwd = st.text_input("비밀번호", type="password", placeholder="최소 8자")
    pwd2 = st.text_input("비밀번호 확인", type="password", placeholder="다시 입력")
    submitted = st.form_submit_button("회원가입")

if submitted:
    if not USERNAME_RE.match(userId or ""):
        st.error("아이디 형식이 올바르지 않습니다. 영문/숫자/._- 만 허용, 3~20자.")
    elif not displayName:
        st.error("표시 이름을 입력하세요.")
    elif len(pwd or "") < 8:
        st.error("비밀번호는 최소 8자 이상이어야 합니다.")
    elif pwd != pwd2:
        st.error("비밀번호 확인이 일치하지 않습니다.")
    else:
        ok, err = signup(userId.strip(), pwd, displayName.strip())
        if ok:
            st.success("회원가입이 완료되었습니다! 이제 로그인하세요.")
            st.page_link("pages/LOGIN.py", label="로그인 하러 가기", icon="🔐")
        else:
            st.error(err or "회원가입에 실패했습니다.")