import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="🎓 Course Filter Tool", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("Final_Data.csv")
    df.columns = df.columns.str.strip()
    df['courseType'] = df['courseType'].astype(str).str.strip()
    df['country'] = df['country'].astype(str).str.strip()
    df['name'] = df['name'].astype(str).str.strip()
    return df

df = load_data()

# Filter only Undergraduate and Postgraduate
df = df[df['courseType'].isin(['Undergraduate', 'Postgraduate'])]

# 🔝 Top Filter Section
st.markdown("## 🔎 Filter Options")

col1, col2, col3, col4 = st.columns([2, 2, 2, 4])

with col1:
    selected_course_types = st.multiselect(
        "🎓 Course Type", ['Undergraduate', 'Postgraduate'], default=['Undergraduate', 'Postgraduate']
    )

with col2:
    available_countries = sorted(df['country'].dropna().unique())
    selected_countries = st.multiselect("🌍 Country", available_countries)

with col3:
    max_budget = st.slider("💰 Max Tuition (INR)", 500000, 5000000, 2000000, step=50000)

with col4:
    search_keyword = st.text_input("🔍 Course Name", placeholder="e.g., Computer Science").strip().lower()

# Filter logic
course_filter = df['courseType'].isin(selected_course_types) if selected_course_types else np.ones(len(df), dtype=bool)
country_filter = df['country'].isin(selected_countries) if selected_countries else np.ones(len(df), dtype=bool)
name_filter = df['name'].str.lower().str.contains(search_keyword) if search_keyword else np.ones(len(df), dtype=bool)

# Tuition conversion
country_to_inr = {
    'United States': 83,
    'United Kingdom': 105,
    'Ireland': 90,
    'Canada': 61,
    'United Arab Emirates': 22
}
df['conversion_rate'] = df['country'].map(country_to_inr)
df['tuition_in_inr'] = df['tuition'] * df['conversion_rate']
tuition_filter = df['tuition_in_inr'] <= max_budget

# Apply all filters
filtered_df = df[course_filter & country_filter & tuition_filter & name_filter]

# Remove duplicates by course name
filtered_df = filtered_df.drop_duplicates(subset='name')

# Rename for display
filtered_df = filtered_df.rename(columns={
    'courseType': 'Course Type',
    'name': 'Course Name',
    'link': 'Course Link',
    'intake': 'Intake',
    'degree_type': 'Degree Type',
    'entry_requirements': 'Entry Requirements',
    'duration': 'Duration (months)',
    'location': 'Location',
    'tuition_in_inr': 'Tuition (INR)'
})

# Format tuition fee in Indian comma style (e.g., 12,00,000)
filtered_df['Tuition (INR)'] = filtered_df['Tuition (INR)'].apply(lambda x: f"{int(x):,}".replace(",", "X").replace(".", ",").replace("X", ","))

# Columns to display
columns_to_display = [
    'Course Type', 'Course Name', 'Course Link', 'Intake',
    'Degree Type', 'Entry Requirements', 'Duration (months)',
    'Location', 'Tuition (INR)'
]

# Display section
st.markdown("## 📋 Filtered Course List")
st.markdown(f"🎯 **{len(filtered_df)} matching courses found**")

st.data_editor(
    filtered_df[columns_to_display],
    use_container_width=True,
    hide_index=True,
    disabled=True
)

# Download CSV
st.download_button("📥 Download Filtered Courses",
                   filtered_df[columns_to_display].to_csv(index=False),
                   "filtered_courses.csv",
                   "text/csv")
