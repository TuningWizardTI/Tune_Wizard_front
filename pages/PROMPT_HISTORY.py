import os
import requests
import streamlit as st
import pandas as pd
import datetime

# ✅ 추가: 인증 유틸에서 현재 사용자 정보/가드 가져오기
from auth.session import require_auth, touch_activity, current_user

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

# ✅ 로그인 가드 + 활동 갱신
require_auth()
touch_activity()

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="🧙🏻 튜닝마법사 - 프롬프트 이력", layout="wide")

# -----------------------------
# Environment & constants
# -----------------------------
API_BASE = os.getenv("API_URL", "http://localhost:8080/api/v1/chatGPT/promptHistory")
DATE_FMT = "%Y-%m-%d %H:%M:%S"

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
    logout()
    st.rerun()


# -----------------------------
# Utilities
# -----------------------------
class ApiError(RuntimeError):
    pass

def _post(url: str, json_data: dict | None = None):
    try:
        r = requests.post(url, json=json_data, timeout=20)
        if r.status_code >= 400:
            raise ApiError(f"POST {url} failed: {r.status_code} {r.text}")
        return r.json()
    except requests.RequestException as e:
        raise ApiError(str(e)) from e


def _human_dt(ts_str):
    if not ts_str:
        return ""
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]:
        try:
            dt = datetime.strptime(ts_str, fmt)
            return dt.strftime(DATE_FMT)
        except Exception:
            pass
    return str(ts_str)

# -----------------------------
# API wrappers (PROMPT_HISTORY only)
# -----------------------------
# Expecting endpoints:
#   GET /history?limit&offset                -> list
#   GET /history/{uuid}                      -> detail
# Adjust if your backend path differs.

def fetch_history(limit: int = 100, offset: int = 0):
    url = f"{API_BASE}"
    user_id = st.session_state.get("auth", {}).get("user")  # 로그인한 사용자 ID
    payload = {
        "user_id": userId
    }
    return _post(url, payload)

def fetch_history_detail(uuid: str):
    url = f"{API_BASE}/history/{uuid}"
    payload = {
        "user_id": userId
    }

    return _post(url, payload)

# -----------------------------
# Sidebar / Filters
# -----------------------------
st.sidebar.title("📜 프롬프트 이력 필터")

col_f1, col_f2 = st.sidebar.columns(2)
limit_rows = col_f1.number_input("페이지 크기", min_value=10, max_value=500, value=100, step=10)
keyword = col_f2.text_input("키워드")

# -----------------------------
# Session state
# -----------------------------
if "history_offset" not in st.session_state:
    st.session_state.history_offset = 0
if "selected_uuid" not in st.session_state:
    st.session_state.selected_uuid = None

# -----------------------------
# Layout
# -----------------------------
st.title("🧙🏻 튜닝마법사 · 프롬프트 호출 이력")
st.caption("PROMPT_HISTORY 스키마(UUID, CLOB, VARCHAR2, DATE 문자열) 기준으로 목록 및 상세를 제공합니다.")

# Pagination controls
c1, c2, c3 = st.columns([1,1,1])
if c1.button("◀ 이전", use_container_width=True, disabled=st.session_state.history_offset == 0):
    st.session_state.history_offset = max(0, st.session_state.history_offset - limit_rows)
if c2.button("새로고침", use_container_width=True):
    pass
if c3.button("다음 ▶", use_container_width=True):
    st.session_state.history_offset += limit_rows

# Fetch
try:
    items = fetch_history(limit=limit_rows, offset=st.session_state.history_offset)
except ApiError as e:
    st.error(f"이력 조회 실패: {e}")
    items = []

if not isinstance(items, list):
    items = items.get("items", []) if isinstance(items, dict) else []

# Client-side keyword filtering (prompt/response)
if keyword:
    key = keyword.lower()
    def keep(row):
        pt = (row.get("promptText") or row.get("PROMPT_TEXT") or "").lower()
        rt = (row.get("responseText") or row.get("RESPONSE_TEXT") or "").lower()
        return key in pt or key in rt
    items = list(filter(keep, items))

if items:
    # Normalize rows for table display
    rows = []
    for it in items:
        rows.append(
            {
            "UUID": it.get("uuid") or it.get("UUID"),
            "MODEL_NAME": it.get("modelName") or it.get("MODEL_NAME"),
            "CALL_DATE": datetime.datetime.strptime(it.get("callDate"), '%Y%m%d').date() or datetime.datetime.strptime(it.get("CALL_DATE"), '%Y%m%d').date(),
            "CALL_TIME": datetime.datetime.strptime(it.get("callTime"), '%H%M%S').time() or datetime.datetime.strptime(it.get("CALL_TIME"), '%H%M%S').time()
            }
            )

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)

    # Selector by UUID
    uuids = [r["UUID"] for r in rows]
    default_idx = uuids.index(st.session_state.selected_uuid) if st.session_state.selected_uuid in uuids else (0 if uuids else None)
    sel_uuid = st.selectbox("결과 선택 (UUID)", options=uuids, index=default_idx if uuids else None, key="history_selector")
    st.session_state.selected_uuid = sel_uuid

    # Fetch detail
    try:
        sel_obj = fetch_history_detail(sel_uuid)
    except ApiError:
        # fallback to list item if detail endpoint not available
        sel_obj = next((it for it in items if (it.get("uuid") or it.get("UUID")) == sel_uuid), None)

    if sel_obj:
        with st.container(border=True):
            st.markdown("### 🔍 결과 상세")
            meta1, meta2, meta3 = st.columns(3)
            meta1.metric("UUID", sel_uuid)
            meta2.metric("MODEL", sel_obj.get("modelName") or sel_obj.get("MODEL_NAME"))

            st.markdown("#### 🧑‍💻 프롬프트")
            st.code(sel_obj.get("promptText") or sel_obj.get("PROMPT_TEXT") or "", language="markdown")

            st.markdown("#### 🤖 응답")
            st.code(sel_obj.get("responseText") or sel_obj.get("RESPONSE_TEXT") or "", language="markdown")

            m1, m2, m3, m4 = st.columns(4)
            m1.write(f"**MODEL_NAME**: {sel_obj.get('modelName') or sel_obj.get('MODEL_NAME')}")
            
            m2.write(f"**CALL_DATE**: {datetime.datetime.strptime(sel_obj.get('callDate'), '%Y%m%d').date() or datetime.datetime.strptime(sel_obj.get('CALL_DATE'), '%Y%m%d').date()}")
            
            m3.write(f"**CALL_TIME**: {datetime.datetime.strptime(sel_obj.get('callTime'), '%H%M%S').time() or datetime.datetime.strptime(sel_obj.get('CALL_TIME'), '%H%M%S').time()}")



            # Download JSON
            import json
            json_str = json.dumps(sel_obj, ensure_ascii=False, indent=2)
            st.download_button("JSON 다운로드", data=json_str, file_name=f"history_{sel_uuid}.json", mime="application/json")
else:
    st.info("표시할 이력이 없습니다. 필터를 확인해 보세요.")

st.caption("ⓒ Tune Wizard · Prompt History Viewer (PROMPT_HISTORY schema)")
