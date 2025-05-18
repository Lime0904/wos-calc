import streamlit as st
import pandas as pd

# --- 페이지 설정 ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 불러오기 ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/build_time_clean.csv")
    return df

build_time_df = load_data()

# --- 공통 레벨 옵션 추출 ---
level_options_map = {}
for b in build_time_df["Building"].unique():
    levels = (
        build_time_df[build_time_df["Building"] == b]
        .sort_values("numerical")[["level", "numerical"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    level_options_map[b] = levels

# --- 제목 및 안내 ---
st.title("🏗️ 건설 가속 계산기")
st.caption("각 건물의 현재/목표 레벨과 버프 정보를 입력하면 최종 건설 시간을 계산합니다.")

with st.expander("📘 기본 건설 속도 확인 방법"):
    st.markdown("""
    **확인 경로:**  
    ▶️ 좌측 상단 프로필 옆 **주먹 아이콘** 클릭 → **보너스 보기** → **[발전] 탭** → **건설 속도 확인**

    ℹ️ 참고: **집행관 버프**가 적용되어 있을 경우 이 수치에 포함되어 표시됩니다.
    """)

# --- 입력 폼 ---
with st.form("input_form"):
    st.markdown("### 🧱 건물별 현재/목표 레벨 선택")

    selected_buildings = {}
    for b in sorted(build_time_df["Building"].unique()):
        levels = level_options_map[b]
        default_index = levels[levels["level"] == "FC7"].index[0] if "FC7" in levels["level"].values else 0

        with st.expander(f"🏛 {b}"):
            col1, col2 = st.columns(2)
            with col1:
                start_label = st.selectbox(f"{b} - 현재 레벨", levels["level"], key=f"{b}_start", index=default_index)
            with col2:
                end_label = st.selectbox(f"{b} - 목표 레벨", levels["level"], key=f"{b}_end", index=default_index)

            start_num = levels[levels["level"] == start_label]["numerical"].values[0]
            end_num = levels[levels["level"] == end_label]["numerical"].values[0]

            if start_num != end_num:
                selected_buildings[b] = (start_num, end_num)

    st.markdown("### ⚙️ 버프 정보 입력")
    cs = st.number_input("🏗️ 기본 건설 속도 (%)", value=85.0, min_value=0.0) / 100

    col3, col4 = st.columns(2)
    with col3:
        boost = st.selectbox("💥 중상주의 (Double Time)", ["Yes", "No"], index=0)
    with col4:
        vp = st.selectbox("🎖️ VP 관직 보너스", ["Yes", "No"], index=0)

    hyena = st.selectbox("🦴 하이에나 보너스(Pet skill)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

# --- 계산 및 결과 출력 ---
if submitted and selected_buildings:
    total_raw = 0
    total_adjusted = 0

    st.markdown("---")
    st.subheader("📤 계산 결과")

    for b, (start, end) in selected_buildings.items():
        filtered = build_time_df[
            (build_time_df["Building"] == b) &
            (build_time_df["numerical"] >= min(start, end)) &
            (build_time_df["numerical"] <= max(start, end))
        ].copy()

        subtotal = filtered["Total"].sum()
        total_raw += subtotal

        # 시간 변환 함수
        def secs_to_str(secs):
            d = int(secs // 86400)
            h = int((secs % 86400) // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            return f"{d}d {h}:{m:02}:{s:02}"

        st.markdown(f"#### 🏛 {b}")
        filtered["초"] = filtered["Total"].astype(int)
        filtered["시간"] = filtered["초"].apply(secs_to_str)
        st.dataframe(filtered[["level", "시간"]].set_index("level"), use_container_width=True)
        st.markdown(f"🔹 이 구간 건설 시간: `{secs_to_str(subtotal)}`")

    # 버프 반영
    boost_bonus = 0.2 if boost == "Yes" else 0
    vp_bonus = 0.1 if vp == "Yes" else 0
    adjusted = total_raw / (1 + cs + vp_bonus + hyena + boost_bonus)

    # 결과 출력
    st.markdown("### 🧮 총 건설 시간")
    st.info(f"🕒 Unboosted Time: {secs_to_str(total_raw)}")
    st.success(f"⚡ Adjusted Time: {secs_to_str(adjusted)}")
elif submitted and not selected_buildings:
    st.warning("⛔ 건물별 현재/목표 레벨이 동일합니다. 최소 하나 이상 레벨 구간을 선택해주세요.")
