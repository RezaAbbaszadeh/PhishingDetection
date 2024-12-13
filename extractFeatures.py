import pandas as pd
import os
from features.url_features import extract_url_features
from features.html_features import extract_website_features

input_csv = 'dataset/dm.csv' 

# Read the input CSV file
df = pd.read_csv(input_csv)


# Define a function to process the created_date column
def process_created_date(created_date):
    try:
        dt = pd.to_datetime(created_date)
        return {'year': dt.year, 'month': dt.month, 'day': dt.day, 'hour': dt.hour, 'minute': dt.minute}
    except Exception as e:
        return {'year': None, 'month': None, 'day': None, 'hour': None, 'minute': None}

# Create an empty list to hold processed rows
url_data = []
html_data = []

start_index, end_index = 30000,80000
for index, row in df[start_index:end_index].iterrows():
    # print(c)
    if index%1000==0:
        print(index)
    # Extract features from the URL
    url_features = extract_url_features(row['url'])

    # Extract features from the website
    website_features = extract_website_features(row['website'], row['url'])

    # Process the created_date column
    # date_features = process_created_date(row['created_date'])

    processed_url_row = {
        'rec_id': row['rec_id'],
        **url_features,
        'phishing': row['result']
    }
    processed_html_row = {
        'rec_id': row['rec_id'],
        **website_features,
        'phishing': row['result']
    }

    # Add the processed row to the list
    url_data.append(processed_url_row)
    html_data.append(processed_html_row)

# Convert the processed data into a DataFrame
url_df = pd.DataFrame(url_data)
html_df = pd.DataFrame(html_data)

url_df.to_csv(f'features/url_features_{start_index}_{end_index}.csv', index=False)
html_df.to_csv(f'features/html_features_{start_index}_{end_index}.csv', index=False)
