import gspread
import json

def courses_to_json(url: str):
    account = gspread.service_account("././google-credentials.json")
    # Open spreadsheet by name:
    spreadsheet = account.open_by_url(url)
    # Open sheet by name:
    worksheet = spreadsheet.get_worksheet(0)  # Assuming the first worksheet

    all_values = worksheet.get_all_values()

    # Extract the first row as keys and the rest of the rows as values
    keys = all_values[0]
    values = all_values[1:]

    # Create a list for stroing all rows
    courses = []
    for row in values:
        data_dict = {key: value for key, value in zip(keys, row)}
        courses.append(data_dict)

    return courses

if __name__ == "__main__":
    url = "https://docs.google.com/spreadsheets/d/1Zpk8kXLrMx3dboCleZHj4AW-_8Mr8q-jpvScwHZnyBI/edit?usp=sharing"
    courses = courses_to_json(url)
    
    # Save the dictionary as JSON
    with open('../files/output.json', 'w') as file:
        json.dump(courses, file, indent=4, ensure_ascii=False)