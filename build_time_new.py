import streamlit as st
import pandas as pd

st.set_page_config(page_title="건설 가속 계산기", layout="wide")

# 🍋 레벨 매핑 (표시용)
fc_map = {
    1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8",
    9: "9", 10: "10", 11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16",
    17: "17", 18: "18", 19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24",
    25: "25", 26: "26", 27: "27", 28: "28", 29: "29", 30: "30", 31: "30-1", 32: "30-2",
    33: "30-3", 34: "30-4", 35: "FC1", 36: "FC1-1", 37: "FC1-2", 38: "FC1-3", 39: "FC1-4",
    40: "FC2", 41: "FC2-1", 42: "FC2-2", 43: "FC2-3", 44: "FC2-4", 45: "FC3", 46: "FC3-1",
    47: "FC3-2", 48: "FC3-3", 49: "FC3-4", 50: "FC4", 51: "FC4-1", 52: "FC4-2", 53: "FC4-3", 54: "FC4-4",
    55: "FC5", 56: "FC5-1", 57: "FC5-2", 58: "FC5-3", 59: "FC5-4", 60: "FC6", 61: "FC6-1", 62: "FC6-2",
    63: "FC6-3", 64: "FC6-4", 65: "FC7", 66: "FC7-1", 67: "FC7-2", 68: "FC7-3", 69: "FC7-4",
    70: "FC8", 71: "FC8-1", 72: "FC8-2", 73: "FC8-3", 74: "FC8-4", 75: "FC9", 76: "FC9-1",
    77: "FC9-2", 78: "FC9-3", 79: "FC9-4", 80: "FC10"
}

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

# ✅ 각 건물에 개별 레벨 리스트 생성
level_options = {b: lv_df["fc_level"].tolist() for b, lv_df in level_dict.items()}
def_fc = next((v for v in list(fc_map.values()) if "FC7" in v), list(fc_map.values())[0])

data = [
    {
        "건물명(Building)": building_labels[b],
        "현재 레벨(Current)": def_fc,
        "목표 레벨(Target)": def_fc,
    } for b in ordered_buildings
]
df_input = pd.DataFrame(data)

st.title("🏗️ 건설 가속 계산기")
st.caption("건물별로 현재/목표 레벨을 표로 한 번에 설정하세요.")

st.markdown("""
    <style>
    .stDataFrame tbody tr td {
        text-align: center;
    }
    thead tr th:first-child { display: none }
    tbody th { display: none }
    .st-emotion-cache-1ov7g5e {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .st-emotion-cache-1ov7g5e .element-container .stDataFrame td, 
    .st-emotion-cache-1ov7g5e .element-container .stDataFrame th {
        text-align: center !important;
        vertical-align: middle !important;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("### 🏢 건물별 레벨 입력")
    # column_config에서 공통 옵션이 아닌, 단일 level_list로 설정 (제한적이지만 Streamlit 현재 제약상 해결법)
    edited_df = st.data_editor(
        df_input,
        use_container_width=True,
        num_rows="fixed",
        hide_index=True,
        column_config={
            "건물명(Building)": st.column_config.TextColumn(disabled=True),
            "현재 레벨(Current)": st.column_config.SelectboxColumn(options=list(fc_map.values())),
            "목표 레벨(Target)": st.column_config.SelectboxColumn(options=list(fc_map.values())),
        }
    )

# 버프 입력
with st.container():
    st.markdown("### 🧪 버프 입력")
    cs = st.number_input("기본 건설 속도(%) (Your Constr Speed)", value=85.0) / 100
    boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    vp = st.selectbox("부집행관 여부 (VP)", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스(%) (Pet skill)", [0, 5, 7, 9, 12, 15], index=5) / 100

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

    total = 0
    per_building_result = {}

    for _, row in edited_df.iterrows():
        b = [k for k, v in building_labels.items() if v == row["건물명(Building)"]][0]
        start, end = row["현재 레벨(Current)"], row["목표 레벨(Target)"]
        if start == end:
            continue

        lv_df = level_dict[b]
        start_num = lv_df[lv_df["fc_level"] == start]["numerical"].values[0]
        end_num = lv_df[lv_df["fc_level"] == end]["numerical"].values[0]
        sub_df = df[(df["Building"] == b) & (df["numerical"] > start_num) & (df["numerical"] <= end_num)]
        subtotal = sub_df["Total"].sum()
        total += subtotal
        per_building_result[b] = subtotal

    boost_bonus = 0.2 if boost == "Yes" else 0
    vp_bonus = 0.1 if vp == "Yes" else 0
    speed_total = 1 + cs + vp_bonus + hyena
    adjusted = (total / speed_total) * (1 - boost_bonus)

    st.markdown("### ✅ 최종 건설 시간")
    st.success(f"⚡ Adjusted Time: {secs_to_str(adjusted)}")

    with st.expander("⏱️ Unboosted Time (참고용)"):
        st.info(f"🕒 총합: {secs_to_str(total)}")
        for b in ordered_buildings:
            if b in per_building_result:
                st.markdown(f"- **{building_labels[b]}**: {secs_to_str(per_building_result[b])}")

st.markdown("---")
st.markdown("<div style='text-align:center; color: gray;'>🍋 Made with 💚 by <b>Lime</b></div>", unsafe_allow_html=True)
