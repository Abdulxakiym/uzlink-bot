import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.i18n import MESSAGES


def test_all_languages_have_same_keys():
    langs = list(MESSAGES.keys())
    base_keys = set(MESSAGES[langs[0]].keys())
    for lang in langs[1:]:
        assert set(MESSAGES[lang].keys()) == base_keys
