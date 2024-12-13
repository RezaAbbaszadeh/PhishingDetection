from bs4 import BeautifulSoup
import zipfile
import re
from urllib.parse import urlparse
from collections import Counter

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

    # https://doi.org/10.1038/s41598-022-10841-5
    # (https://www.nature.com/articles/s41598-022-10841-5)
    features.update(extract_script_css_img_anchor_features(soup)) # F1,F2,F3,F4
    features.update(extract_empty_and_null_hyperlinks_features(soup)) # F7,F8,F9
    features.update(extract_internal_external_features(soup, base_domain)) # F10,F11,F12
    features.update(extract_login_form_features(soup, base_domain)) # F14,F15

    # https://doi.org/10.1016/j.ins.2019.01.064
    features.update(extract_url_features(soup, url))
    features.update(extract_form_features(soup, url))
    features.update(extract_hyperlink_and_redirection_features(soup, url))
    features.update(extract_javascript_html_features(soup))
    features.update(extract_miscellaneous_features(soup, url))

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
            try:
                parsed_url = urlparse(url)
                if parsed_url.netloc == "" or base_domain in parsed_url.netloc:
                    internal_hyperlinks += 1
                else:
                    external_hyperlinks += 1
            except:
                pass

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

def extract_url_features(soup, base_url):
    base_domain = urlparse(base_url).netloc

    # Extract anchor tags (hyperlinks)
    anchor_tags = soup.find_all('a', href=True)
    total_hyperlinks = len(anchor_tags)
    external_hyperlinks = 0

    for tag in anchor_tags:
        href = tag.get('href')
        try:
            if href and base_domain not in urlparse(href).netloc:
                external_hyperlinks += 1
        except:
            pass

    # Extract resource tags (scripts, images, stylesheets)
    resource_tags = soup.find_all(['script', 'img', 'link'], src=True)
    total_resources = len(resource_tags)
    external_resources = 0

    for tag in resource_tags:
        try:
            src_or_href = tag.get('src') or tag.get('href')
            if src_or_href and base_domain not in urlparse(src_or_href).netloc:
                external_resources += 1
        except:
            pass

    # Check for external favicon
    favicon = soup.find('link', rel='icon')
    favicon_external = favicon and 'href' in favicon and base_domain not in urlparse(favicon['href']).netloc

    return {
        'PctExtHyperlinks': external_hyperlinks / total_hyperlinks if total_hyperlinks > 0 else 0,
        'PctExtResourceUrls': external_resources / total_resources if total_resources > 0 else 0,
        'ExtFavicon': int(bool(favicon_external))
    }

def extract_form_features(soup, base_url):
    base_domain = urlparse(base_url).netloc
    forms = soup.find_all('form')
    insecure_forms = 0
    relative_forms = 0
    external_forms = 0
    abnormal_forms = 0

    for form in forms:
        action = form.get('action', '')
        if not action:
            abnormal_forms += 1
        elif action.startswith('#') or 'javascript:' in action or 'about:blank' in action:
            abnormal_forms += 1
        elif base_domain not in urlparse(action).netloc:
            external_forms += 1
        elif action.startswith('/'):
            relative_forms += 1
        if not action.startswith('https://'):
            insecure_forms += 1

    return {
        'InsecureForms': int(insecure_forms > 0),
        'RelativeFormAction': int(relative_forms > 0),
        'ExtFormAction': int(external_forms > 0),
        'AbnormalFormAction': int(abnormal_forms > 0)
    }

def extract_hyperlink_and_redirection_features(soup, base_url):
    # Function to calculate the percentage of null self-redirect hyperlinks
    def calculate_pct_null_self_redirect_links(soup, base_url):
        all_links = soup.find_all('a')
        null_self_redirect_links = 0

        for link in all_links:
            href = link.get('href', '')
            if href in ['#', '', base_url, 'javascript:void(0);']:
                null_self_redirect_links += 1

        total_links = len(all_links)
        return null_self_redirect_links / total_links if total_links > 0 else 0

    # Function to check frequent domain name mismatch
    def check_frequent_domain_mismatch(soup, base_url):
        base_domain = urlparse(base_url).netloc

        # Extract all domains from href attributes
        all_domains = []
        for tag in soup.find_all('a', href=True):
            href = tag.get('href')
            if href:
                try:
                    parsed_url = urlparse(href)
                    if parsed_url.netloc:
                        all_domains.append(parsed_url.netloc)
                except:
                    pass

        # Count occurrences of each domain
        domain_counts = Counter(all_domains)
        most_frequent_domain = domain_counts.most_common(1)

        if most_frequent_domain:
            most_frequent_domain = most_frequent_domain[0][0]
            return most_frequent_domain != base_domain  # True if mismatch, False otherwise
        return False  # No domains to compare
    
    return {
        'PctNullSelfRedirectHyperlinks': calculate_pct_null_self_redirect_links(soup, base_url),
        'FrequentDomainNameMismatch': int(check_frequent_domain_mismatch(soup, base_url))
    }

def extract_javascript_html_features(soup):
    # Find all scripts and tags with attributes
    scripts = soup.find_all('script')
    tags_with_attrs = soup.find_all(attrs=True)

    # Detect Fake Links in Status Bar
    fake_link_in_status_bar = False
    for tag in tags_with_attrs:
        if 'onmouseover' in tag.attrs:
            # Check if onMouseOver contains JavaScript modifying the status bar
            js_code = tag.attrs.get('onmouseover', '')
            if 'window.status' in js_code or 'status=' in js_code:
                fake_link_in_status_bar = True
                break

    for script in scripts:
        if 'onMouseOver' in script.text and ('window.status' in script.text or 'status=' in script.text):
            fake_link_in_status_bar = True
            break

    # Detect Right-Click Disabled
    right_click_disabled = any("contextmenu" in script.text for script in scripts) or \
                           any("oncontextmenu" in tag.attrs for tag in tags_with_attrs)

    # Detect Popup Window Creation
    popup_window = any("window.open" in script.text for script in scripts)

    # Detect Submitting Information to Email
    submit_to_email = any('mailto:' in (tag.get('href', '') or '') for tag in soup.find_all('a', href=True)) or \
                      soup.find_all(string=lambda text: 'mailto:' in text if text else False)

    # Count Iframes and Frames
    iframe_or_frame_count = len(soup.find_all(['iframe', 'frame']))

    return {
        'FakeLinkInStatusBar': int(fake_link_in_status_bar),
        'RightClickDisabled': int(right_click_disabled),
        'PopUpWindow': int(popup_window),
        'SubmitInfoToEmail': int(bool(submit_to_email)),
        'IframeOrFrame': iframe_or_frame_count
    }



def extract_miscellaneous_features(soup, base_url):
    features = {}
    parsed_url = urlparse(base_url)
    base_domain = parsed_url.netloc

    # Feature 40: IframeOrFrame
    iframe_or_frame_count = len(soup.find_all(['iframe', 'frame']))
    features['IframeOrFrame'] = int(iframe_or_frame_count > 0)

    # Feature 41: MissingTitle
    title = soup.find('title')
    features['MissingTitle'] = int(title is None or title.text.strip() == '')

    # Feature 42: ImagesOnlyInForm
    forms = soup.find_all('form')
    images_only_in_forms = 0
    for form in forms:
        form_text = ''.join(form.stripped_strings).strip()
        if not form_text and form.find('img'):
            images_only_in_forms += 1
    features['ImagesOnlyInForm'] = int(images_only_in_forms > 0)

    # Feature 47: ExtMetaScriptLinkRT
    external_meta_script_links = 0
    meta_script_link_tags = soup.find_all(['meta', 'script', 'link'])
    total_meta_script_links = len(meta_script_link_tags)
    for tag in meta_script_link_tags:
        src_or_href = tag.get('src') or tag.get('href')
        if src_or_href and base_domain not in urlparse(src_or_href).netloc:
            external_meta_script_links += 1
    features['ExtMetaScriptLinkRT'] = external_meta_script_links / total_meta_script_links if total_meta_script_links > 0 else 0

    return features





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
# features = parse_html_and_extract_features(html_example, 'http://malicious.com')

# Print the extracted features
# print(len(features))
