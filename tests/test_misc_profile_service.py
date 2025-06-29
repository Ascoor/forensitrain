import io
from unittest import mock

import os
import sys
import pytest
import types

sys.modules.setdefault('httpx', types.SimpleNamespace())
sys.modules.setdefault('bs4', types.SimpleNamespace(BeautifulSoup=lambda *a, **k: None))
email_mod = types.SimpleNamespace(
    validate_email=lambda e, check_deliverability=True: types.SimpleNamespace(email=e),
    EmailNotValidError=Exception,
)
sys.modules.setdefault('email_validator', email_mod)
sys.modules.setdefault('requests', types.SimpleNamespace(get=lambda *a, **k: None, post=lambda *a, **k: None))
sys.modules.setdefault('PIL', types.SimpleNamespace(Image=types.SimpleNamespace(open=lambda *a, **k: None)))
sys.modules.setdefault('pytesseract', types.SimpleNamespace(image_to_string=lambda *a, **k: ""))

services_path = os.path.join(os.path.dirname(__file__), "..", "backend", "app", "services")
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
import importlib.util, types as _types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
import importlib, types as _types
app_pkg = _types.ModuleType("app")
services_pkg = _types.ModuleType("app.services")
services_pkg.__path__ = [services_path]
sys.modules['app'] = app_pkg
sys.modules['app.services'] = services_pkg
sys.modules.setdefault('app.services.advanced_osint_service', _types.SimpleNamespace(
    apify_social_media_finder=lambda *a, **k: [],
    social_searcher_mentions=lambda *a, **k: [],
))
sys.modules.setdefault('app.services.phone_service', _types.ModuleType('phone_service'))
sys.modules.setdefault('app.services.osint_service', _types.ModuleType('osint_service'))
sys.modules.setdefault('app.services.recursive_osint_engine', _types.ModuleType('recursive_osint_engine'))
sys.modules.setdefault('app.services.identity_enrichment_service', _types.ModuleType('identity_enrichment_service'))
mps = importlib.import_module('app.services.misc_profile_service')


@pytest.fixture
def dummy_image_bytes():
    return b"fake"


def test_extract_text_ocrspace(dummy_image_bytes):
    with mock.patch("requests.post") as mpost, mock.patch.dict(os.environ, {"OCR_SPACE_KEY": "KEY"}):
        mpost.return_value.status_code = 200
        mpost.return_value.json.return_value = {"ParsedResults": [{"ParsedText": "text"}]}
        text = mps.extract_text_from_image(dummy_image_bytes)
        assert text == "text"


def test_validate_and_normalize_email_api():
    with mock.patch("requests.get") as mget, mock.patch.dict(os.environ, {"ANYMAILFINDER_KEY": "K"}):
        mget.return_value.status_code = 200
        mget.return_value.json.return_value = {"status": "deliverable", "email": "a@b.c"}
        res = mps.validate_and_normalize_email("A@B.c")
        assert res["valid"] is True
        assert res["email"] == "a@b.c"


def test_find_profiles_by_email():
    with mock.patch("requests.get") as mget, mock.patch.dict(os.environ, {"PROXYCURL_KEY": "K"}):
        mget.return_value.status_code = 200
        mget.return_value.json.return_value = {"linkedin_profile_url": "https://linkedin.com/in/test"}
        res = mps.find_profiles_by_email("a@b.c")
        assert res["linkedin"]


def test_find_profiles_by_name_apify():
    with mock.patch.object(mps, "apify_social_media_finder") as finder, mock.patch.dict(os.environ, {"APIFY_TOKEN": "T"}):
        finder.return_value = [{"facebook": "http://fb.com/x"}]
        urls = mps.find_profiles_by_name("john")
        assert "http://fb.com/x" in urls
