# --- trigger_analyzer.py ---
import re

# Regex patterns for common triggers
URL_REGEX = r"https?://[^\s/$.?#].[^\s]*"
CRYPTO_REGEX = {
    "BTC": r"\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b",
    "ETH": r"\b0x[a-fA-F0-9]{40}\b",
}
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
FILE_EXTENSION_REGEX = r"\b\w+\.(exe|zip|scr|msi|dmg|apk)\b"

def analyze_for_triggers(text: str) -> dict | None:
    """
    Scans a single message for high-confidence conclusion triggers.
    Returns a dictionary with trigger info if found, otherwise None.
    """
    # Check for Crypto Wallets
    for coin, pattern in CRYPTO_REGEX.items():
        match = re.search(pattern, text)
        if match:
            return {"type": "Crypto Wallet", "value": match.group(0), "coin": coin}

    # Check for Malicious File Extensions
    match = re.search(FILE_EXTENSION_REGEX, text, re.IGNORECASE)
    if match:
        return {"type": "Malicious File Lure", "value": match.group(0)}

    # Check for URLs
    match = re.search(URL_REGEX, text)
    if match:
        return {"type": "URL / Phishing Link", "value": match.group(0)}

    # Check for Email Address (less critical, but still useful intelligence)
    match = re.search(EMAIL_REGEX, text)
    if match:
        return {"type": "Contact Info (Email)", "value": match.group(0)}
    
    return None