import re
import socket
import requests
import tldextract
import whois
import math
from datetime import datetime
from urllib.parse import urlparse


# -------------------------------------------------------
# SAFE DOMAIN HANDLER
# -------------------------------------------------------
def safe_domain(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        parsed = urlparse(url)
        domain = parsed.hostname
        if domain is None or "." not in domain:
            return None, url
        return domain.lower(), url
    except:
        return None, url



# -------------------------------------------------------
# STRICT PHISHING CHECK (Mode C)
# -------------------------------------------------------
SUSPICIOUS_KEYWORDS = [
    "secure", "account", "update", "verify", "login", "signin",
    "bank", "payment", "invoice", "paypal", "amazon", "gift",
    "free", "claim", "urgent", "alert", "verification"
]

SUSPICIOUS_TLDS = [
    "xyz", "top", "online", "shop", "buzz", "cyou", "click",
    "zip", "cam", "gq", "ml", "ga", "tk", "cf", "work", "rest"
]

SHORTENER_PATTERN = r"(bit\.ly|goo\.gl|tinyurl|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly|cutt\.ly)"

BRAND_DOMAINS = {
    "paypal": ["paypal.com"],
    "google": ["google.com"],
    "amazon": ["amazon.com"],
    "microsoft": ["microsoft.com", "live.com", "outlook.com"],
    "facebook": ["facebook.com", "fb.com"],
    "sbi": ["sbi.co.in", "onlinesbi.com"],
    "hdfc": ["hdfcbank.com"],
    "axis": ["axisbank.com"]
}


def entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum([p * math.log(p, 2) for p in prob])


def is_strict_phishing(url):
    domain, fixed_url = safe_domain(url)
    if domain is None:
        return True

    host = domain
    lower = fixed_url.lower()
    score = 0

    # 1. URL shortener
    if re.search(SHORTENER_PATTERN, lower):
        score += 2

    # 2. IP address
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        score += 3

    # 3. brand impersonation
    for brand, legit_list in BRAND_DOMAINS.items():
        if brand in lower:
            if not any(host.endswith(ld) for ld in legit_list):
                score += 3

    # 4. suspicious TLD
    if any(host.endswith("." + tld) for tld in SUSPICIOUS_TLDS):
        score += 2

    # 5. high entropy hostname
    if entropy(host) > 3.6:
        score += 2

    # 6. too many digits
    digits = sum(c.isdigit() for c in host)
    if digits > 5:
        score += 1

    # 7. keyword based
    if any(k in lower for k in SUSPICIOUS_KEYWORDS):
        score += 2

    # Strict threshold
    return score >= 4



# ---------------------------------------------------------------
# --- ORIGINAL 30 FEATURES (your same names, SAFE FOR MODEL) ---
# ---------------------------------------------------------------
# (No changes here except using strict rule above)
# ---------------------------------------------------------------

def having_IP_Address(url):
    try:
        host = urlparse(url).hostname
        socket.inet_aton(host)
        return -1
    except:
        return 1

def URL_Length(url):
    L = len(url)
    if L < 54: return -1
    if L <= 75: return 0
    return 1

def Shortining_Service(url):
    return -1 if re.search(SHORTENER_PATTERN, url.lower()) else 1

def having_At_Symbol(url): return -1 if "@" in url else 1

def double_slash_redirecting(url):
    try:
        after = url[url.find("//") + 2:]
        return -1 if "//" in after else 1
    except:
        return 1

def Prefix_Suffix(domain): return -1 if "-" in domain else 1

def having_Sub_Domain(url):
    ext = tldextract.extract(url)
    parts = ext.subdomain.split(".") if ext.subdomain else []
    if len(parts) == 0: return 1
    if len(parts) == 1: return 0
    return -1

def SSLfinal_State(url): return 1 if url.startswith("https") else -1

def Domain_registeration_length(domain):
    try:
        w = whois.whois(domain)
        exp = w.expiration_date
        cre = w.creation_date
        if isinstance(exp, list): exp = exp[0]
        if isinstance(cre, list): cre = cre[0]
        if exp and cre and (exp - cre).days >= 365:
            return 1
        return -1
    except:
        return -1

def Favicon(url):
    try:
        r = requests.get(url, timeout=3)
        return 1 if "favicon" in r.text.lower() else -1
    except:
        return -1

def port(url):
    parsed = urlparse(url)
    return 1 if parsed.port in (80, 443, None) else -1

def HTTPS_token(domain): return -1 if "https" in domain else 1

def Request_URL(url):
    L = url.lower()
    return -1 if any(k in L for k in SUSPICIOUS_KEYWORDS) else 1

def URL_of_Anchor(url): return 1
def Links_in_tags(url): return 1
def SFH(url): return 1
def Submitting_to_email(url): return -1 if "mailto:" in url.lower() else 1

def Abnormal_URL(url):
    return -1 if entropy(url) > 4.0 else 1

def Redirect(url):
    try:
        r = requests.get(url, timeout=4)
        return -1 if len(r.history) > 1 else 1
    except:
        return -1

def on_mouseover(url): return 1
def RightClick(url): return 1
def popUpWidnow(url): return 1
def Iframe(url): return 1

def age_of_domain(domain):
    try:
        w = whois.whois(domain)
        cre = w.creation_date
        if isinstance(cre, list): cre = cre[0]
        if cre and (datetime.now() - cre).days >= 365:
            return 1
        return -1
    except:
        return -1

def DNSRecord(domain):
    try:
        socket.gethostbyname(domain)
        return 1
    except:
        return -1

def web_traffic(url):
    host = urlparse(url).hostname or ""
    if any(host.endswith("." + tld) for tld in SUSPICIOUS_TLDS):
        return -1
    return 1

def Page_Rank(url): return -1
def Google_Index(url): return 1
def Links_pointing_to_page(url): return 0
def Statistical_report(url): return 1



# -------------------------------------------------------
# STRICT FEATURE GENERATION INSIDE EXTRACTOR
# -------------------------------------------------------
def extract_features(url):
    domain, fixed_url = safe_domain(url)
    if domain is None:
        return "INVALID"

    # ---------------------------------------------------
    # STRICT MODE APPLIED HERE
    # ---------------------------------------------------
    if is_strict_phishing(fixed_url):
        return {
            "having_IP_Address": -1,
            "URL_Length": 1,
            "Shortining_Service": -1,
            "having_At_Symbol": -1,
            "double_slash_redirecting": -1,
            "Prefix_Suffix": -1,
            "having_Sub_Domain": -1,
            "SSLfinal_State": -1,
            "Domain_registeration_length": -1,
            "Favicon": -1,
            "port": -1,
            "HTTPS_token": -1,
            "Request_URL": -1,
            "URL_of_Anchor": -1,
            "Links_in_tags": -1,
            "SFH": -1,
            "Submitting_to_email": -1,
            "Abnormal_URL": -1,
            "Redirect": -1,
            "on_mouseover": -1,
            "RightClick": -1,
            "popUpWidnow": -1,
            "Iframe": -1,
            "age_of_domain": -1,
            "DNSRecord": -1,
            "web_traffic": -1,
            "Page_Rank": -1,
            "Google_Index": -1,
            "Links_pointing_to_page": -1,
            "Statistical_report": -1
        }

    # ---------------------------------------------------
    # NORMAL FEATURE EXTRACTION (if NOT strict phishing)
    # ---------------------------------------------------
    return {
        "having_IP_Address": having_IP_Address(fixed_url),
        "URL_Length": URL_Length(fixed_url),
        "Shortining_Service": Shortining_Service(fixed_url),
        "having_At_Symbol": having_At_Symbol(fixed_url),
        "double_slash_redirecting": double_slash_redirecting(fixed_url),
        "Prefix_Suffix": Prefix_Suffix(domain),
        "having_Sub_Domain": having_Sub_Domain(fixed_url),
        "SSLfinal_State": SSLfinal_State(fixed_url),
        "Domain_registeration_length": Domain_registeration_length(domain),
        "Favicon": Favicon(fixed_url),
        "port": port(fixed_url),
        "HTTPS_token": HTTPS_token(domain),
        "Request_URL": Request_URL(fixed_url),
        "URL_of_Anchor": URL_of_Anchor(fixed_url),
        "Links_in_tags": Links_in_tags(fixed_url),
        "SFH": SFH(fixed_url),
        "Submitting_to_email": Submitting_to_email(fixed_url),
        "Abnormal_URL": Abnormal_URL(fixed_url),
        "Redirect": Redirect(fixed_url),
        "on_mouseover": on_mouseover(fixed_url),
        "RightClick": RightClick(fixed_url),
        "popUpWidnow": popUpWidnow(fixed_url),
        "Iframe": Iframe(fixed_url),
        "age_of_domain": age_of_domain(domain),
        "DNSRecord": DNSRecord(domain),
        "web_traffic": web_traffic(fixed_url),
        "Page_Rank": Page_Rank(fixed_url),
        "Google_Index": Google_Index(fixed_url),
        "Links_pointing_to_page": Links_pointing_to_page(fixed_url),
        "Statistical_report": Statistical_report(fixed_url)
    }

