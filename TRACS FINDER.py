# TRACS-FINDER import pandas as pd

# Load the Excel file
data = pd.read_excel('your_file.xlsx')
selected_link_section = input("Enter link section: ")

# Filter data by link section
filtered_data = data[data['link_section'] == selected_link_section]
# Apply the failing condition: Rutting > 10 and Texture < 0.8
failing_data = filtered_data[
    (filtered_data['rutting'] > 10) &
    (filtered_data['texture'] < 0.8)
]
if failing_data.empty:
    print("No failing sections found for the given link section.")
else:
    print("Failing sections:")
    # Output the relevant columns, including rutting and texture values
    print(failing_data[['lane', 'chainage_start', 'chainage_end', 'rutting', 'texture']])
