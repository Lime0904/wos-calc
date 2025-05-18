import streamlit as st
import pandas as pd
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- FC 레벨 매핑 (코드 내 포함)
fc_map = {
    35: "FC1", 36: "FC1-1", 37: "FC1-2", 38: "FC1-3",
    39: "FC2", 40: "FC2-1", 41: "FC2-2", 42: "FC2-3",
    43: "FC3", 44: "FC3-1", 45: "FC3-2", 46: "FC3-3",
    47: "FC4", 48: "FC4-1", 49: "FC4-2", 50: "FC4-3",
    51: "FC5", 52: "FC5-1", 53: "FC5-2", 54: "FC5-3",
    55: "FC6", 56: "FC6-1", 57: "FC6-2", 58: "FC6-3",
    59: "FC7", 60: "FC7-1", 61: "FC7-2", 62: "FC7-3",
    63: "FC8", 64: "FC8-1", 65: "FC8-2", 66: "FC8-3",
    67: "FC9", 68: "FC9-1", 69: "FC9-2", 70: "FC9-3",
    71: "FC10", 72: "FC10-1", 73: "FC10-2", 74: "FC10-3",
    75: "FC11", 76: "FC11-1", 77: "FC11-2", 78: "FC11-3",
    79: "FC12", 80: "FC12-1"
}

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/build_numeric.csv")
    df = df[df["Building"].isin(["Furnace", "Infantry Camp"])]
    df["fc_level"] = df["numerical"].map(fc_map)
    return df.dropna(subset=["fc_level"])

df = load_data()

# --- 레벨 목록 구성 ---
level_dict = {
    b: df[df["Building"] == b][["fc_level", "numerical"]].drop_duplicates().sort_values("numerical").reset_index(drop=True)
    for b in df["Building"].unique()
}

# --- UI 시작 ---
st.title("🏗️ 건설 가속 계산기")
st.caption("Furnace / Infantry Camp의 현재-목표 레벨과 버프를 선택하세요.")

selected_levels = {}

with st.form("build_form"):
    for b in level_dict:
        lv_df = level_dict[b]
        level_list = lv_df["fc_level"].tolist()
        default_idx = lv_df[lv_df["fc_level"].str.contains("FC7")].index[0] if any(lv_df["fc_level"].str.contains("FC7")) else 0

        st.markdown(f"**🏛 {b}**")
        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox(f"{b} 현재 레벨", level_list, index=default_idx, key=f"{b}_start")
        with col2:
            end = st.selectbox(f"{b} 목표 레벨", level_list, index=default_idx, key=f"{b}_end")

        if start != end:
            selected_levels[b] = (start, end)

    st.markdown("### ⚙️ 버프 설정")
    cs = st.number_input("기본 건설 속도 (%)", value=85.0) / 100
    boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    vp = st.selectbox("VP 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 ---
if submitted:
    def secs_to_str(secs):
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{d}d {h}:{m:02}:{s:02}"

    if not selected_levels:
        st.warning("⚠️ 레벨 구간이 선택되지 않았습니다.")
    else:
        total = 0
        st.subheader("📤 계산 결과")

        for b, (start_fc, end_fc) in selected_levels.items():
            lv_df = level_dict[b]
            start_num = lv_df[lv_df["fc_level"] == start_fc]["numerical"].values[0]
            end_num = lv_df[lv_df["fc_level"] == end_fc]["numerical"].values[0]

            sub_df = df[
                (df["Building"] == b) &
                (df["numerical"] >= min(start_num, end_num)) &
                (df["numerical"] <= max(start_num, end_num))
            ].copy()

            subtotal = sub_df["Total"].sum()
            total += subtotal

            sub_df["초"] = sub_df["Total"].astype(int)
            sub_df["시간"] = sub_df["초"].apply(secs_to_str)

            st.markdown(f"#### 🏛 {b}")
            st.dataframe(sub_df[["fc_level", "시간"]].set_index("fc_level"), use_container_width=True)
            st.markdown(f"🔹 구간 총 시간: `{secs_to_str(subtotal)}`")

        # 최종 Adjusted
        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        adjusted = total / (1 + cs + vp_bonus + hyena + boost_bonus)

        st.markdown("### 🧮 총 건설 시간")
        st.info(f"Unboosted Time: {secs_to_str(total)}")
        st.success(f"Adjusted Time: {secs_to_str(adjusted)}")
