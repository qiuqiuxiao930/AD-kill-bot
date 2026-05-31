"""Tests for the keyword filter module."""

from detection.keyword_filter import KeywordFilter


def test_loads_keywords(tmp_path):
    kw_file = tmp_path / "kw.txt"
    kw_file.write_text("稳赚不赔\n博彩\n# comment\n\nclick here now\n", encoding="utf-8")
    kf = KeywordFilter(str(kw_file))
    assert len(kf.keywords) == 3


def test_match_chinese():
    kf = KeywordFilter.__new__(KeywordFilter)
    kf.keywords = ["稳赚不赔", "博彩"]
    result = kf.check("加我微信，稳赚不赔，日收益300%")
    assert result is not None
    assert result["confidence"] == 1.0
    assert "投资诈骗" in result["type"]


def test_match_english():
    kf = KeywordFilter.__new__(KeywordFilter)
    kf.keywords = ["guaranteed profit"]
    result = kf.check("This is a Guaranteed Profit scheme!")
    assert result is not None


def test_no_match():
    kf = KeywordFilter.__new__(KeywordFilter)
    kf.keywords = ["稳赚不赔", "博彩"]
    result = kf.check("今天天气真好")
    assert result is None


def test_classify_keyword():
    assert KeywordFilter._classify_keyword("博彩平台") == "博彩广告"
    assert KeywordFilter._classify_keyword("稳赚不赔") == "投资诈骗"
    assert KeywordFilter._classify_keyword("刷单赚钱") == "刷单兼职"
    assert KeywordFilter._classify_keyword("unknown_keyword") == "其他违规"
