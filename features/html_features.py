from bs4 import BeautifulSoup
import zipfile
import re
from urllib.parse import urlparse

zip_files = [(f'dataset-part-{i}', zipfile.ZipFile(f"dataset/dataset_part_{i}.zip", 'r')) for i in range(1, 9)]
default_values = {
        'html_title': None,
        'num_links': None,
        'num_images': None
    }

def extract_website_features(website, url):
    for base_folder, zip_file in zip_files:
        file_path_in_zip = f'{base_folder}/{website}'
        if file_path_in_zip in zip_file.namelist():
            with zip_file.open(file_path_in_zip) as file:
                html_content = file.read()
                return parse_html_and_extract_features(html_content, url)
    # If file is not found in any zip, return default values
    return default_values

def parse_html_and_extract_features(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc

    features = {}
    features.update(extract_script_css_img_anchor_features(soup)) # F1,F2,F3,F4
    features.update(extract_empty_and_null_hyperlinks_features(soup)) # F7,F8,F9
    features.update(extract_internal_external_features(soup, base_domain)) # F10,F11,F12
    features.update(extract_login_form_features(soup, base_domain)) # F14,F15

    return features

def extract_script_css_img_anchor_features(soup):
    total_hyperlinks = len(soup.find_all(['a', 'link', 'script', 'img']))
    script_files = soup.find_all('script', src=True)
    css_files = soup.find_all('link', rel='stylesheet')
    img_files = soup.find_all('img', src=True)
    anchor_files = soup.find_all('a', href=True)

    return {
        'script_files_ratio': len(script_files) / total_hyperlinks if total_hyperlinks > 0 else 0,
        'css_files_ratio': len(css_files) / total_hyperlinks if total_hyperlinks > 0 else 0,
        'image_files_ratio': len(img_files) / total_hyperlinks if total_hyperlinks > 0 else 0,
        'anchor_files_ratio': len(anchor_files) / total_hyperlinks if total_hyperlinks > 0 else 0
    }

def extract_empty_and_null_hyperlinks_features(soup):
    all_tags = soup.find_all(['a', 'script', 'link', 'img'])
    total_hyperlinks = len(all_tags)
    empty_anchor_count = 0
    null_hyperlink_count = 0

    for tag in all_tags:
        if tag.name == 'a':
            href = tag.get('href')
            if href is None:
                empty_anchor_count += 1
            if href is None or href in ['', '#', '#content', 'javascript:void(0);']:
                null_hyperlink_count += 1
        else:
            src_or_href = tag.get('src') or tag.get('href')
            if src_or_href is None or src_or_href in ['', '#', '#content', 'javascript:void(0);']:
                null_hyperlink_count += 1

    return {
        'empty_anchor_ratio': empty_anchor_count / total_hyperlinks if total_hyperlinks > 0 else 0,
        'null_hyperlink_ratio': null_hyperlink_count / total_hyperlinks if total_hyperlinks > 0 else 0,
        'total_hyperlinks': total_hyperlinks
    }

def extract_internal_external_features(soup, base_domain):
    all_tags = soup.find_all(['a', 'script', 'link', 'img', 'form'])
    total_hyperlinks = len(all_tags)
    internal_hyperlinks = 0
    external_hyperlinks = 0

    for tag in all_tags:
        url = tag.get('href') or tag.get('src') or tag.get('action')
        if url:
            parsed_url = urlparse(url)
            if parsed_url.netloc == "" or base_domain in parsed_url.netloc:
                internal_hyperlinks += 1
            else:
                external_hyperlinks += 1

    return {
        'internal_hyperlink_ratio': internal_hyperlinks / total_hyperlinks if total_hyperlinks > 0 else 0,
        'external_hyperlink_ratio': external_hyperlinks / total_hyperlinks if total_hyperlinks > 0 else 0,
        'external_to_internal_ratio': external_hyperlinks / internal_hyperlinks if internal_hyperlinks > 0 else 0
    }

def extract_login_form_features(soup, base_domain):
    forms = soup.find_all('form')
    total_forms = len(forms)
    suspicious_forms = 0

    for form in forms:
        action_url = form.get('action')
        if action_url is None or action_url.strip() == "":
            suspicious_forms += 1
        else:
            parsed_action_url = urlparse(action_url)
            if not parsed_action_url.netloc or base_domain not in parsed_action_url.netloc:
                suspicious_forms += 1

    return {
        'total_forms': total_forms,
        'suspicious_form_ratio': suspicious_forms / total_forms if total_forms > 0 else 0
    }




html_example = """
<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
</head>
<body>
    <img src="image.png" alt="Example Image">
    <a href="http://example.com/page1">Link 1</a>
    <a href="#content">Null Link</a>
    <a href="javascript:void(0);">JavaScript Link</a>
    <form action="http://example.com/login">
        <input type="text" name="username">
        <input type="password" name="password">
    </form>
    <form action="http://malicious.com/submit">
        <input type="text" name="user">
    </form>
</body>
</html>
"""

# Call the function
features = parse_html_and_extract_features(html_example, 'http://malicious.com')

# Print the extracted features
print(len(features))
