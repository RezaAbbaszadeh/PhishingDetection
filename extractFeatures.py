import pandas as pd
import os
from features.url_features import extract_url_features
from features.html_features import extract_website_features

input_csv = 'dataset/dm.csv' 
output_csv = 'features/features.csv'

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
processed_data = []

c=0
# Iterate over each row in the dataframe
for index, row in df.iterrows():
    c+=1
    # print(c)
    if c==1000:
        print(c)
    # Extract features from the URL
    url_features = extract_url_features(row['url'])

    # Extract features from the website
    website_features = extract_website_features(row['website'], row['url'])

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
