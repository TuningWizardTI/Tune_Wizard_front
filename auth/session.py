# auth/session.py
import os
from datetime import datetime, timedelta, timezone
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")

# 엔드포인트(백엔드 실제 경로에 맞게 수정)
REGISTER_ENDPOINT = f"{API_URL}/api/v1/chatGPT/sighupTuneWizard"  # POST {username, password, displayName}
LOGIN_ENDPOINT    = f"{API_URL}/api/v1/chatGPT/loginTuneWizard"     # POST {username, password}
LOGOUT_ENDPOINT   = f"{API_URL}/api/v1/chatGPT/logoutTuneWizard"    # POST/GET (서버 세션 무효화)

INACTIVITY_LIMIT_MIN = 30  # 무활동 자동 로그아웃 시간

def _now_utc():
    return datetime.now(timezone.utc)

def _init_state():
    if "auth" not in st.session_state:
        st.session_state["auth"] = None  # {"user": {...}, "loginAt": iso}
    if "last_activity_utc" not in st.session_state:
        st.session_state["last_activity_utc"] = _now_utc()
    # 백엔드 쿠키(JSESSIONID 등)를 보존할 세션
    if "http" not in st.session_state:
        st.session_state["http"] = requests.Session()

def _clear_auth():
    st.session_state["auth"] = None
    st.session_state["last_activity_utc"] = _now_utc()
    # 쿠키도 정리하고 싶으면 주석 해제
    # st.session_state["http"] = requests.Session()

def is_authenticated() -> bool:
    _init_state()
    auth = st.session_state.get("auth")
    if not auth:
        return False
    last = st.session_state.get("last_activity_utc", _now_utc())
    if (_now_utc() - last) > timedelta(minutes=INACTIVITY_LIMIT_MIN):
        _clear_auth()
        return False
    return True

def touch_activity():
    _init_state()
    st.session_state["last_activity_utc"] = _now_utc()

def current_user() -> dict | None:
    if not is_authenticated():
        return None
    return st.session_state["auth"]["user"]

# ---------------------------
# 백엔드 연동 함수
# ---------------------------

def signup(userId: str, password: str, displayName: str) -> tuple[bool, str | None]:
    """
    회원가입: 백엔드로 위임. 성공 시 True.
    백엔드 응답(예시):
      201 Created, body: {"id":1,"username":"foo","displayName":"홍길동","roles":["USER"]}
      409 Conflict (중복) 등
    """
    _init_state()
    if not API_URL:
        return False, "API_URL 환경변수가 설정되어 있지 않습니다."
    if not userId or not password or not displayName:
        return False, "아이디/비밀번호/표시이름을 모두 입력하세요."

    try:
        r = st.session_state["http"].post(
            REGISTER_ENDPOINT,
            json={
              "userId": userId
            , "password": password
            , "userName": displayName
            , "loginStatus": "N"
            },
            timeout=10,
        )
        if r.status_code in (200, 201):
            return True, None
        elif r.status_code == 409:
            return False, "이미 존재하는 아이디입니다."
        elif r.status_code == 400:
            # 백엔드가 검증 메시지를 내려주면 표시
            msg = r.json().get("message") if r.headers.get("content-type","").startswith("application/json") else None
            return False, msg or "요청 형식이 올바르지 않습니다."
        else:
            return False, f"회원가입 실패 (HTTP {r.status_code})"
    except requests.RequestException as e:
        return False, f"네트워크 오류: {e}"

def login(userId: str, password: str) -> tuple[bool, str | None]:
    """
    로그인: 백엔드로 검증 위임. 성공 시 사용자 정보를 세션에 저장.
    백엔드 응답(예시):
      200 OK, body: {"user":{"username":"foo","displayName":"홍길동","roles":["USER"]}}
      (쿠키 세션이 있다면 Set-Cookie 포함 → requests.Session이 자동 보관)
    """
    _init_state()
    if not API_URL:
        return False, "API_URL 환경변수가 설정되어 있지 않습니다."
    if not userId or not password:
        return False, "아이디와 비밀번호를 입력하세요."
    print(userId + ", " + password)

    try:
        r = st.session_state["http"].post(
            LOGIN_ENDPOINT,
            json={"userId": userId, "password": password},
            timeout=10,
        )
        print(r.json())
        if r.json()['result']['response'] == '200':
            data = r.json() 
            user = r.json()['result']['userId']
            name = r.json()['result']['userName']
            print(user)
            st.session_state["auth"] = {"user": user, "loginAt": _now_utc().isoformat(), "userName" : name}
            touch_activity()
            return True, None
        elif r.json()['result']['response'] in ('401', '403'):
            return False, "아이디 또는 비밀번호가 올바르지 않습니다."
        else:
            return False, f"로그인 실패 (HTTP {r.response})"
    except requests.RequestException as e:
        return False, f"네트워크 오류: {e}"

def logout(userId: str):
    """
    로그아웃: 서버 세션이 있다면 무효화 요청 후 로컬 세션 정리.
    """
    _init_state()
    try:
        r = st.session_state["http"].post(
            LOGOUT_ENDPOINT,
            json={"userId": userId},
            timeout=10,
        )
        print(r.json())
        if r.json()['result']['response'] == '200':
             _clear_auth()
    except requests.RequestException:
        pass
   

def require_auth(roles: list[str] | None = None):
    if not is_authenticated():
        st.warning("로그인이 필요한 페이지 입니다.")
        #st.page_link("./LOGIN.py", label="로그인 페이지로 이동", icon="🔐")
        st.page_link("pages/LOGIN.py", label="로그인 페이지로 이동", icon="🔐")
        st.stop()

    if roles:
        user_roles = set(st.session_state["auth"]["user"].get("roles", []))
        if not set(roles).issubset(user_roles):
            st.error("접근 권한이 없습니다.")
            st.stop()