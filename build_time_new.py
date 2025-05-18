import streamlit as st
import pandas as pd
import os

# --- 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    df_build = pd.read_csv("data/build_numeric.csv")  # numerical, Total, Building
    df_map = pd.read_csv("data/fur_numeric.txt", sep="\t")  # fc_level, numerical
    df_map.columns = ["fc_level", "numerical"]
    df = pd.merge(df_build, df_map, on="numerical", how="left")
    return df[df["Building"].isin(["Furnace", "Infantry Camp"])]

df = load_data()

# --- level 목록 구성 ---
level_dict = {
    b: df[df["Building"] == b][["fc_level", "numerical"]].dropna().sort_values("numerical").reset_index(drop=True)
    for b in df["Building"].unique()
}

# --- UI 시작 ---
st.title("🏗️ 건설 가속 계산기")
st.caption("현재/목표 레벨을 선택하면 건설 시간을 계산합니다.")

# --- 입력 영역 ---
selected_levels = {}

with st.form("build_form"):
    for b in level_dict:
        lv_df = level_dict[b]
        level_list = lv_df["fc_level"].astype(str).tolist()
        default_idx = lv_df[lv_df["fc_level"].str.contains("FC7", na=False)].index[0] if "FC7" in "".join(level_list) else 0

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
if submitted and selected_levels:
    def secs_to_str(secs):
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{d}d {h}:{m:02}:{s:02}"

    total = 0
    st.markdown("---")
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
        st.markdown(f"🔹 해당 구간 소요 시간: `{secs_to_str(subtotal)}`")

    # 버프 반영
    boost_bonus = 0.2 if boost == "Yes" else 0
    vp_bonus = 0.1 if vp == "Yes" else 0
    adjusted = total / (1 + cs + vp_bonus + hyena + boost_bonus)

    st.markdown("### 🧮 총 건설 시간")
    st.info(f"🕒 Unboosted Time: {secs_to_str(total)}")
    st.success(f"⚡ Adjusted Time: {secs_to_str(adjusted)}")

elif submitted and not selected_levels:
    st.warning("⚠️ 레벨이 변경되지 않았습니다. 계산할 범위를 선택해주세요.")
