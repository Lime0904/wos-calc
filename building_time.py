import streamlit as st
import pandas as pd
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    df = pd.read_csv("build_time.csv")
    return df

if not os.path.exists("build_time.csv"):
    st.error("⚠️ 'build_time.csv' 파일이 누락되었습니다.")
    st.stop()

build_time_df = load_data()

# --- 헤더 영역 ---
st.title("🏗️ 건설 가속 계산기")
st.caption("건물, 레벨, 버프 정보를 입력하면 최종 건설 시간을 계산합니다.")

# --- 건설 속도 가이드 (텍스트) ---
with st.expander("📘 기본 건설 속도 확인 방법"):
    st.markdown("""
    **확인 경로:**  
    ▶️ 좌측 상단 프로필 옆 **주먹 아이콘** 클릭 → **보너스 보기** → **[발전] 탭** → **건설 속도 확인**

    ℹ️ 참고: **집행관 버프**가 적용되어 있을 경우 이 수치에 포함되어 표시됩니다.
    """)

# --- 입력 폼 영역 ---
with st.form("input_form"):
    st.markdown("### 🧱 건물 및 레벨 선택")
    buildings = build_time_df["Building"].unique()
    building = st.selectbox("건물 선택", buildings, index=list(buildings).index("Infantry Camp"))

    levels = sorted([int(l) for l in build_time_df["Level"].unique() if not pd.isnull(l)])
    def_fc7 = 23
    col1, col2 = st.columns(2)
    with col1:
        start_level = st.selectbox("시작 레벨", levels, index=levels.index(def_fc7))
    with col2:
        end_level = st.selectbox("목표 레벨", levels, index=levels.index(def_fc7))

    st.markdown("### ⚙️ 버프 정보 입력")
    cs = st.number_input("🏗️ 기본 건설 속도 (%)", value=85.0, min_value=0.0) / 100

    col3, col4 = st.columns(2)
    with col3:
        boost = st.selectbox("💥 중상주의 (Merc/Double Time)", ["Yes", "No"], index=0)
    with col4:
        vp = st.selectbox("🎖️ VP 관직 보너스", ["Yes", "No"], index=0)

    hyena = st.selectbox("🦴 하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 및 출력 ---
if submitted:
    # 필터링
    filtered = build_time_df[
        (build_time_df["Building"] == building) &
        (build_time_df["Level"] >= start_level) &
        (build_time_df["Level"] <= end_level)
    ]

    total_secs = filtered["Seconds"].sum()
    boost_bonus = 0.2 if boost == "Yes" else 0
    vp_bonus = 0.1 if vp == "Yes" else 0
    adjusted_secs = total_secs / (1 + cs + vp_bonus + hyena + boost_bonus)

    def secs_to_str(secs):
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{d}d {h}:{m:02}:{s:02}"

    # 결과 출력
    st.markdown("---")
    st.markdown("### ⏱️ 각 레벨별 건설 시간")
    filtered_display = filtered.copy()
    filtered_display["Seconds"] = filtered_display["Seconds"].astype(int)
    filtered_display["시간"] = filtered_display["Seconds"].apply(secs_to_str)
    st.dataframe(filtered_display[["Level", "시간"]].set_index("Level"), use_container_width=True)

    st.markdown("### 🧮 총 건설 시간")
    st.info(f"🕒 Unboosted Time: {secs_to_str(total_secs)}")
    st.success(f"⚡ Adjusted Time: {secs_to_str(adjusted_secs)}")
