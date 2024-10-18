import pandas as pd
import argparse

# Function to load the Excel file
def load_excel(file_path):
    return pd.read_excel(file_path)

# Function to filter the data based on the link section
def filter_by_link_section(data, link_section):
    return data[data['link_section'] == link_section]

# Function to find failing data based on rutting and texture conditions
def find_failing_sections(filtered_data):
    # Rutting > 10 and Texture < 0.8 are considered failing
    failing_data = filtered_data[
        (filtered_data['rutting'] > 10) &
        (filtered_data['texture'] < 0.8)
    ]
    return failing_data

# Function to display the failing sections
def display_failing_sections(failing_data):
    if failing_data.empty:
        print("No failing sections found for the given link section.")
    else:
        print("Failing sections:")
        print(failing_data[['lane', 'chainage_start', 'chainage_end', 'rutting', 'texture']])

# Main function to handle the input and processing
def main():
    # Setup argparse to handle command-line inputs
    parser = argparse.ArgumentParser(description="Excel Data Tool for Finding Failing Sections")
    parser.add_argument("file", help="Path to the Excel file")
    parser.add_argument("link_section", help="Link section to search for failures")

    args = parser.parse_args()

    # Load the Excel file
    data = load_excel(args.file)

    # Filter the data by the link section
    filtered_data = filter_by_link_section(data, args.link_section)

    # Find the failing sections
    failing_data = find_failing_sections(filtered_data)

    # Display the results
    display_failing_sections(failing_data)

if __name__ == "__main__":
    main()
