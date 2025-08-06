import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Make Prompt - SQL 튜닝", layout="wide")

# 제목
st.title("🛠 Make Prompt (SQL 튜닝용)")

# 임의 테이블 목록 및 컬럼 정보
table_list = ["employees", "departments", "salaries"]

table_schemas = {
    "employees": pd.DataFrame({
        "Column": ["emp_no", "first_name", "last_name", "gender", "hire_date"],
        "Type": ["INT", "VARCHAR", "VARCHAR", "CHAR", "DATE"]
    }),
    "departments": pd.DataFrame({
        "Column": ["dept_no", "dept_name"],
        "Type": ["CHAR(4)", "VARCHAR"]
    }),
    "salaries": pd.DataFrame({
        "Column": ["emp_no", "salary", "from_date", "to_date"],
        "Type": ["INT", "INT", "DATE", "DATE"]
    }),
}

# 테이블 선택
selected_table = st.selectbox("📊 테이블 선택", table_list)

# 스키마 출력
st.subheader("📋 테이블 컬럼 정보")
st.dataframe(table_schemas[selected_table])

# 튜닝 목적 선택
tuning_goal = st.selectbox(
    "🎯 튜닝 목적을 선택하세요",
    ["인덱스 추천", "조인 순서 최적화", "실행계획 분석", "쿼리 리팩토링"]
)

# 사용자 입력 조건
user_input = st.text_area("✏️ 조건 또는 설명 입력 (선택)", placeholder="예: 최근 5년 이내 입사자만 대상으로...")

# 프롬프트 생성
if st.button("🚀 프롬프트 생성"):
    prompt = f"""당신은 SQL 성능 튜닝 전문가입니다.
튜닝 대상 테이블: [{selected_table}]
컬럼 정보:
{table_schemas[selected_table].to_markdown(index=False)}

튜닝 목적: {tuning_goal}
"""
    if user_input.strip():
        prompt += f"\n추가 설명: {user_input.strip()}"

    prompt += "\n\n이 정보를 바탕으로 튜닝된 SQL이나 인사이트를 제시해주세요."

    # 결과 출력
    st.subheader("🧾 생성된 프롬프트")
    st.code(prompt.strip(), language="markdown")