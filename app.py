import streamlit as st
import pandas as pd
import math

# Function to round up values
def roundup(value):
    return math.ceil(value)

# Function to calculate PSV values
def calculate_psv(aadt_value, per_hgvs, year, lanes, site_category, il_value, psv_data):
    if year == 0:
        design_period = 0
    else:
        design_period = (20 + 2025) - year
    
    if per_hgvs >= 11:
        AADT_HGVS = (per_hgvs * (aadt_value / 100))
    else:
        AADT_HGVS = (11 * aadt_value) / 100
    
    total_projected_aadt_hgvs = AADT_HGVS * (1 + 1.54 / 100) ** design_period
    AADT_HGVS = round(AADT_HGVS)
    total_projected_aadt_hgvs = round(total_projected_aadt_hgvs)
    
    lane1 = lane2 = lane3 = lane4 = 0
    lane_details_lane1 = lane_details_lane2 = lane_details_lane3 = lane_details_lane4 = 0
    
    if lanes == 1:
        lane1 = 100
        lane_details_lane1 = total_projected_aadt_hgvs
    elif lanes > 1 and lanes <= 3:
        if total_projected_aadt_hgvs < 5000:
            lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
            lane2 = round(100 - lane1)
        elif total_projected_aadt_hgvs >= 5000 and total_projected_aadt_hgvs < 25000:
            lane1 = round(89 - (0.0014 * total_projected_aadt_hgvs))
            lane2 = 100 - lane1
        else:
            lane1 = 54
            lane2 = 46
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round(total_projected_aadt_hgvs * (lane2 / 100))
    elif lanes >= 4:
        if total_projected_aadt_hgvs <= 10500:
            lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
        elif total_projected_aadt_hgvs > 10500 and total_projected_aadt_hgvs < 25000:
            lane1 = round(75 - (0.0012 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 = round(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
        else:
            lane1 = 45
            lane2 = 54
            lane3 = 1
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round((total_projected_aadt_hgvs - lane_details_lane1) * (lane2 / 100))
        lane_details_lane3 = round(total_projected_aadt_hgvs - (lane_details_lane1 + lane_details_lane2))
    
    # PSV Lookup
    psv_lane1 = psv_data.get((site_category, il_value, lane_details_lane1), "No matching PSV")
    psv_lane2 = psv_data.get((site_category, il_value, lane_details_lane2), "No matching PSV") if lane_details_lane2 > 0 else "NA"
    psv_lane3 = psv_data.get((site_category, il_value, lane_details_lane3), "No matching PSV") if lane_details_lane3 > 0 else "NA"
    
    return {
        "AADT_HGVS": AADT_HGVS,
        "Design Period": design_period,
        "Total Projected AADT HGVs": total_projected_aadt_hgvs,
        "Lane 1 %": lane1,
        "Lane 2 %": lane2,
        "Lane 3 %": lane3,
        "Lane 4 %": lane4,
        "Lane 1 Details": lane_details_lane1,
        "Lane 2 Details": lane_details_lane2,
        "Lane 3 Details": lane_details_lane3,
        "Lane 4 Details": lane_details_lane4,
        "PSV Lane 1": psv_lane1,
        "PSV Lane 2": psv_lane2,
        "PSV Lane 3": psv_lane3
    }

# Streamlit UI
st.title("PSV Calculator from CSV")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
psv_file = st.file_uploader("Upload PSV Excel file", type=["xlsx"])

if uploaded_file is not None and psv_file is not None:
    # Read the input CSV file
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:", df.head())
    
    # Read the PSV data from the uploaded Excel file
    psv_df = pd.read_excel(psv_file, sheet_name="Sheet1")  # Adjust sheet_name if necessary
    psv_data = {}
    
    # Build a dictionary for PSV lookup
    for index, row in psv_df.iterrows():
        key = (row['SiteCategory'], row['IL'], row['LaneDetails'])
        psv_data[key] = row['PSV']
    
    results = []
    for index, row in df.iterrows():
        result = calculate_psv(
            row['AADT'], row['HGV_Percentage'], row['Year'], row['Lanes'], row['SiteCategory'], row['IL'], psv_data
        )
        result['SiteCategory'] = row['SiteCategory']
        result['IL'] = row['IL']
        results.append(result)
    
    output_df = pd.DataFrame(results)
    st.write("Calculated Results:", output_df.head())
    
    # Export output as CSV
    output_csv = output_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV Output",
        data=output_csv,
        file_name="psv_output.csv",
        mime="text/csv"
    )
