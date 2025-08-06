import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="📜 프롬포트 사용 이력", layout="wide")
st.title("📜 프롬포트 사용 이력 조회")

api_url = "http://localhost:8080/api/prompts/history"

try:
    #response = requests.get(api_url)
    data = '''{"id": 1,"prompt": "SQL 튜닝 프롬포트 예시","result": "인덱스 스캔이 적절합니다",     "usedAt": "2025-07-13T16:35:00"}'''
    #response.raise_for_status()
    #data = response.json()

    df = pd.DataFrame([data])
    df["usedAt"] = pd.to_datetime(df["usedAt"])
    df = df.sort_values(by="usedAt", ascending=False)

    st.dataframe(df, use_container_width=True)

except requests.exceptions.RequestException as e:
    st.error(f"API 호출 실패: {e}")