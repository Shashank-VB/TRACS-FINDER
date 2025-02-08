import pandas as pd
import math
import streamlit as st
import io

# Title
st.title("Polished Stone Value (PSV) Calculator Results")

# Input parameters
st.sidebar.title("Polished Stone Value (PSV) Calculator")
st.sidebar.header("Enter values:")

# Create a form to enter multiple link sections with input parameters
link_sections_input = st.sidebar.text_area("Enter Link Sections (separate with commas)", "")
link_section_list = [link.strip() for link in link_sections_input.split(',') if link.strip()]

# Initialize the DataFrame to hold all link section results
all_results = []

# PSV Table (to be uploaded by the user)
uploaded_file = st.sidebar.file_uploader("Upload your Excel file with PSV table", type=["xlsx"])

def roundup(value):
    return math.ceil(value)

# Process each link section
for link_section in link_section_list:
    # User inputs for the current link section
    aadt_value = st.sidebar.number_input(f"Enter AADT for {link_section}:", min_value=0, key=f"aadt_{link_section}")
    per_hgvs = st.sidebar.number_input(f"Enter % of HGVs for {link_section}:", min_value=0, key=f"per_hgvs_{link_section}")
    year = st.sidebar.number_input(f"Enter Year for {link_section}:", min_value=0, key=f"year_{link_section}")
    lanes = st.sidebar.number_input(f"Enter number of lanes for {link_section}:", min_value=1, key=f"lanes_{link_section}")

    # Design period
    if year == 0:
        design_period = 0
    else:
        design_period = ((20 + 2025) - year)

    # AADT_HGVS Calculation
    if per_hgvs >= 11:
        AADT_HGVS = (per_hgvs * (aadt_value / 100))
    else:
        AADT_HGVS = (11 * aadt_value) / 100

    total_projected_aadt_hgvs = AADT_HGVS * (1 + 1.54 / 100) ** design_period
    AADT_HGVS = round(AADT_HGVS)
    total_projected_aadt_hgvs = round(total_projected_aadt_hgvs)

    # Lane calculation
    lane1, lane2, lane3, lane4 = 0, 0, 0, 0
    lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4 = 0, 0, 0, 0
    
    if lanes == 1:
        lane1 = 100
        lane_details_lane1 = total_projected_aadt_hgvs
    elif lanes > 1 and lanes <= 3:
        if total_projected_aadt_hgvs < 5000:
            lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
            lane2 = round(100 - lane1)
        elif total_projected_aadt_hgvs >= 5000 and total_projected_aadt_hgvs < 25000:
            lane1 = round(89 - (0.0014 * total_projected_aadt_hgvs))
            lane2 = round(100 - lane1)
        else:
            lane1 = 54
            lane2 = 100 - 54
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round(total_projected_aadt_hgvs * (lane2 / 100))

    elif lanes >= 4:
        if total_projected_aadt_hgvs <= 10500:
            lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
            lane4 = 0
        elif total_projected_aadt_hgvs > 10500 and total_projected_aadt_hgvs < 25000:
            lane1 = round(75 - (0.0012 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
            lane4 = 0
        else:
            lane1 = 45
            lane2 = 54
            lane3 = 100 - 54
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round((total_projected_aadt_hgvs - lane_details_lane1) * (lane2 / 100))
        lane_details_lane3 = round(total_projected_aadt_hgvs - (lane_details_lane1 + lane_details_lane2))

    # PSV calculation (with placeholders if no data is uploaded)
    result, result2, result3 = 'NA', 'NA', 'NA'

    # If PSV table is uploaded, read and search for the matching values
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        # Example logic: using site category and IL value from the uploaded table
        value1 = st.sidebar.text_input(f"Enter Site Category for {link_section}:")
        value2 = st.sidebar.number_input(f"Enter IL value for {link_section}:")
        
        # Placeholder search logic based on the uploaded table
        # Assume `df` contains columns `SiteCategory`, `IL`, and columns with ranges for PSV calculation
        if not df.empty:
            # For Lane 1 PSV (example of how to look up the value)
            for col in df.columns:
                if '-' in col:
                    col_range = list(map(int, col.split('-')))
                    if col_range[0] <= lane_details_lane1 <= col_range[1]:
                        range_column = col
                        filtered_df = df[(df['SiteCategory'] == value1) & (df['IL'] == value2)]
                        if not filtered_df.empty:
                            result = filtered_df.iloc[0][range_column]
                            break
        # Add similar logic for Lane 2 and Lane 3 if needed

    # Store the results in the list for all link sections
    all_results.append({
        'Link Section': link_section,
        'AADT_HGVS': AADT_HGVS,
        'Design Period': design_period,
        'Total Projected AADT HGVs': total_projected_aadt_hgvs,
        'Lane 1': lane1,
        'Lane 2': lane2,
        'Lane 3': lane3,
        'Lane 4': lane4,
        'Lane 1 Details': lane_details_lane1,
        'Lane 2 Details': lane_details_lane2,
        'Lane 3 Details': lane_details_lane3,
        'Lane 4 Details': lane_details_lane4,
        'PSV Lane 1': result,
        'PSV Lane 2': result2,
        'PSV Lane 3': result3,
    })

# Convert the results list into a DataFrame
df_results = pd.DataFrame(all_results)

# Display the DataFrame on the Streamlit page
st.write("PSV Results Output", df_results)

# Convert the DataFrame to CSV
csv_data = df_results.to_csv(index=False)

# Create a download button for the CSV file
st.download_button(
    label="Download Results as CSV",
    data=csv_data,
    file_name='psv_results.csv',
    mime='text/csv'
)
