"""Tests for the database module."""

import os
import tempfile

import pytest

from db.database import Database


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    _db = Database(db_path)
    yield _db
    _db.close()


class TestWarnings:
    def test_initial_zero(self, db):
        assert db.get_warnings(1, 100) == 0

    def test_add_warning(self, db):
        count = db.add_warning(1, 100)
        assert count == 1
        count = db.add_warning(1, 100)
        assert count == 2

    def test_reset_warnings(self, db):
        db.add_warning(1, 100)
        db.add_warning(1, 100)
        db.reset_warnings(1, 100)
        assert db.get_warnings(1, 100) == 0


class TestGroupSettings:
    def test_default_enabled(self, db):
        assert db.is_enabled(100) is True

    def test_disable_enable(self, db):
        db.set_enabled(100, False)
        assert db.is_enabled(100) is False
        db.set_enabled(100, True)
        assert db.is_enabled(100) is True


class TestWhitelist:
    def test_not_whitelisted_by_default(self, db):
        assert db.is_whitelisted(1, 100) is False

    def test_add_remove(self, db):
        db.add_to_whitelist(1, 100)
        assert db.is_whitelisted(1, 100) is True
        db.remove_from_whitelist(1, 100)
        assert db.is_whitelisted(1, 100) is False


class TestDetectionLog:
    def test_log_and_stats(self, db):
        db.log_detection(100, 1, "scam text", "投资诈骗", 0.95, "删除消息")
        db.log_detection(100, 2, "another scam", "博彩广告", 0.90, "删除消息")
        stats = db.get_stats(100)
        assert stats["total_detections"] == 2
        assert stats["by_type"]["投资诈骗"] == 1
        assert stats["by_type"]["博彩广告"] == 1
