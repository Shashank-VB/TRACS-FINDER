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
