"""Tests for the URL checker module."""

from detection.url_checker import URLChecker


def test_shortener_detected():
    checker = URLChecker()
    result = checker.check("快来看 https://bit.ly/abc123 好东西")
    assert result is not None
    assert result["type"] == "可疑短链接"


def test_suspicious_tld():
    checker = URLChecker()
    result = checker.check("Visit https://example.xyz/login now!")
    assert result is not None
    assert result["type"] == "钓鱼链接"


def test_phishing_pattern_ip():
    checker = URLChecker()
    result = checker.check("http://192.168.1.1/login")
    assert result is not None


def test_clean_url():
    checker = URLChecker()
    result = checker.check("Check https://www.google.com for info")
    assert result is None


def test_no_url():
    checker = URLChecker()
    result = checker.check("这是一条普通消息，没有链接")
    assert result is None
