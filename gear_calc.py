import streamlit as st
import pandas as pd

# CSV 데이터 로딩
gear_df = pd.read_csv("data/gear_data.csv")
gear_levels = gear_df["Level"].tolist()
packages_df = pd.read_csv("data/packages.csv")

# 기어 자원 사전 생성
resource_dict = {
    row["Level"]: {
        "Alloy": row["Alloy"],
        "Polish": row["Polish"],
        "Design": row["Design"],
        "Amber": row["Amber"]
    } for _, row in gear_df.iterrows()
}

# 등급 한국어 매핑
level_labels = {
    "Green": "고급", "Green 1*": "고급 1성",
    "Blue": "레어", "Blue 1*": "레어 1성", "Blue 2*": "레어 2성", "Blue 3*": "레어 3성",
    "Purple": "에픽", "Purple 1*": "에픽 1성", "Purple 2*": "에픽 2성", "Purple 3*": "에픽 3성",
    "Purple T1": "에픽 T1", "Purple T1 1*": "에픽 T1 1성", "Purple T1 2*": "에픽 T1 2성", "Purple T1 3*": "에픽 T1 3성",
    "Gold": "레전드", "Gold 1*": "레전드 1성", "Gold 2*": "레전드 2성", "Gold 3*": "레전드 3성",
    "Gold T1": "레전드 T1", "Gold T1 1*": "레전드 T1 1성", "Gold T1 2*": "레전드 T1 2성", "Gold T1 3*": "레전드 T1 3성",
    "Gold T2": "레전드 T2", "Gold T2 1*": "레전드 T2 1성", "Gold T2 2*": "레전드 T2 2성", "Gold T2 3*": "레전드 T2 3성",
    "Legendary": "신화", "Legendary 1*": "신화 1성", "Legendary 2*": "신화 2성", "Legendary 3*": "신화 3성",
    "Legendary T1": "신화 T1", "Legendary T1 1*": "신화 T1 1성", "Legendary T1 2*": "신화 T1 2성", "Legendary T1 3*": "신화 T1 3성",
    "Legendary T2": "신화 T2", "Legendary T2 1*": "신화 T2 1성", "Legendary T2 2*": "신화 T2 2성", "Legendary T2 3*": "신화 T2 3성",
    "Legendary T3": "신화 T3", "Legendary T3 1*": "신화 T3 1성", "Legendary T3 2*": "신화 T3 2성", "Legendary T3 3*": "신화 T3 3성",
}

# 병종별 부위 매핑
gear_groups = {
    "방패병": ["Coat", "Pants"],
    "궁병": ["Ring", "Cudgel"],
    "창병": ["Hat", "Watch"]
}

gear_parts_kor = {
    "Hat": "모자",
    "Coat": "상의",
    "Ring": "반지",
    "Watch": "시계",
    "Pants": "하의",
    "Cudgel": "지팡이"
}

st.title("영주 장비 자원 계산기")

user_inputs = {}
st.subheader("각 부위의 현재 / 목표 등급")

for unit_type, parts in gear_groups.items():
    st.markdown(f"#### {unit_type}")
    for part in parts:
        part_label = gear_parts_kor[part]
        cols = st.columns(2)
        with cols[0]:
            cur = st.selectbox(
                f"{part_label} - 현재 등급",
                options=gear_levels,
                index=gear_levels.index("Gold"),
                key=f"{part}_cur",
                format_func=lambda x: level_labels.get(x, x)
            )
        with cols[1]:
            tar = st.selectbox(
                f"{part_label} - 목표 등급",
                options=gear_levels,
                index=gear_levels.index("Gold"),
                key=f"{part}_tar",
                format_func=lambda x: level_labels.get(x, x)
            )
        user_inputs[part_label] = (cur, tar)

st.markdown("---")
st.subheader("보유 자원 입력")
res_cols = st.columns(4)
user_owned = {
    "Design": res_cols[0].number_input("설계도면", min_value=0, value=0),
    "Alloy": res_cols[1].number_input("합금", min_value=0, value=0),
    "Polish": res_cols[2].number_input("윤활제", min_value=0, value=0),
    "Amber": res_cols[3].number_input("앰버", min_value=0, value=0),
}

# 선택사항 - 패키지 입력 섹션 (기본 숨김)
with st.expander("선택사항: 패키지 구매 입력", expanded=False):
    st.caption("⚠️ PACKAGES 데이터는 업데이트가 필요한 예시입니다. 실제 구매 구성을 확인해 주세요!")

    price_list = ["$5", "$10", "$20", "$50", "$100"]
    price_kor = {"$5": "7,500원", "$10": "15,000원", "$20": "30,000원", "$50": "79,000원", "$100": "149,000원"}

    package_counts = {}
    package_resources = {"Design": 0, "Alloy": 0, "Polish": 0, "Amber": 0, "Plans": 0, "DesignPlans": 0}

    st.markdown("### 📦 장인 패키지")
    artisan_types = ["Sublime", "Exquisite", "Classic"]
    for artisan in artisan_types:
        st.markdown(f"**{artisan}**")
        cols = st.columns(len(price_list))
        for i, price in enumerate(price_list):
            key = f"{artisan}_{price}"
            label = f"{price} ({price_kor[price]})"
            count = cols[i].number_input(label=label, min_value=0, value=0, step=1, key=key)
            package_counts[key] = count

        # expander는 컬럼 바깥에서 별도로 처리
        with st.expander(f"{artisan} 패키지 구성 보기", expanded=False):
            pkg = packages_df[packages_df["Category"] == artisan]
            for price in price_list:
                sub = pkg[pkg["Package"] == price]
                if not sub.empty:
                    st.markdown(f"**{price} ({price_kor[price]})**")
                    for _, row in sub.iterrows():
                        st.markdown(f"- {row['Resource']}: {int(row['Amount'])}")

    st.markdown("### 🌙 새벽시장")
    st.markdown("디자인 도면 전용")
    dawn_cols = st.columns(len(price_list))
    for i, price in enumerate(price_list):
        key = f"DawnMarket_{price}"
        label = f"{price} ({price_kor[price]})"
        count = dawn_cols[i].number_input(label=label, min_value=0, value=0, step=1, key=key)
        package_counts[key] = count

    with st.expander("새벽시장 패키지 구성 보기", expanded=False):
        dawn = packages_df[packages_df["Category"] == "DawnMarket"]
        for price in price_list:
            sub = dawn[dawn["Package"] == price]
            if not sub.empty:
                st.markdown(f"**{price} ({price_kor[price]})**")
                for _, row in sub.iterrows():
                    st.markdown(f"- {row['Resource']}: {int(row['Amount'])}")

# 패키지 자원 계산
for key, count in package_counts.items():
    if count > 0:
        category, price = key.split("_")
        pkg_rows = packages_df[(packages_df["Category"] == category) & (packages_df["Package"] == price)]
        for _, row in pkg_rows.iterrows():
            res = row["Resource"]
            if res not in package_resources:
                package_resources[res] = 0
            package_resources[res] += row["Amount"] * count

# 총 보유 자원 계산
total_owned = {
    k: user_owned.get(k, 0) + package_resources.get(k, 0)
    for k in user_owned
}

if st.button("부족 자원 계산"):
    total_needed = {k: 0 for k in user_owned}

    for part, (cur, tar) in user_inputs.items():
        i1 = gear_levels.index(cur)
        i2 = gear_levels.index(tar)
        if i1 >= i2:
            continue
        for level in gear_levels[i1+1:i2+1]:
            for k in total_needed:
                total_needed[k] += resource_dict.get(level, {}).get(k, 0)

    st.markdown("---")
    st.subheader("자원 요약")

    result_data = []
    for k in user_owned:
        result_data.append({
            "자원": k,
            "필요량": total_needed[k],
            "보유량": total_owned.get(k, 0),
            "부족량": max(0, total_needed[k] - total_owned.get(k, 0))
        })

    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df, use_container_width=True)

st.markdown("---")
st.markdown("<div style='text-align:center; color: gray;'>🍋 Made with 💚 by <b>Lime</b></div>", unsafe_allow_html=True)
