import streamlit as st
import pandas as pd
from io import BytesIO

# Function to analyze TRACS failure
def analyze_tracs_failure(data_file, link_sections_file):
    # Load data
    df = pd.read_excel(data_file)
    link_sections_df = pd.read_excel(link_sections_file)

    # Ensure "Link section" column exists in the uploaded list
    if "Link section" not in link_sections_df.columns:
        st.error("The uploaded link sections file must contain a 'Link section' column.")
        return None

    # Extract unique link sections
    link_sections = link_sections_df["Link section"].dropna().unique()

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

    # Apply failure conditions
    failing_rows = df_filtered[
        (df_filtered["Max Rut"] >= 15) |
        (df_filtered["Texture"] < 0.8) |
        ((df_filtered["Max LPV 3m"] > 3.9) & (df_filtered["Max LPV 3m"] < 5.5)) |
        ((df_filtered["Max LPV 10m"] > 15.7) & (df_filtered["Max LPV 10m"] < 22.8))
    ]

    return failing_rows if not failing_rows.empty else None

# Streamlit UI
st.title("TRACS Failure Analysis")
st.write("Upload your **data file** and **list of link sections** to analyze.")

# File Uploads
data_file = st.file_uploader("Upload Data File (Excel)", type=["xlsx"])
link_sections_file = st.file_uploader("Upload Link Sections File (Excel)", type=["xlsx"])

if data_file and link_sections_file:
    st.success("Files uploaded successfully. Click the button to analyze.")
    
    if st.button("Analyze TRACS Failure"):
        result = analyze_tracs_failure(data_file, link_sections_file)

        if result is not None:
            st.subheader("TRACS Failing Sections")
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

# Run with: `streamlit run app.py`
