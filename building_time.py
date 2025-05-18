import streamlit as st
import pandas as pd

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    return pd.read_csv("data/build_time_clean.csv", encoding="cp949")

df = load_data()
target_buildings = ["Furnace", "Command Center", "Embassy"]
df = df[df["Building"].isin(target_buildings)]

# --- 건물별 레벨 매핑 dict 생성 ---
level_dict = {
    b: df[df["Building"] == b][["level", "numerical"]].drop_duplicates().sort_values("numerical").reset_index(drop=True)
    for b in target_buildings
}

# --- UI 시작 ---
st.title("🏗️ 건설 가속 계산기")
st.markdown("현재/목표 레벨과 버프를 입력하면 최종 건설 시간을 계산합니다.")

with st.form("build_form"):
    st.markdown("### 🧱 건물별 레벨 선택")

    selected = {}
    for b in target_buildings:
        levels = level_dict[b]["level"].tolist()
        default_idx = level_dict[b][level_dict[b]["level"] == "FC7"].index[0] if "FC7" in levels else 0

        st.markdown(f"**🏛 {b}**")
        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox(f"{b} 현재 레벨", levels, index=default_idx, key=f"{b}_start")
        with col2:
            end = st.selectbox(f"{b} 목표 레벨", levels, index=default_idx, key=f"{b}_end")

        if start != end:
            selected[b] = (start, end)

    st.markdown("### ⚙️ 버프 정보")
    cs = st.number_input("기본 건설 속도 (%)", value=85.0) / 100
    col1, col2 = st.columns(2)
    with col1:
        boost = st.selectbox("중상주의 (Double Time)", ["Yes", "No"], index=0)
    with col2:
        vp = st.selectbox("VP 관직 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 ---
if submitted:
    if not selected:
        st.warning("⚠️ 최소 하나 이상의 건물을 선택해주세요.")
    else:
        def secs_to_str(secs):
            d = int(secs // 86400)
            h = int((secs % 86400) // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            return f"{d}d {h}:{m:02}:{s:02}"

        total = 0
        st.markdown("---")
        st.subheader("📤 계산 결과")

        for b, (start_label, end_label) in selected.items():
            levels = level_dict[b]
            start_num = levels[levels["level"] == start_label]["numerical"].values[0]
            end_num = levels[levels["level"] == end_label]["numerical"].values[0]

            sub = df[
                (df["Building"] == b) &
                (df["numerical"] >= min(start_num, end_num)) &
                (df["numerical"] <= max(start_num, end_num))
            ].copy()

            sub_total = sub["Total"].sum()
            total += sub_total

            sub["초"] = sub["Total"].astype(int)
            sub["시간"] = sub["초"].apply(secs_to_str)

            st.markdown(f"#### 🏛 {b}")
            st.dataframe(sub[["level", "시간"]].set_index("level"), use_container_width=True)
            st.markdown(f"🔹 구간 시간: `{secs_to_str(sub_total)}`")

        # 최종 계산
        boost_bonus = 0.2 if boost == "Yes" else 0
        vp_bonus = 0.1 if vp == "Yes" else 0
        adjusted = total / (1 + cs + vp_bonus + hyena + boost_bonus)

        st.markdown("### 🧮 총 건설 시간")
        st.info(f"🕒 Unboosted Time: {secs_to_str(total)}")
        st.success(f"⚡ Adjusted Time: {secs_to_str(adjusted)}")
