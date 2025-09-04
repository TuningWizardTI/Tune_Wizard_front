import streamlit as st
import requests
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="Make Prompt - SQL 튜닝", layout="wide")

# 제목
st.title("🛠 Make Prompt (SQL 튜닝용)")

# 호출 API URL목록
API_TABLE_URL = "http://localhost:8080/api/v1/chatGPT/tableList"
API_URL = "http://localhost:8080/api/v1/chatGPT/tableInfoList"
headers = {
    "Content-Type":"application/json"
}

# 테이블 선택


try:
    table_response = requests.post(API_TABLE_URL, headers)
    table_response.raise_for_status()
    table_options = table_response.json()  # 응답 JSON에서 'tables' 키 값 추출
    if not table_options:  # 빈 배열이면 기본 옵션
        table_options = ["SQL 튜닝", "힌트 설명", "실행계획 분석"]
except Exception as e:
    st.warning(f"테이블 목록을 불러오지 못했습니다: {e}")
    table_options = ["SQL 튜닝", "힌트 설명", "실행계획 분석"]

table_name = st.selectbox(
    "보낼 테이블을 선택하세요",
    table_options,
    index=0
)

# 📥 chat_input은 항상 하단에 고정됨
if table_name :
    with st.spinner("컬럼을 불러오는 중입니다..."):
        try:
            json={"tableName": table_name}
            print(json)
            response = requests.post(API_URL,  headers=headers, json=json)
            
            response.raise_for_status()
            ai_answer = response.json().get("result", "답변을 받아오지 못했습니다.")
            print(response.json())
        except Exception as e:
            ai_answer = f"API 호출 실패: {e}"

table_schemas = {
    table_name: pd.DataFrame(
        response.json()
    ),
}

# 스키마 출력
st.subheader("📋 테이블 컬럼 정보")
st.dataframe(table_schemas[table_name])

# 튜닝 목적 선택
tuning_goal = st.selectbox(
    "🎯 튜닝 목적을 선택하세요",
    ["인덱스 추천", "조인 순서 최적화", "실행계획 분석", "쿼리 리팩토링", "쿼리생성"]
)



# 사용자 입력 조건
user_input = st.text_area("✏️ 조건 또는 설명 입력 (선택)", placeholder="예: 최근 5년 이내 입사자만 대상으로...")

# 프롬프트 생성
if st.button("🚀 프롬프트 생성"):
    prompt = f"""당신은 SQL 성능 튜닝 전문가입니다.
튜닝 대상 테이블: [{table_name}]
컬럼 정보:
{table_schemas[table_name].to_markdown(index=False)}

튜닝 목적: {tuning_goal}
"""
    if user_input.strip():
        prompt += f"\n추가 설명: {user_input.strip()}"

    prompt += "\n\n이 정보를 바탕으로 튜닝된 SQL이나 인사이트를 제시해주세요."

    # 결과 출력
    st.subheader("🧾 생성된 프롬프트")
    st.code(prompt.strip(), language="markdown")



def build_schema_dict(df_cols, table_col='table_name', column_col='column_name', type_col='type_str'):
    """
    df_cols: 테이블/컬럼/타입이 들어있는 단일 DataFrame
    반환: {table_name: DataFrame([Column, Type])}
    """
    result = {}
    for tname, g in df_cols.groupby(table_col):
        result[tname] = g[[column_col, type_col]] \
            .rename(columns={column_col: "Column", type_col: "Type"}) \
            .reset_index(drop=True)
    return result