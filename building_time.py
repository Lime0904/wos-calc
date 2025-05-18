import streamlit as st
import pandas as pd
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 로딩 ---
def load_data():
    path = "data/build_time_clean_with_research.csv"
    if not os.path.exists(path):
        st.error("❗ 'data/build_time_clean.csv' 파일을 찾을 수 없습니다.")
        st.stop()
    return pd.read_csv(path)

df = load_data()

# 🔧 Furnace만 필터링 (UI는 전체 버전처럼 보이게 유지)
df = df[df["Building"].str.strip().str.lower() == "furnace"]

# --- 레벨 매핑 딕셔너리 ---
buildings = sorted(df["Building"].unique())
level_dict = {
    b: df[df["Building"] == b][["level", "numerical"]].drop_duplicates().sort_values("numerical").reset_index(drop=True)
    for b in buildings
}

# --- 제목 및 가이드 ---
st.title("🏗️ 건설 가속 계산기")
st.caption("건물별 현재/목표 레벨과 버프 정보를 입력하면 총 건설 시간을 계산합니다.")

with st.expander("📘 기본 건설 속도 확인 방법"):
    st.markdown("""
    ▶️ 좌측 상단 프로필 옆 **주먹 아이콘** 클릭 → **보너스 보기** → **[발전] 탭** → **건설 속도 확인**

    ℹ️ 참고: 집행관 버프가 포함된 수치입니다.
    """)

# --- 입력 UI ---
st.subheader("🧱 건물별 현재/목표 레벨 선택")

selected_levels = {}

with st.form("building_form"):
    for b in buildings:
        levels_df = level_dict[b]
        level_list = levels_df["level"].tolist()
        default_idx = levels_df[levels_df["level"] == "FC7"].index[0] if "FC7" in level_list else 0

        st.markdown(f"**🏛 {b}**")
        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox(f"{b} 현재 레벨", level_list, index=default_idx, key=f"{b}_start")
        with col2:
            end = st.selectbox(f"{b} 목표 레벨", level_list, index=default_idx, key=f"{b}_end")

        if start != end:
            selected_levels[b] = (start, end)

    st.subheader("⚙️ 버프 설정")
    cs = st.number_input("기본 건설 속도 (%)", value=85.0) / 100
    col3, col4 = st.columns(2)
    with col3:
        boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    with col4:
        vp = st.selectbox("VP 관직 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 로직 ---
if submitted:
    if not selected_levels:
        st.warning("⚠️ 최소 하나 이상의 건물에서 레벨 범위를 선택해주세요.")
    else:
        def secs_to_str(secs):
            d = int(secs // 86400)
            h = int((secs % 86400) // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            return f"{d}d {h}:{m:02}:{s:02}"

        total_secs = 0
        st.subheader("📤 결과")

        for b, (start_label, end_label) in selected_levels.items():
            levels_df = level_dict[b]
            start_num = levels_df[levels_df["level"] == start_label]["numerical"].values[0]
            end_num = levels_df[levels_df["level"] == end_label]["numerical"].values[0]

            subset = df[
                (df["Building"] == b) &
                (df["numerical"] >= min(start_num, end_num)) &
                (df["numerical"] <= max(start_num, end_num))
            ].copy()

            subtotal = subset["Total"].sum()
            total_secs += subtotal

            subset["초"] = subset["Total"].astype(int)
            subset["시간"] = subset["초"].apply(secs_to_str)

            st.markdown(f"#### 🏛 {b}")
            st.dataframe(subset[["level", "시간"]].set_index("level"), use_container_width=True)
            st.markdown(f"🔹 해당 구간 소요 시간: `{secs_to_str(subtotal)}`")

        # 버프 반영
        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        adjusted = total_secs / (1 + cs + vp_bonus + hyena + boost_bonus)

        st.markdown("### 🧮 총 건설 시간")
        st.info(f"Unboosted Time: {secs_to_str(total_secs)}")
        st.success(f"Adjusted Time: {secs_to_str(adjusted)}")
