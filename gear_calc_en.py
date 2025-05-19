import streamlit as st
import pandas as pd
from io import StringIO

# Load CSV data
df = pd.read_csv("data/gear_data.csv")
gear_levels = df["Level"].tolist()

# Resource dictionary
resource_dict = {
    row["Level"]: {
        "Alloy": row["Alloy"],
        "Polish": row["Polish"],
        "Design": row["Design"],
        "Amber": row["Amber"]
    } for _, row in df.iterrows()
}

# English labels (optional)
level_labels = {level: level for level in gear_levels}

# Group gear parts by unit type
gear_groups = {
    "Infantry": ["Coat", "Pants"],
    "Marksman": ["Ring", "Cudgel"],
    "Lancer": ["Hat", "Watch"]
}

gear_parts_eng = {
    "Hat": "Hat",
    "Coat": "Coat",
    "Ring": "Ring",
    "Watch": "Watch",
    "Pants": "Pants",
    "Cudgel": "Cudgel"
}

st.title("Chief Gear Resource Calculator")

user_inputs = {}

st.subheader("Current / Target Level for Each Gear")

for unit_type, parts in gear_groups.items():
    st.markdown(f"#### {unit_type}")
    for part in parts:
        part_label = gear_parts_eng[part]
        cols = st.columns(2)
        with cols[0]:
            cur = st.selectbox(
                f"{part_label} - Current",
                options=gear_levels,
                format_func=lambda x: level_labels.get(x, x),
                index=gear_levels.index("Gold"),
                key=f"{part}_cur"
            )
        with cols[1]:
            tar = st.selectbox(
                f"{part_label} - Target",
                options=gear_levels,
                format_func=lambda x: level_labels.get(x, x),
                index=gear_levels.index("Gold"),
                key=f"{part}_tar"
            )
        user_inputs[part_label] = (cur, tar)

st.markdown("---")
st.subheader("Current Resource Inventory")
res_cols = st.columns(4)
user_owned = {
    "Design": res_cols[0].number_input("Design Plans", min_value=0, value=0),
    "Alloy": res_cols[1].number_input("Alloy", min_value=0, value=0),
    "Polish": res_cols[2].number_input("Polishing Solution", min_value=0, value=0),
    "Amber": res_cols[3].number_input("Lunar Amber", min_value=0, value=0),
}

if st.button("Calculate Deficit"):
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
    st.subheader("Resource Summary")

    result_data = []
    for k in user_owned:
        result_data.append({
            "Resource": k,
            "Required": total_needed[k],
            "Owned": user_owned.get(k, 0),
            "Deficit": max(0, total_needed[k] - user_owned.get(k, 0))
        })

    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df, use_container_width=True)


st.markdown("---")
st.markdown("<div style='text-align:center; color: gray;'>🍋 Made with 💚 by <b>Lime</b></div>", unsafe_allow_html=True)
