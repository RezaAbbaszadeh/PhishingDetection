import re
from urllib.parse import urlparse
import requests

def extract_url_features(url):
    features = {}

    # Call each feature category function and update the features dictionary
    features.update(extract_whole_url_features(url))
    features.update(extract_domain_features(url))
    features.update(extract_directory_features(url))
    features.update(extract_file_features(url))
    features.update(extract_parameter_features(url))
    features.update(external_metrics(url))

    return features

def extract_whole_url_features(url):
    parsed = urlparse(url)
    path = parsed.path

    special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
    features = {f"qty_{char}_url": url.count(char) for char in special_chars}
    features["qty_tld_url"] = len(urlparse(url).netloc.split('.')[-1]) if '.' in urlparse(url).netloc else 0
    features["length_url"] = len(url)
    features["email_in_url"] = int(bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", url)) and parsed.scheme in ('http', 'https'))

    return features

def extract_domain_features(url):
    parsed = urlparse(url)
    domain = parsed.netloc

    special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
    features = {f"qty_{char}_domain": domain.count(char) for char in special_chars}
    features["qty_vowels_domain"] = sum(1 for char in domain if char.lower() in 'aeiou')
    features["domain_length"] = len(domain)
    features["domain_in_ip"] = int(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", domain) is not None)
    features["server_client_domain"] = int("server" in domain or "client" in domain)

    return features

def extract_directory_features(url):
    parsed = urlparse(url)
    path = parsed.path

    special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
    features = {f"qty_{char}_directory": path.count(char) for char in special_chars}
    features["directory_length"] = len(path)

    return features

def extract_file_features(url):
    parsed = urlparse(url)
    path = parsed.path
    file_name = path.split("/")[-1] if "/" in path else path

    special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
    features = {f"qty_{char}_file": file_name.count(char) for char in special_chars}
    features["file_length"] = len(file_name)

    return features

def extract_parameter_features(url):
    parsed = urlparse(url)
    query = parsed.query

    special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
    features = {f"qty_{char}_params": query.count(char) for char in special_chars}
    features["params_length"] = len(query)
    features["tld_present_params"] = int(any(re.search(rf"\b{tld}\b", query) for tld in [".com", ".net", ".org", ".edu", ".gov", ".io", ".co", ".uk", ".us"]))
    features["qty_params"] = query.count('&') + 1 if query else 0

    return features

def external_metrics(url):
    # Simulate some metrics; replace with API calls or computations where needed
    features = {
        "time_response": -1,  # Placeholder, e.g., use requests.get(url).elapsed.total_seconds()
        "domain_spf": -1,    # Placeholder for SPF record check
        "asn_ip": -1,        # Placeholder for ASN lookup
        "time_domain_activation": -1,
        "time_domain_expiration": -1,
        "qty_ip_resolved": -1,
        "qty_nameservers": -1,
        "qty_mx_servers": -1,
        "ttl_hostname": -1,
        "tls_ssl_certificate": -1,
        "qty_redirects": -1,
        "url_google_index": -1,
        "domain_google_index": -1,
        "url_shortened": int("bit.ly" in url or "tinyurl" in url)
    }

    return features

# Example usage
url = "http://example.com/path/to/resource/index.php?query=reza@gmail.c&gewfwe"
print(len(extract_url_features(url)))
