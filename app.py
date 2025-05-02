import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="🎓 Course Filter Tool", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("combine.csv")
    df.columns = df.columns.str.strip()
    df['courseType'] = df['courseType'].astype(str).str.strip()
    df['country'] = df['country'].astype(str).str.strip()
    df['name'] = df['name'].astype(str).str.strip()
    df['university_name'] = df['university_name'].astype(str).str.strip()
    return df

df = load_data()

# Convert duration to years
df['duration'] = (df['duration'] / 12).round(1)

# Filter only Undergraduate and Postgraduate
df = df[df['courseType'].isin(['Undergraduate', 'Postgraduate'])]

# 🔝 Top Filter Section
st.markdown("## 🔎 Filter Options")

col1, col2, col3, col4 = st.columns([2, 2, 2, 4])

with col1:
    selected_course_types = st.multiselect(
        "🎓 Course Type", ['Undergraduate', 'Postgraduate'], default=['Postgraduate']
    )

with col2:
    available_countries = sorted(df['country'].dropna().unique())
    selected_countries = st.multiselect("🌍 Country", available_countries)

with col3:
    if selected_countries:
        filtered_unis = df[df['country'].isin(selected_countries)]['university_name'].dropna().unique()
    else:
        filtered_unis = df['university_name'].dropna().unique()

    selected_universities = st.multiselect("🏛️ University", sorted(filtered_unis))

with col4:
    search_keyword = st.text_input("🔍 Course Name", placeholder="e.g., Computer Science").strip().lower()

# Filter logic
course_filter = df['courseType'].isin(selected_course_types) if selected_course_types else np.ones(len(df), dtype=bool)
country_filter = df['country'].isin(selected_countries) if selected_countries else np.ones(len(df), dtype=bool)
university_filter = df['university_name'].isin(selected_universities) if selected_universities else np.ones(len(df), dtype=bool)
name_filter = df['name'].str.lower().str.contains(search_keyword) if search_keyword else np.ones(len(df), dtype=bool)

# Tuition conversion to INR
country_to_inr = {
    'United States': 83,
    'United Kingdom': 105,
    'Ireland': 90,
    'Canada': 61,
    'United Arab Emirates': 22
}
#df['conversion_rate'] = df['country'].map(country_to_inr)
#df['tuition_in_inr'] = df['tuition'] * df['conversion_rate']

# Apply all filters
filtered_df = df[course_filter & country_filter & university_filter & name_filter]

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
    'duration': 'Duration (years)',
    'location': 'Location',
    'university_name': 'University'
})

# Columns to display
columns_to_display = [
    'University', 'Course Type', 'Course Name', 'Course Link', 'Intake',
    'Degree Type', 'Entry Requirements', 'Duration (years)', 'Location'
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
