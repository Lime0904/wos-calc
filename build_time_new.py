import streamlit as st
import pandas as pd

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- FC 레벨 매핑 (코드 내 포함)
fc_map = {
    1: "1", 2: "2", 3: "3", 4: "4",
    5: "5", 6: "6", 7: "7", 8: "8",
    9: "9", 10: "10", 11: "11", 12: "12",
    13: "13", 14: "14", 15: "15", 16: "16",   
    17: "17", 18: "18", 19: "19", 20: "20",
    21: "21", 22: "22", 23: "23", 24: "24",
    25: "25", 26: "26", 27: "27", 28: "28",
    29: "29", 30: "30", 
    30-1: "30-1", 30-2: "30-2", 30-3: "30-3", 30-4: "30-4",
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

ordered_buildings = [
    "Furnace", "Embassy", "Command Center", "Infantry Camp",
    "Lancer Camp", "Marksman Camp", "War Academy", "Infirmary", "Research Center"
]

@st.cache_data
def load_data():
    df = pd.read_csv("data/build_numeric.csv")
    df = df[df["Building"].isin(ordered_buildings)]
    df["fc_level"] = df["numerical"].map(fc_map)
    return df.dropna(subset=["fc_level"])

df = load_data()

level_dict = {
    b: df[df["Building"] == b][["fc_level", "numerical"]]
    .drop_duplicates()
    .sort_values("numerical")
    .reset_index(drop=True)
    for b in ordered_buildings if b in df["Building"].unique()
}

st.title("\U0001f3d7️ 건설 가속 계산기")
st.caption("도달 목표 레벨에 해당하는 시간만 계산합니다.")

st.markdown("### \U0001f9f1 건설 목표")
selected_levels = {}

with st.form("build_form"):
    for b in ordered_buildings:
        if b not in level_dict:
            continue

        # numerical 기준 정렬된 fc_level 리스트 추출
        lv_df = level_dict[b].sort_values("numerical").reset_index(drop=True)
        level_list = lv_df["fc_level"].tolist()  # <- 문자열 변환 없이 그대로 사용
        default_idx = next((i for i, v in enumerate(level_list) if "FC7" in v), 0)

        st.markdown(f"**\U0001f3db {b}**")
        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox(f"{b} 현재 레벨", level_list, index=default_idx, key=f"{b}_start")
        with col2:
            end = st.selectbox(f"{b} 목표 레벨", level_list, index=default_idx, key=f"{b}_end")

        if start != end:
            selected_levels[b] = (start, end)

    st.markdown("---")
    st.markdown("### \U0001f9f0 버프 입력")
    cs = st.number_input("기본 건설 속도 (%)", value=85.0) / 100
    boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    vp = st.selectbox("VP 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    st.markdown("---")
    submitted = st.form_submit_button("\U0001f9ee 계산하기")

if submitted:
    def secs_to_str(secs):
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{d}d {h}:{m:02}:{s:02}"

    if not selected_levels:
        st.warning("⚠️ 최소 한 건물이라도 구간을 선택해주세요.")
    else:
        total = 0
        per_building_result = {}

        for b, (start_fc, end_fc) in selected_levels.items():
            lv_df = level_dict[b]
            end_num = lv_df[lv_df["fc_level"].astype(str) == str(end_fc)]["numerical"].values[0]

            sub_df = df[(df["Building"] == b) & (df["numerical"] == end_num)]
            subtotal = sub_df["Total"].sum()
            total += subtotal
            per_building_result[b] = subtotal

        st.markdown("---")
        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        adjusted = total / (1 + cs + vp_bonus + hyena + boost_bonus)

        st.markdown("### ✅ 최종 건설 시간")
        st.success(f"⚡ **Adjusted Time:** {secs_to_str(adjusted)}")

        st.markdown("### ⏱️ Unboosted Time")
        for b in ordered_buildings:
            if b in per_building_result:
                st.markdown(f"- **{b}**: {secs_to_str(per_building_result[b])}")
        st.info(f"🕒 **총합:** {secs_to_str(total)}")
