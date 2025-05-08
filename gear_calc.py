import streamlit as st
import pandas as pd

# Load gear data
df = pd.read_csv("data/gear_data.csv")
gear_levels = df["Level"].tolist()

resource_dict = {
    row["Level"]: {
        "Alloy": row["Alloy"],
        "Polish": row["Polish"],
        "Design": row["Design"],
        "Amber": row["Amber"]
    } for _, row in df.iterrows()
}

# Korean labels
gear_groups = {
    "방패병": ["Coat", "Pants"],
    "궁병": ["Ring", "Cudgel"],
    "창병": ["Hat", "Watch"]
}
gear_parts_kor = {
    "Hat": "모자", "Coat": "상의", "Ring": "반지",
    "Watch": "시계", "Pants": "하의", "Cudgel": "지팡이"
}

st.title("치프 기어 부족 자원 계산기")

user_inputs = {}
st.subheader("장비별 현재/목표 등급 선택")

for troop_type, parts in gear_groups.items():
    st.markdown(f"#### {troop_type}")
    for part in parts:
        part_kor = gear_parts_kor[part]
        cols = st.columns(2)
        with cols[0]:
            cur = st.selectbox(f"{part_kor} - 현재", options=gear_levels, index=gear_levels.index("Gold"), key=f"{part}_cur")
        with cols[1]:
            tar = st.selectbox(f"{part_kor} - 목표", options=gear_levels, index=gear_levels.index("Gold"), key=f"{part}_tar")
        user_inputs[part_kor] = (cur, tar)

st.markdown("---")
st.subheader("현재 보유 자원 입력")
res_cols = st.columns(4)
user_owned = {
    "Design": res_cols[0].number_input("설계도면", min_value=0, value=0),
    "Alloy": res_cols[1].number_input("합금", min_value=0, value=0),
    "Polish": res_cols[2].number_input("윤활제", min_value=0, value=0),
    "Amber": res_cols[3].number_input("앰버", min_value=0, value=0),
}

# Optional: package input
packages_df = pd.read_csv("data/packages.csv")
with st.expander("선택사항: 패키지 구매 입력"):
    st.warning("⚠️ 패키지 데이터는 아직 업데이트가 필요한 예시입니다. 사용에 유의하세요!!")
    package_groups = {
        "Artisans": ["Sublime", "Exquisite", "Classic"],
        "Dawn Market": ["DawnMarket"]
    }
    user_package_inputs = {}
    for group, categories in package_groups.items():
        st.markdown(f"**{group}**")
        for cat in categories:
            for price in ["$5", "$10", "$20", "$50", "$100"]:
                key = f"{cat}_{price}"
                user_package_inputs[key] = st.number_input(f"{cat} {price}", min_value=0, step=1, key=key)

# ✅ Show package content outside of expander
if st.checkbox("패키지 구성 보기"):
    st.dataframe(packages_df, use_container_width=True)

# Main calculation
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

    # Add package resources
    for key, count in user_package_inputs.items():
        if count > 0:
            cat, price = key.split("_")
            rows = packages_df[(packages_df["Category"] == cat) & (packages_df["Package"] == price)]
            for _, row in rows.iterrows():
                res = row["Resource"]
                amt = row["Amount"] * count
                if res in total_needed:
                    user_owned[res] += amt

    # 결과 출력
    st.markdown("---")
    st.subheader("결과 요약")
    name_map = {"Design": "설계도면", "Alloy": "합금", "Polish": "윤활제", "Amber": "앰버"}
    result_df = pd.DataFrame([
        {
            "자원": name_map.get(k, k),
            "총 필요량": total_needed[k],
            "보유량": user_owned.get(k, 0),
            "부족량": max(0, total_needed[k] - user_owned.get(k, 0))
        } for k in user_owned
    ])
    st.dataframe(result_df, use_container_width=True)
