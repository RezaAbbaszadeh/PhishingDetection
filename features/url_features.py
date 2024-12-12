from urllib.parse import urlparse


# Define a function to extract features from the URL
def extract_url_features(url):
    parsed = urlparse(url)
    return {
        'domain': parsed.netloc,
        'path': parsed.path,
        'query': parsed.query,
        'scheme': parsed.scheme
    }