import streamlit as st
from auth.session import require_auth, touch_activity, current_user, logout, API_URL

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

st.set_page_config(page_title="Tune Wizard", layout="wide")

require_auth()
touch_activity()


st.markdown(
    "<h2>Welcome to Tune Wizard 👋</h2><p>Select a feature from the sidebar.</p>",
    unsafe_allow_html=True
)
 
# ✅ 현재 로그인 사용자 (백엔드에서 인증 완료 후 로그인할 때 session에 보관해둔 값)
#user = current_user() or {}
userId = st.session_state['auth']['user']  # ← 여기서 아이디를 얻습니다.
name = st.session_state['auth']['userName']


# 사이드바에 로그인 사용자 표시 (선택)
with st.sidebar:
    st.markdown("### 👤 로그인 정보")
    st.write(f"아이디: **{userId or '-'}**")
    st.write(f"사용자이름: **{name or '-'}**")

if st.sidebar.button("로그아웃"):
    logout(userid)
    st.rerun()


