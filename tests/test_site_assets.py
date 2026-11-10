from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs" / "index.html"
SITE_DIR = SITE.parent

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.missing_alt = [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag == "img":
            if not a.get("alt"): self.missing_alt.append(a.get("src"))
            if a.get("src"): self.refs.append(a["src"])
        if tag == "a" and a.get("href"): self.refs.append(a["href"])

def test_site_sections_are_unique():
    p=Parser(); p.feed(SITE.read_text(encoding="utf-8"))
    assert len(p.ids) == len(set(p.ids))
    assert {"top","model","tile","results","entangler","roadmap","evidence"} <= set(p.ids)

def test_local_assets_exist_and_images_have_alt():
    p=Parser(); p.feed(SITE.read_text(encoding="utf-8"))
    assert not p.missing_alt
    for ref in p.refs:
        u=urlparse(ref)
        if u.scheme or u.netloc or ref.startswith("#"): continue
        if not u.path: continue
        target=(SITE_DIR / unquote(u.path)).resolve()
        assert target.is_relative_to(SITE_DIR.resolve())
        assert target.is_file(), f"broken local reference: {ref}"

def test_site_contains_current_model_and_open_blocker():
    s=SITE.read_text(encoding="utf-8")
    for token in ("1.3937127 J","0.1770433","6.38074 μs","complex Z link","not a measured gate"):
        assert token.lower() in s.lower()
    assert "protected doublet" not in s.lower()
    assert "gauge protection" not in s.lower()
