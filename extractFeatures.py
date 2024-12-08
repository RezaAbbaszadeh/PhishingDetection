import pandas as pd
from urllib.parse import urlparse
import os
import zipfile
from bs4 import BeautifulSoup

# Load the CSV file
input_csv = 'dataset/dm.csv'  # Replace with the actual file path
output_csv = 'features.csv'
# Paths to the zip files
zip_files = [f"dataset/dataset_part_{i}.zip" for i in range(1, 9)]


# Read the input CSV file
df = pd.read_csv(input_csv)

# Define a function to extract features from the URL
def extract_url_features(url):
    parsed = urlparse(url)
    return {
        'domain': parsed.netloc,
        'path': parsed.path,
        'query': parsed.query,
        'scheme': parsed.scheme
    }


# Define a function to parse the HTML file and extract features
def parse_html_and_extract_features(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else None
        if title:
            title = ' '.join(title.split()).strip()
        num_links = len(soup.find_all('a'))
        num_images = len(soup.find_all('img'))
        return {
            'html_title': title,
            'num_links': num_links,
            'num_images': num_images
        }
    except Exception as e:
        return {
            'html_title': None,
            'num_links': None,
            'num_images': None
        }

# Define a function to search for the HTML file in the zip archives
def extract_website_features(website):
    for zip_file in zip_files:
        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                folder_name = os.path.splitext(os.path.basename(zip_file))[0].replace('_','-')
                file_path_in_zip = f'{folder_name}/{website}'
                if file_path_in_zip in z.namelist():
                    with z.open(file_path_in_zip) as file:
                        html_content = file.read()
                        return parse_html_and_extract_features(html_content)
        except Exception as e:
            continue
    # If file is not found in any zip, return default values
    return {
        'html_title': None,
        'num_links': None,
        'num_images': None
    }


# Define a function to process the created_date column
def process_created_date(created_date):
    try:
        dt = pd.to_datetime(created_date)
        return {'year': dt.year, 'month': dt.month, 'day': dt.day, 'hour': dt.hour, 'minute': dt.minute}
    except Exception as e:
        return {'year': None, 'month': None, 'day': None, 'hour': None, 'minute': None}

# Create an empty list to hold processed rows
processed_data = []

c=0
# Iterate over each row in the dataframe
for index, row in df.iterrows():
    c+=1
    print(c)
    if c==10:
        break
    # Extract features from the URL
    url_features = extract_url_features(row['url'])

    # Extract features from the website
    website_features = extract_website_features(row['website'])

    # Process the created_date column
    date_features = process_created_date(row['created_date'])

    # Combine all features with the rec_id
    processed_row = {
        'rec_id': row['rec_id'],
        **url_features,
        **website_features,
        **date_features
    }

    # Add the processed row to the list
    processed_data.append(processed_row)

# Convert the processed data into a DataFrame
processed_df = pd.DataFrame(processed_data)

# Save the processed data into a new CSV file
processed_df.to_csv(output_csv, index=False)

print(f"Processed data has been saved to {output_csv}")
