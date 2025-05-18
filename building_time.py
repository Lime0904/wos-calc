import streamlit as st
import pandas as pd
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    path = "data/build_time_clean.csv"
    return pd.read_csv(path, encoding="cp949")

df = load_data()

# 🔧 포함할 건물만 필터링
target_buildings = ["Furnace", "Command Center", "Embassy"]
df = df[df["Building"].isin(target_buildings)]

# --- 레벨 매핑 딕셔너리 구성 ---
level_dict = {
    b: df[df["Building"] == b][["level", "numerical"]]
    .drop_duplicates()
    .sort_values("numerical")
    .reset_index(drop=True)
    for b in target_buildings
}

# --- UI 시작 ---
st.title("🏗️ 건설 가속 계산기")
st.markdown("각 건물의 현재/목표 레벨과 버프 정보를 입력하면 총 건설 시간을 계산합니다.")

with st.expander("📘 기본 건설 속도 확인 방법"):
    st.markdown("""
    ▶️ 좌측 상단 프로필 옆 **주먹 아이콘** 클릭 → **보너스 보기** → **[발전] 탭** → **건설 속도 확인**

    ℹ️ 참고: 집행관 버프가 포함된 수치입니다.
    """)

# --- 입력 섹션 ---
st.subheader("🧱 건물별 현재/목표 레벨 선택")
selected_levels = {}

with st.form("build_form"):
    for b in target_buildings:
        levels_df = level_dict[b]
        level_list = levels_df["level"].astype(str).tolist()
        default_idx = levels_df[levels_df["level"] == "FC7"].index[0] if "FC7" in levels_df["level"].values else 0

        st.markdown(f"**🏛 {b}**")
        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox(f"{b} 현재 레벨", level_list, index=default_idx, key=f"{b}_start")
        with col2:
            end = st.selectbox(f"{b} 목표 레벨", level_list, index=default_idx, key=f"{b}_end")

        if start != end:
            selected_levels[b] = (start, end)

    st.markdown("### ⚙️ 버프 입력")
    cs = st.number_input("🏗️ 기본 건설 속도 (%)", value=85.0) / 100
    col3, col4 = st.columns(2)
    with col3:
        boost = st.selectbox("💥 중상주의 (Double Time)", ["Yes", "No"], index=0)
    with col4:
        vp = st.selectbox("🎖️ VP 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("🦴 하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 및 결과 ---
if submitted:
    if not selected_levels:
        st.warning("⚠️ 최소 하나 이상의 건물에서 레벨 구간을 선택해주세요.")
    else:
        def secs_to_str(secs):
            d = int(secs // 86400)
            h = int((secs % 86400) // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            return f"{d}d {h}:{m:02}:{s:02}"

        total_secs = 0
        st.markdown("---")
        st.subheader("📤 결과")

        for b, (start_label, end_label) in selected_levels.items():
            levels_df = level_dict[b]
            start_num = levels_df[levels_df["level"].astype(str) == str(start_label)]["numerical"].values[0]
            end_num = levels_df[levels_df["level"].astype(str) == str(end_label)]["numerical"].values[0]

            sub_df = df[
                (df["Building"] == b) &
                (df["numerical"] >= min(start_num, end_num)) &
                (df["numerical"] <= max(start_num, end_num))
            ].copy()

            subtotal = sub_df["Total"].sum()
            total_secs += subtotal

            sub_df["초"] = sub_df["Total"].astype(int)
            sub_df["시간"] = sub_df["초"].apply(secs_to_str)

            st.markdown(f"#### 🏛 {b}")
            st.dataframe(sub_df[["level", "시간"]].set_index("level"), use_container_width=True)
            st.markdown(f"🔹 해당 구간 소요 시간: `{secs_to_str(subtotal)}`")

        # 최종 Adjusted 시간
        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        adjusted = total_secs / (1 + cs + vp_bonus + hyena + boost_bonus)

        st.markdown("### 🧮 총 건설 시간")
        st.info(f"🕒 Unboosted Time: {secs_to_str(total_secs)}")
        st.success(f"⚡ Adjusted Time: {secs_to_str(adjusted)}")
