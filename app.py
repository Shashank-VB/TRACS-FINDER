import streamlit as st
import pandas as pd
from io import BytesIO

# Function to analyze TRACS failure
def analyze_tracs_failure(data_file, link_sections_file):
    try:
        # Attempt to read CSV files with different encodings
        df = pd.read_csv(data_file, encoding='ISO-8859-1')
        link_sections_df = pd.read_csv(link_sections_file, encoding='ISO-8859-1')
    except Exception as e:
        st.error(f"Error reading the files: {e}")
        return None

    # Clean column names by stripping any leading/trailing spaces
    df.columns = df.columns.str.strip()
    link_sections_df.columns = link_sections_df.columns.str.strip()

    # Ensure "Link section" column exists in the uploaded list
    if "Link section" not in link_sections_df.columns:
        st.error("The uploaded link sections file must contain a 'Link section' column.")
        return None

    # Extract unique link sections
    link_sections = pd.Series(link_sections_df["Link section"].dropna().unique())  # Convert to pandas Series

    # Ensure required columns exist in the main data file
    required_columns = [
        "Link section", "Start Chainage", "End Chainage", "Lane", 
        "Max Rut", "Texture", "Max LPV 3m", "Max LPV 10m"
    ]
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing columns in data file: {', '.join(missing_cols)}")
        return None

    # Filter data based on link sections
    df_filtered = df[df["Link section"].isin(link_sections)]

    if df_filtered.empty:
        st.warning("No matching link sections found in the data file.")
        return None

    # Initialize a new column for the failure criterion
    df_filtered['Failure Criterion'] = None

    # Apply failure conditions and assign failure criteria
    df_filtered.loc[df_filtered["Max Rut"] >= 15, 'Failure Criterion'] = 'Rut Failure'
    df_filtered.loc[df_filtered["Texture"] < 0.8, 'Failure Criterion'] = 'Texture Failure'
    df_filtered.loc[
        (df_filtered["Max LPV 3m"] > 3.9) & (df_filtered["Max LPV 3m"] < 5.5), 
        'Failure Criterion'] = 'LPV 3m Failure'
    df_filtered.loc[
        (df_filtered["Max LPV 10m"] > 15.7) & (df_filtered["Max LPV 10m"] < 22.8), 
        'Failure Criterion'] = 'LPV 10m Failure'

    # Filter rows where any failure criterion is applied
    failing_rows = df_filtered[df_filtered['Failure Criterion'].notnull()]

    # Handle non-failing sections only if failing_rows is not empty
    if not failing_rows.empty:
        non_failing_sections = link_sections[~link_sections.isin(failing_rows["Link section"])]
    else:
        non_failing_sections = link_sections

    # Create rows for non-failing sections
    no_failure_rows = pd.DataFrame({
        "Link section": non_failing_sections,
        "Start Chainage": ["N/A"] * len(non_failing_sections),
        "End Chainage": ["N/A"] * len(non_failing_sections),
        "Lane": ["N/A"] * len(non_failing_sections),
        "Max Rut": ["N/A"] * len(non_failing_sections),
        "Texture": ["N/A"] * len(non_failing_sections),
        "Max LPV 3m": ["N/A"] * len(non_failing_sections),
        "Max LPV 10m": ["N/A"] * len(non_failing_sections),
        "Failure Criterion": ["NO TRACS FAILURE"] * len(non_failing_sections)
    })

    # Combine failing rows and non-failing rows
    all_results = pd.concat([failing_rows, no_failure_rows])

    # Reorder columns to place "Failure Criterion" to the right of "Link section"
    column_order = [
        "Link section", "Failure Criterion", "Start Chainage", "End Chainage", "Lane",
        "Max Rut", "Texture", "Max LPV 3m", "Max LPV 10m"
    ]
    all_results = all_results[column_order]

    return all_results if not all_results.empty else None

# Streamlit UI
st.title("TRACS Failure Analysis")
st.write("Upload your **data file (CSV format)** and **list of link sections** to analyze.")

# File Uploads
data_file = st.file_uploader("Upload Data File (CSV)", type=["csv"])
link_sections_file = st.file_uploader("Upload Link Sections File (CSV)", type=["csv"])

if data_file and link_sections_file:
    st.success("Files uploaded successfully. Click the button to analyze.")
    
    if st.button("Analyze TRACS Failure"):
        result = analyze_tracs_failure(data_file, link_sections_file)

        if result is not None:
            st.subheader("TRACS Failure Analysis Results")
            st.dataframe(result)  # Show data in table

            # Convert DataFrame to CSV
            csv_buffer = BytesIO()
            result.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            st.download_button(
                label="Download TRACS Failure Report",
                data=csv_buffer,
                file_name="TRACS_Failure_Report.csv",
                mime="text/csv"
            )
        else:
            st.success("No TRACS failure detected!")
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
