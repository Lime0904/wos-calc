import streamlit as st
import pandas as pd

# 📱 모바일 최적화를 위한 layout 설정
st.set_page_config(page_title="건설 가속 계산기", layout="wide")

# 🔁 FC 레벨 매핑
fc_map = {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8",
    9: "9", 10: "10", 11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16",
    17: "17", 18: "18", 19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24",
    25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30", 31: "30-1", 32: "30-2",
    33: "30-3", 34: "30-4",
    35: "FC1", 36: "FC1-1", 37: "FC1-2", 38: "FC1-3", 39: "FC1-4",
    40: "FC2", 41: "FC2-1", 42: "FC2-2", 43: "FC2-3", 44: "FC2-4",
    45: "FC3", 46: "FC3-1", 47: "FC3-2", 48: "FC3-3", 49: "FC3-4",
    50: "FC4", 51: "FC4-1", 52: "FC4-2", 53: "FC4-3", 54: "FC4-4",
    55: "FC5", 56: "FC5-1", 57: "FC5-2", 58: "FC5-3", 59: "FC5-4",
    60: "FC6", 61: "FC6-1", 62: "FC6-2", 63: "FC6-3", 64: "FC6-4",
    65: "FC7", 66: "FC7-1", 67: "FC7-2", 68: "FC7-3", 69: "FC7-4",
    70: "FC8", 71: "FC8-1", 72: "FC8-2", 73: "FC8-3", 74: "FC8-4",
    75: "FC9", 76: "FC9-1", 77: "FC9-2", 78: "FC9-3", 79: "FC9-4",
    80: "FC10"
}

# 영어 → 한글 병기 이름
building_labels = {
    "Furnace": "Furnace (용광로)",
    "Embassy": "Embassy (대사관)",
    "Command Center": "Command Center (지휘부)",
    "Infantry Camp": "Infantry Camp (방패병영)",
    "Lancer Camp": "Lancer Camp (창병병영)",
    "Marksman Camp": "Marksman Camp (궁병병영)",
    "War Academy": "War Academy (전쟁아카데미)",
    "Infirmary": "Infirmary (의무실)",
    "Research Center": "Research Center (연구소)"
}
ordered_buildings = list(building_labels.keys())

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

st.title("🏗️ 건설 가속 계산기")
st.caption("목표 구간만 계산됩니다. 건물별로 현재와 목표 레벨을 선택하세요.")

selected_levels = {}

with st.container():
    st.markdown("### 🎯 건설 목표")

    for i in range(0, len(ordered_buildings), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j >= len(ordered_buildings):
                continue
            b = ordered_buildings[i + j]
            if b not in level_dict:
                continue
            lv_df = level_dict[b]
            level_list = lv_df["fc_level"].tolist()
            default_idx = next((k for k, v in enumerate(level_list) if "FC7" in v), 0)
            with cols[j]:
                st.markdown(f"**🏗️ {building_labels[b]}**")
                start = st.selectbox("현재(Current)", level_list, index=default_idx, key=f"{b}_start")
                end = st.selectbox("목표(Target)", level_list, index=default_idx, key=f"{b}_end")
                if start != end:
                    selected_levels[b] = (start, end)

with st.container():
    st.markdown("### 🧪 버프 입력")
    cs = st.number_input("기본 건설 속도(Your Constr Speed) (%)", value=85.0) / 100
    boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    vp = st.selectbox("부집행관 (VP)", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스(Pet Skill) (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

with st.expander("📘 내 기본 건설 속도 확인 방법 가이드"):
    st.markdown("""
    **확인 경로:**  
    ▶️ 좌측 상단 프로필 옆 **주먹 아이콘** 클릭 → **보너스 보기** → **[발전] 탭** → **건설 속도 확인**

    ℹ️ 참고: **집행관 버프**가 적용되어 있을 경우 이 수치에 포함되어 표시됩니다.
    """)

submitted = st.button("🧮 계산하기")

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
            end_num = lv_df[lv_df["fc_level"] == end_fc]["numerical"].values[0]
            start_num = lv_df[lv_df["fc_level"] == start_fc]["numerical"].values[0]
            sub_df = df[(df["Building"] == b) & (df["numerical"] > start_num) & (df["numerical"] <= end_num)]
            subtotal = sub_df["Total"].sum()
            total += subtotal
            per_building_result[b] = subtotal

        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        speed_total = 1 + cs + vp_bonus + hyena
        adjusted = (total / speed_total) * (1 - boost_bonus)

        st.markdown("### ✅ 최종 건설 시간")
        st.success(f"⚡ **Adjusted Time:** {secs_to_str(adjusted)}")

        with st.expander("📋 입력 요약"):
            st.markdown(
                f"""
                - Constr Speed: {cs*100:.1f}%  
                - Double Time: {'O' if boost == 'Yes' else 'X'}  
                - VP: {'O' if vp == 'Yes' else 'X'}  
                - Hyena: {int(hyena*100)}%  
                """
            )
            st.markdown("**📌 건설 구간:**")
            for b, (start_fc, end_fc) in selected_levels.items():
                st.markdown(f"- {building_labels[b]}: {start_fc} → {end_fc}")

        with st.expander("⏱️ Unboosted Time (참고용)"):
            st.info(f"🕒 총합: {secs_to_str(total)}")
            for b in ordered_buildings:
                if b in per_building_result:
                    st.markdown(f"- **{building_labels[b]}**: {secs_to_str(per_building_result[b])}")

st.markdown("---")
st.markdown("<div style='text-align:center; color: gray;'>🍋 Made with 💚 by <b>Lime</b></div>", unsafe_allow_html=True)
