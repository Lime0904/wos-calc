with st.form("input_form"):
    st.markdown("### 🧱 건물 및 레벨 선택")

    buildings = sorted(build_time_df["Building"].unique())
    st.markdown("**건물 선택**")
    selected_building = st.radio("건물", buildings, index=buildings.index("Infantry Camp"), label_visibility="collapsed")

    building_df = build_time_df[build_time_df["Building"] == selected_building]
    level_options = building_df.sort_values("numerical")[["level", "numerical"]].drop_duplicates()

    # FC7 기본값 (없으면 첫 번째)
    default_index = level_options[level_options["level"] == "FC7"].index[0] if "FC7" in level_options["level"].values else 0

    col1, col2 = st.columns(2)
    with col1:
        start_label = st.selectbox("시작 레벨", level_options["level"].tolist(), index=default_index)
    with col2:
        end_label = st.selectbox("목표 레벨", level_options["level"].tolist(), index=default_index)
    
    start_num = level_options[level_options["level"] == start_label]["numerical"].values[0]
    end_num = level_options[level_options["level"] == end_label]["numerical"].values[0]

    # 버프 입력 + 제출 버튼은 그대로 유지
    st.markdown("### ⚙️ 버프 정보 입력")
    cs = st.number_input("🏗️ 기본 건설 속도 (%)", value=85.0, min_value=0.0) / 100

    col3, col4 = st.columns(2)
    with col3:
        boost = st.selectbox("💥 중상주의 (Merc/Double Time 중 하나)", ["Yes", "No"], index=0)
    with col4:
        vp = st.selectbox("🎖️ VP 관직 보너스", ["Yes", "No"], index=0)

    hyena = st.selectbox("🦴 하이에나 보너스 (%)", [0, 5, 7, 9, 12, 15], index=5) / 100

    submitted = st.form_submit_button("🧮 계산하기")
