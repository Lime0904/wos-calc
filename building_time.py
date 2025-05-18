import streamlit as st
import pandas as pd
import os

# --- 설정 ---
st.set_page_config(page_title="건설 가속 계산기 (Furnace 전용)", layout="centered")

# --- 데이터 로딩 ---
def load_data():
    path = "data/build_time_clean.csv"
    if not os.path.exists(path):
        st.error("❗ 'data/build_time_clean.csv' 파일을 찾을 수 없습니다.")
        st.stop()
    return pd.read_csv(path)

df = load_data()
df = df[df["Building"] == "Furnace"]

# --- 레벨 정리 ---
levels_df = df[["level", "numerical"]].drop_duplicates().sort_values("numerical").reset_index(drop=True)
level_list = levels_df["level"].tolist()
default_idx = levels_df[levels_df["level"] == "FC7"].index[0] if "FC7" in level_list else 0

# --- 헤더 ---
st.title("🔥 용광로 건설 가속 계산기 (Furnace Only)")

# --- 입력 UI ---
with st.form("furnace_form"):
    col1, col2 = st.columns(2)
    with col1:
        start = st.selectbox("현재 레벨", level_list, index=default_idx, key="start")
    with col2:
        end = st.selectbox("목표 레벨", level_list, index=default_idx, key="end")

    st.markdown("### ⚙️ 버프 설정")
    cs = st.number_input("기본 건설 속도 (%)", value=85.0) / 100
    col3, col4 = st.columns(2)
    with col3:
        boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    with col4:
        vp = st.selectbox("VP 관직 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 ---
if submitted:
    if start == end:
        st.warning("⚠️ 현재와 목표 레벨이 동일합니다. 변경 후 다시 시도해주세요.")
    else:
        def secs_to_str(secs):
            d = int(secs // 86400)
            h = int((secs % 86400) // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            return f"{d}d {h}:{m:02}:{s:02}"

        start_num = levels_df[levels_df["level"] == start]["numerical"].values[0]
        end_num = levels_df[levels_df["level"] == end]["numerical"].values[0]

        subset = df[
            (df["numerical"] >= min(start_num, end_num)) &
            (df["numerical"] <= max(start_num, end_num))
        ].copy()

        subtotal = subset["Total"].sum()

        subset["초"] = subset["Total"].astype(int)
        subset["시간"] = subset["초"].apply(secs_to_str)

        st.markdown("### ⏱️ 각 레벨별 건설 시간")
        st.dataframe(subset[["level", "시간"]].set_index("level"), use_container_width=True)

        st.markdown(f"🔹 해당 구간 소요 시간: `{secs_to_str(subtotal)}`")

        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        adjusted = subtotal / (1 + cs + vp_bonus + hyena + boost_bonus)

        st.markdown("### 🧮 총 건설 시간")
        st.info(f"Unboosted Time: {secs_to_str(subtotal)}")
        st.success(f"Adjusted Time: {secs_to_str(adjusted)}")
