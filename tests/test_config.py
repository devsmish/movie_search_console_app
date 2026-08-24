import pytest

from config import REQUIRED_VARS, Config, ConfigError


class TestMissingVars:
    def test_returns_empty_list_when_all_required_vars_are_set(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, "some-value")
        assert Config.missing_vars() == []

    def test_reports_a_single_missing_var(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, "some-value")
        monkeypatch.setattr(Config, "MYSQL_HOST", None)
        assert Config.missing_vars() == ["MYSQL_HOST"]

    def test_reports_all_missing_vars_in_declared_order(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, None)
        assert Config.missing_vars() == list(REQUIRED_VARS)

    def test_empty_string_counts_as_missing(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, "some-value")
        monkeypatch.setattr(Config, "MONGO_URI", "")
        assert Config.missing_vars() == ["MONGO_URI"]

    def test_mysql_password_is_not_required(self, monkeypatch):
        # An empty MySQL password is valid for some local dev setups
        # (e.g. root with no password), so it must never be flagged.
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, "some-value")
        monkeypatch.setattr(Config, "MYSQL_PASSWORD", "")
        assert Config.missing_vars() == []


class TestValidate:
    def test_does_not_raise_when_config_is_complete(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, "some-value")
        Config.validate()  # must not raise

    def test_raises_config_error_when_vars_are_missing(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, None)
        with pytest.raises(ConfigError):
            Config.validate()

    def test_config_error_carries_the_missing_var_names(self, monkeypatch):
        for name in REQUIRED_VARS:
            monkeypatch.setattr(Config, name, "some-value")
        monkeypatch.setattr(Config, "MONGO_COLLECTION", None)
        with pytest.raises(ConfigError) as exc_info:
            Config.validate()
        assert exc_info.value.missing == ["MONGO_COLLECTION"]
