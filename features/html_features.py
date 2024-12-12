from bs4 import BeautifulSoup
import zipfile

# Paths to the zip files
zip_files = [(f'dataset-part-{i}', zipfile.ZipFile(f"dataset/dataset_part_{i}.zip", 'r')) for i in range(1, 9)]


default_values = {
        'html_title': None,
        'num_links': None,
        'num_images': None
    }

def extract_website_features(website):
    for base_folder, zip_file in zip_files:
        file_path_in_zip = f'{base_folder}/{website}'
        if file_path_in_zip in zip_file.namelist():
            with zip_file.open(file_path_in_zip) as file:
                html_content = file.read()
                return parse_html_and_extract_features(html_content)
    # If file is not found in any zip, return default values
    return default_values


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
        return default_values
