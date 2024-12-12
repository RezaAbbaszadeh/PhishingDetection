import re
from urllib.parse import urlparse
import requests

top_tlds = [".com", ".org", ".net", ".int", ".edu", ".gov", ".mil", ".co", ".io", ".biz", ".info", ".us", ".uk", ".de", ".cn", ".fr", ".au", ".ru", ".jp", ".in"]

def extract_url_features(url):
    features = {}

    # Call each feature category function and update the features dictionary
    # https://doi.org/10.1016/j.dib.2020.106438.
    # https://www.sciencedirect.com/science/article/pii/S2352340920313202
    features.update(extract_whole_url_features(url))
    features.update(extract_domain_features(url))
    features.update(extract_directory_features(url))
    features.update(extract_file_features(url))
    features.update(extract_parameter_features(url))
    features.update(external_metrics(url))

    # https://doi.org/10.1016/j.ins.2019.01.064.
    # (https://www.sciencedirect.com/science/article/pii/S0020025519300763)
    features.update(extract_features_from_hybrid_paper(url))

    # https://doi.org/10.1016/j.eswa.2014.03.019
    # (https://www.sciencedirect.com/science/article/pii/S0957417414001481)
    features.update(features_from_associative_classification_paper(url))

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
    features["subdomain_level"] = domain.count('.')

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
    features["tld_present_params"] = int(any(re.search(rf"\b{tld}\b", query) for tld in top_tlds))
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

def extract_features_from_hybrid_paper(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    query = parsed.query

    features = {
        "num_dots": url.count('.'),
        "subdomain_level": domain.count('.'),
        "path_level": path.count('/') - 1,
        "url_length": len(url),
        "num_dash": url.count('-'),
        "num_dash_in_hostname": domain.count('-'),
        "at_symbol": int('@' in url),
        "tilde_symbol": int('~' in url),
        "num_underscore": url.count('_'),
        "num_percent": url.count('%'),
        "num_query_components": query.count('&') + 1 if query else 0,
        "num_ampersand": url.count('&'),
        "num_hash": url.count('#'),
        "num_numeric_chars": sum(c.isdigit() for c in url),
        "no_https": int(parsed.scheme != 'https'),
        "random_string": int(bool(re.search(r'[a-zA-Z]{10,}', domain))),
        "ip_address": int(bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", domain))),
        "domain_in_subdomains": sum(1 for part in url.split('.')[:-1] if f".{part}" in top_tlds),
        "domain_in_paths": int(any(tld in path for tld in top_tlds)),
        "https_in_hostname": int("https" in domain),
        "hostname_length": len(domain),
        "path_length": len(path),
        "query_length": len(query),
        "double_slash_in_path": int('//' in path),
        "num_sensitive_words": int(any(word in url.lower() for word in ["secure", "account", "webscr", "login", "ebayisapi", "signin", "banking", "confirm"])),
    }

    return features


def features_from_associative_classification_paper(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path

    features = {
        "ip_address_in_url": int(bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", domain))),
        "long_url": int(len(url) > 54),
        "at_symbol_in_url": int('@' in url),
        "prefix_suffix_in_domain": int('-' in domain),
        "subdomain_count": domain.count('.'),
        # "abnormal_url": int(not bool(re.match(r"^(https?|ftp)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", url))), # Query WHOIS database
        # "dns_record": int(bool(domain)),  # Simulated as presence of domain
        # "age_of_domain": -1  # Placeholder for WHOIS lookup
    }

    return features

# Example usage
url = "http://example.com.ca.hello.au.fr.com/path/to/resource/index.php?query=reza@gmail.c&gewfwe"
print(len(extract_url_features(url)))
print(extract_url_features(url)['domain_in_subdomains'])
