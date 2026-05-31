"""URL-based scam detection: suspicious TLDs, shorteners, known patterns."""

import re
from typing import Optional
from urllib.parse import urlparse

from loguru import logger


# Common URL shorteners that are often abused
_SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "adf.ly", "bl.ink", "lnkd.in",
    "shorte.st", "bc.vc", "v.gd", "cutt.ly", "rb.gy",
}

# Suspicious TLDs frequently used in phishing
_SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".club", ".work", ".click", ".link",
    ".buzz", ".icu", ".win", ".loan", ".gq", ".cf",
    ".tk", ".ml", ".ga",
}

# Regex patterns for phishing-like URLs
_PHISHING_PATTERNS = [
    re.compile(r"(?:login|signin|verify|secure|account|update|confirm)", re.I),
    re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),  # raw IP
    re.compile(r"@"),  # credential-style URLs
]

# URL extraction regex
_URL_RE = re.compile(
    r"https?://[^\s<>\"')\]]+|"           # http(s) URLs
    r"(?<!\w)[a-zA-Z0-9.-]+\.[a-z]{2,}/\S*",  # bare domain with path
    re.I,
)


class URLChecker:
    """Detect suspicious URLs in a message."""

    def __init__(self) -> None:
        logger.debug("URLChecker initialised")

    def check(self, text: str) -> Optional[dict]:
        """Return detection info if suspicious URLs are found."""
        urls = _URL_RE.findall(text)
        if not urls:
            return None

        for raw_url in urls:
            url = raw_url if raw_url.startswith("http") else f"http://{raw_url}"
            parsed = urlparse(url)
            domain = parsed.hostname or ""

            if self._is_shortener(domain):
                return {
                    "type": "可疑短链接",
                    "url": raw_url,
                    "confidence": 0.90,
                }

            if self._has_suspicious_tld(domain):
                return {
                    "type": "钓鱼链接",
                    "url": raw_url,
                    "confidence": 0.85,
                }

            if self._matches_phishing_pattern(url):
                return {
                    "type": "钓鱼链接",
                    "url": raw_url,
                    "confidence": 0.80,
                }

        return None

    @staticmethod
    def _is_shortener(domain: str) -> bool:
        return domain.lower() in _SHORTENER_DOMAINS

    @staticmethod
    def _has_suspicious_tld(domain: str) -> bool:
        for tld in _SUSPICIOUS_TLDS:
            if domain.lower().endswith(tld):
                return True
        return False

    @staticmethod
    def _matches_phishing_pattern(url: str) -> bool:
        for pattern in _PHISHING_PATTERNS:
            if pattern.search(url):
                return True
        return False
