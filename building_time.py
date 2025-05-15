import streamlit as st
import pandas as pd

# --- 페이지 설정 (항상 첫 줄) ---
st.set_page_config(page_title="건설 가속 계산기", layout="centered")

# --- 데이터 불러오기 ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/build_time.csv")
    return df

build_time_df = load_data()

# --- UI ---
st.title("🏗️ 건설 가속 계산기")
st.markdown("목표하는 건물 레벨, 버프 정보를 입력하면 최종 건설 시간을 계산해줍니다.")

with st.expander("📸 내 기본 건설 속도 확인 방법 가이드"):
    st.image("data/build_speed_guide.png", caption="건설 속도 확인 위치 예시", use_container_width=True)
    st.markdown("""
    **확인 경로:**  
    ▶️ 좌측 상단 프로필 옆 **주먹 아이콘** 클릭 → **보너스 보기** → **[발전] 탭** → **건설 속도 확인**

    ℹ️ 참고: **집행관 버프**가 적용되어 있을 경우 이 수치에 포함되어 표시됩니다.
    """)

with st.form("input_form"):
    st.subheader("📌 건물 및 레벨 선택")
    buildings = build_time_df["Building"].unique()
    building = st.selectbox("건물을 선택하세요", buildings, index=list(buildings).index("Infantry Camp"))

    levels = build_time_df["Level"].unique()
    levels = sorted([int(l) for l in levels if not pd.isnull(l)])
    def_fc7 = 23
    cols = st.columns(2)
    with cols[0]:
        start_level = st.selectbox("시작 레벨", levels, index=levels.index(def_fc7))
    with cols[1]:
        end_level = st.selectbox("목표 레벨", levels, index=levels.index(def_fc7))

    st.subheader("🏗️ 건설 속도")
    cs = st.number_input("건설 속도 (Construction Speed %)", value=85.0, min_value=0.0) / 100

    st.subheader("⚙️ 버프 설정")
    row1 = st.columns(2)
    with row1[0]:
        boost = st.selectbox("중상주의 (Merc or Double Time 중 하나)", ["Yes", "No"], index=0)
    with row1[1]:
        vp = st.selectbox("VP 보너스", ["Yes", "No"], index=0)
    hyena = st.selectbox("Builder's Aide (하이에나) %", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")

if submitted:
    # --- 계산 ---
    filtered = build_time_df[(build_time_df["Building"] == building) &
                             (build_time_df["Level"] >= start_level) &
                             (build_time_df["Level"] <= end_level)]

    total_secs = filtered["Seconds"].sum()
    boost_bonus = 0.2 if boost == "Yes" else 0  # 중상주의 하나만 적용
    vp_bonus = 0.1 if vp == "Yes" else 0

    adjusted_secs = total_secs / (1 + cs + vp_bonus + hyena + boost_bonus)

    def secs_to_str(secs):
        d = int(secs // 86400)
        h = int((secs % 86400) // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{d}d {h}:{m:02}:{s:02}"

    st.markdown("---")
    st.subheader("📤 계산 결과")
    st.write("### ⏱️ 각 레벨별 건설 시간")
    filtered_display = filtered.copy()
    filtered_display["Seconds"] = filtered_display["Seconds"].astype(int)
    filtered_display["시간"] = filtered_display["Seconds"].apply(secs_to_str)
    st.dataframe(filtered_display[["Level", "시간"]].set_index("Level"), use_container_width=True)

    st.write("### 🧮 총 건설 시간")
    st.info(f"Unboosted Time: {secs_to_str(total_secs)}")
    st.success(f"Adjusted Time: {secs_to_str(adjusted_secs)}")
