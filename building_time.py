import streamlit as st
import pandas as pd

# --- 데이터 불러오기 ---
@st.cache_data

def load_data():
    df = pd.read_csv("data/build_time.csv")  # CSV로 저장되어 있다고 가정
    return df

build_time_df = load_data()

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- UI ---
st.title("🏗️ 건설 가속 계산기")
st.markdown("건물과 레벨, 버프 정보를 입력하면 최종 건설 시간을 계산해줍니다.")

with st.form("input_form"):
    st.subheader("📌 건물 및 레벨 선택")
    buildings = build_time_df["Building"].unique()
    building = st.selectbox("건물을 선택하세요", buildings, index=list(buildings).index("Infantry Camp"))

    levels = build_time_df["Level"].unique()
    levels = sorted([int(l) for l in levels if not pd.isnull(l)])
    def_fc7 = 23
    cols = st.columns(2)
    with cols[0]:
        start_level = st.selectbox("시작 레벨", levels, index=levels.index(def_fc7))
    with cols[1]:
        end_level = st.selectbox("목표 레벨", levels, index=levels.index(def_fc7))

    st.subheader("⚙️ 버프 설정")
    cs = st.number_input("건설 속도 (Construction Speed %)", value=85.0, min_value=0.0) / 100
    row1 = st.columns(2)
    with row1[0]:
        merc = st.selectbox("Mercantilism 보너스", ["Yes", "No"], index=0)
    with row1[1]:
        vp = st.selectbox("VP 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("Builder's Aide (하이에나) %", [0, 5, 7, 9, 12, 15], index=5) / 100
    double_time = st.checkbox("Double Time 적용 (20%)", value=True)

    submitted = st.form_submit_button("🧮 계산하기")

if submitted:
    # --- 계산 ---
    filtered = build_time_df[(build_time_df["Building"] == building) &
                             (build_time_df["Level"] >= start_level) &
                             (build_time_df["Level"] <= end_level)]

    total_secs = filtered["Seconds"].sum()
    merc_bonus = 0.1 if merc == "Yes" else 0
    vp_bonus = 0.1 if vp == "Yes" else 0
    dt_penalty = 0.2 if double_time else 0

    reduced_secs = total_secs / (1 + cs + merc_bonus + vp_bonus + hyena)
    adjusted_secs = reduced_secs * (1 - dt_penalty)

    def secs_to_str(secs):
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{d}d {h}:{m:02}:{s:02}"

    st.markdown("---")
    st.subheader("📤 계산 결과")
    st.metric("Unboosted Time", secs_to_str(total_secs))
    st.metric("Adjusted Time", secs_to_str(adjusted_secs))
    st.metric("시간 단축률", f"{100 * (1 - adjusted_secs / total_secs):.2f}%")

