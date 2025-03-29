from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from autotable.settings import (
    AutoTableSettings,
    RepoSettings,
    load_settings_file,
    search_for_settings_file,
    select_setting,
)


class TestSelectSetting(unittest.TestCase):
    def setUp(self) -> None:
        self.setting_key = "gouzil/autoTable/123"
        self.toml_file = """
token = "123"
[common]
token = "1213"
log_level = "INFO"

[repo_settings.paddlepaddle.paddle.123]
token = "123"
log_level = "INFO"

[repo_settings.gouzil.autoTable.123]
token = "456"
log_level = "DEBUG"
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as self.temp_file:
            self.temp_file.write(self.toml_file.encode("utf-8"))

    def tearDown(self):
        # 删除临时文件
        if (file := Path(self.temp_file.name)).exists():
            file.unlink()

    def test_select_setting(self):
        self.assertEqual(select_setting(None, self.setting_key, "token", "test"), "test")
        self.assertEqual(
            select_setting(
                AutoTableSettings(
                    token="test",
                    log_level="INFO",
                    repo_settings={self.setting_key: RepoSettings(token="test", log_level="INFO", issue_id=None)},
                ),
                self.setting_key,
                "token",
                None,
            ),
            "test",
        )
        self.assertEqual(
            select_setting(
                AutoTableSettings(
                    token="test",
                    log_level="INFO",
                    repo_settings={self.setting_key: RepoSettings(token="test", log_level="INFO", issue_id=None)},
                ),
                self.setting_key,
                "token",
                "test1",
            ),
            "test1",
        )

    def test_load_appoint_settings_file(self):
        settings_file = Path(self.temp_file.name)
        settings = load_settings_file(settings_file)
        self.assertEqual(settings.token, "1213")
        self.assertEqual(settings.log_level, "INFO")
        self.assertEqual(
            settings.repo_settings[self.setting_key].token,
            "456",
        )
        self.assertEqual(
            settings.repo_settings[self.setting_key].log_level,
            "DEBUG",
        )

    def test_search_for_settings_file(self):
        assert search_for_settings_file() is None
        test_file = Path("autotable.toml")
        assert not test_file.exists()
        with test_file.open("w", encoding="utf-8") as f:
            f.write(self.toml_file)
        assert search_for_settings_file() is not None
        settings = load_settings_file(test_file)
        self.assertEqual(settings.token, "1213")
        test_file.unlink()
        assert search_for_settings_file() is None
