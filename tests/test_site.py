from html.parser import HTMLParser
import os
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.join(ROOT, "_site")
SITE_URL = "https://dinghaoxi.github.io"
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


FORBIDDEN_IDENTIFIERS = (
    "caihanlin.com",
    "Cai Hanlin",
    "Hanlin CAI",
    "蔡汉霖",
    "GuangLun2000",
    "lancecai",
    "G-T5N5JY1E21",
    "4c8f7caa",
)


PAGE_CONTRACTS = {
    "index.md": {"lang": "en", "alternate_url": "/zh/", "permalink": "/index.html"},
    "publications.md": {
        "lang": "en",
        "alternate_url": "/zh/publications/",
        "permalink": "/publications/index.html",
    },
    "projects.md": {
        "lang": "en",
        "alternate_url": "/zh/projects/",
        "permalink": "/projects/index.html",
    },
    "zh/index.md": {
        "lang": "zh-CN",
        "alternate_url": "/",
        "permalink": "/zh/index.html",
    },
    "zh/publications.md": {
        "lang": "zh-CN",
        "alternate_url": "/publications/",
        "permalink": "/zh/publications/index.html",
    },
    "zh/projects.md": {
        "lang": "zh-CN",
        "alternate_url": "/projects/",
        "permalink": "/zh/projects/index.html",
    },
}


RENDERED_PAGE_CONTRACTS = {
    "index.html": {
        "lang": "en",
        "canonical": SITE_URL + "/",
        "alternates": {
            "en": SITE_URL + "/",
            "zh-CN": SITE_URL + "/zh/",
            "x-default": SITE_URL + "/",
        },
        "navigation": ("About Me", "Publications", "Projects"),
        "switch": {"text": "中文", "href": "/zh/", "lang": "zh-CN", "hreflang": "zh-CN", "aria-label": "切换至中文"},
    },
    "publications/index.html": {
        "lang": "en",
        "canonical": SITE_URL + "/publications/",
        "alternates": {
            "en": SITE_URL + "/publications/",
            "zh-CN": SITE_URL + "/zh/publications/",
            "x-default": SITE_URL + "/publications/",
        },
        "navigation": ("About Me", "Publications", "Projects"),
        "switch": {
            "text": "中文",
            "href": "/zh/publications/",
            "lang": "zh-CN",
            "hreflang": "zh-CN",
            "aria-label": "切换至中文",
        },
    },
    "projects/index.html": {
        "lang": "en",
        "canonical": SITE_URL + "/projects/",
        "alternates": {
            "en": SITE_URL + "/projects/",
            "zh-CN": SITE_URL + "/zh/projects/",
            "x-default": SITE_URL + "/projects/",
        },
        "navigation": ("About Me", "Publications", "Projects"),
        "switch": {
            "text": "中文",
            "href": "/zh/projects/",
            "lang": "zh-CN",
            "hreflang": "zh-CN",
            "aria-label": "切换至中文",
        },
    },
    "zh/index.html": {
        "lang": "zh-CN",
        "canonical": SITE_URL + "/zh/",
        "alternates": {
            "en": SITE_URL + "/",
            "zh-CN": SITE_URL + "/zh/",
            "x-default": SITE_URL + "/",
        },
        "navigation": ("关于我", "发表成果", "项目"),
        "switch": {"text": "EN", "href": "/", "lang": "en", "hreflang": "en", "aria-label": "Switch to English"},
    },
    "zh/publications/index.html": {
        "lang": "zh-CN",
        "canonical": SITE_URL + "/zh/publications/",
        "alternates": {
            "en": SITE_URL + "/publications/",
            "zh-CN": SITE_URL + "/zh/publications/",
            "x-default": SITE_URL + "/publications/",
        },
        "navigation": ("关于我", "发表成果", "项目"),
        "switch": {
            "text": "EN",
            "href": "/publications/",
            "lang": "en",
            "hreflang": "en",
            "aria-label": "Switch to English",
        },
    },
    "zh/projects/index.html": {
        "lang": "zh-CN",
        "canonical": SITE_URL + "/zh/projects/",
        "alternates": {
            "en": SITE_URL + "/projects/",
            "zh-CN": SITE_URL + "/zh/projects/",
            "x-default": SITE_URL + "/projects/",
        },
        "navigation": ("关于我", "发表成果", "项目"),
        "switch": {
            "text": "EN",
            "href": "/projects/",
            "lang": "en",
            "hreflang": "en",
            "aria-label": "Switch to English",
        },
    },
}


class RenderedPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.html_langs = []
        self.canonical_urls = []
        self.alternate_urls = []
        self.navigation_links = []
        self.language_switch_links = []
        self.site_name_links = []
        self.strong_texts = []
        self.bio_photo_alts = []
        self.root_relative_targets = []
        self._navigation_depth = 0
        self._navigation_anchor = None
        self._language_switch_anchor = None
        self._site_name_depth = 0
        self._site_name_anchor = None
        self._strong_depth = 0
        self._strong_text = []
        self.footer_texts = []
        self.footer_container_texts = []
        self._footer_depth = 0
        self._footer_container_text = []
        self._footer_heading_depth = 0
        self._footer_heading_text = []
        self.visible_text_parts = []
        self.article_blocks = []
        self._article_depth = 0
        self._hidden_depth = 0
        self._element_stack = []
        self._article_block = None
        self._article_block_tag = None
        self._article_block_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "article":
            self._article_depth += 1
        hidden = (
            self._hidden_depth > 0
            or tag in {"head", "script", "style", "template", "noscript"}
            or "hidden" in attributes
            or attributes.get("aria-hidden") == "true"
            or "display:none" in (attributes.get("style") or "").replace(" ", "").lower()
        )
        if tag not in VOID_TAGS:
            self._element_stack.append((tag, hidden))
        if hidden and tag not in VOID_TAGS:
            self._hidden_depth += 1
        if self._article_depth and not self._hidden_depth and tag in {"h2", "li", "p"} and self._article_block is None:
            self._article_block = []
            self._article_block_tag = tag
            self._article_block_depth = 1
        elif self._article_block is not None and tag not in VOID_TAGS:
            self._article_block_depth += 1

        if tag == "html":
            self.html_langs.append(attributes.get("lang"))

        if tag == "link":
            relationships = (attributes.get("rel") or "").split()
            if "canonical" in relationships:
                self.canonical_urls.append(attributes.get("href"))
            if "alternate" in relationships and attributes.get("hreflang"):
                self.alternate_urls.append(
                    (attributes.get("hreflang"), attributes.get("href"))
                )

        if tag == "img" and "bio-photo" in (attributes.get("class") or "").split():
            self.bio_photo_alts.append(attributes.get("alt"))

        for attribute_name in ("href", "src"):
            value = attributes.get(attribute_name)
            if value and value.startswith("/") and not value.startswith("//"):
                self.root_relative_targets.append((tag, attribute_name, value))

        if tag == "div":
            if self._site_name_depth:
                self._site_name_depth += 1
            elif "site-name" in (attributes.get("class") or "").split():
                self._site_name_depth = 1

        if tag == "nav":
            self._navigation_depth += 1
        if tag == "a" and self._navigation_depth:
            self._navigation_anchor = {"attributes": attributes, "text": []}
        if tag == "a" and "language-switch" in (attributes.get("class") or "").split():
            self._language_switch_anchor = {"attributes": attributes, "text": []}
        if tag == "a" and self._site_name_depth:
            self._site_name_anchor = {"attributes": attributes, "text": []}

        if tag == "strong":
            if not self._strong_depth:
                self._strong_text = []
            self._strong_depth += 1

        if tag == "footer":
            if not self._footer_depth:
                self._footer_container_text = []
            self._footer_depth += 1

        if tag == "h6" and self._footer_depth:
            if not self._footer_heading_depth:
                self._footer_heading_text = []
            self._footer_heading_depth += 1

    def handle_data(self, data):
        if self._article_depth and not self._hidden_depth:
            self.visible_text_parts.append(data)
        if self._article_block is not None and self._article_depth and not self._hidden_depth:
            self._article_block.append(data)
        if self._navigation_anchor is not None:
            self._navigation_anchor["text"].append(data)
        if self._language_switch_anchor is not None:
            self._language_switch_anchor["text"].append(data)
        if self._site_name_anchor is not None:
            self._site_name_anchor["text"].append(data)
        if self._strong_depth:
            self._strong_text.append(data)
        if self._footer_depth:
            self._footer_container_text.append(data)
        if self._footer_heading_depth and self._footer_depth:
            self._footer_heading_text.append(data)

    def handle_endtag(self, tag):
        if self._article_block is not None and tag not in VOID_TAGS:
            self._article_block_depth -= 1
            if self._article_block_depth == 0:
                self.article_blocks.append(
                    (self._article_block_tag, " ".join("".join(self._article_block).split()))
                )
                self._article_block = None
                self._article_block_tag = None
        if tag not in VOID_TAGS:
            for index in range(len(self._element_stack) - 1, -1, -1):
                element_tag, hidden = self._element_stack[index]
                if element_tag == tag:
                    del self._element_stack[index:]
                    if hidden:
                        self._hidden_depth -= 1
                    break
        if tag == "article" and self._article_depth:
            self._article_depth -= 1

        if tag == "a" and self._navigation_anchor is not None:
            self.navigation_links.append(
                {
                    "attributes": self._navigation_anchor["attributes"],
                    "text": " ".join("".join(self._navigation_anchor["text"]).split()),
                }
            )
            self._navigation_anchor = None
        elif tag == "nav" and self._navigation_depth:
            self._navigation_depth -= 1

        if tag == "a" and self._language_switch_anchor is not None:
            self.language_switch_links.append(
                {
                    "attributes": self._language_switch_anchor["attributes"],
                    "text": " ".join("".join(self._language_switch_anchor["text"]).split()),
                }
            )
            self._language_switch_anchor = None

        if tag == "a" and self._site_name_anchor is not None:
            self.site_name_links.append(
                {
                    "attributes": self._site_name_anchor["attributes"],
                    "text": " ".join("".join(self._site_name_anchor["text"]).split()),
                }
            )
            self._site_name_anchor = None
        elif tag == "div" and self._site_name_depth:
            self._site_name_depth -= 1

        if tag == "strong" and self._strong_depth:
            self._strong_depth -= 1
            if not self._strong_depth:
                self.strong_texts.append(" ".join("".join(self._strong_text).split()))

        if tag == "h6" and self._footer_heading_depth:
            self._footer_heading_depth -= 1
            if not self._footer_heading_depth:
                self.footer_texts.append(
                    " ".join("".join(self._footer_heading_text).split())
                )

        if tag == "footer" and self._footer_depth:
            self._footer_depth -= 1
            if not self._footer_depth:
                self.footer_container_texts.append(
                    " ".join("".join(self._footer_container_text).split())
                )


def read_file(relative_path):
    path = os.path.join(ROOT, relative_path)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def front_matter(text):
    if text is None or not text.startswith("---"):
        return {}
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
    if not match:
        return {}
    values = {}
    for item in re.finditer(r"(?m)^([A-Za-z_][\w-]*):[ \t]*(.*?)[ \t]*(?:[ \t]+#.*)?$", match.group(1)):
        values[item.group(1)] = item.group(2).strip().strip("'\"")
    return values


class SiteContractTest(unittest.TestCase):
    def assert_contains(self, text, marker, relative_path):
        if marker not in (text or ""):
            self.fail("missing marker %r in %s" % (marker, relative_path))

    def rendered_page(self, relative_path):
        path = os.path.join(SITE_ROOT, relative_path)
        self.assertTrue(
            os.path.isfile(path),
            "rendered page is missing: _site/%s; run the site build first"
            % relative_path,
        )
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read()
        parser = RenderedPageParser()
        parser.feed(text)
        parser.close()
        return text, parser

    def test_bilingual_pages_have_front_matter_contract(self):
        for relative_path, expected in PAGE_CONTRACTS.items():
            with self.subTest(page=relative_path):
                text = read_file(relative_path)
                self.assertIsNotNone(
                    text, "required page file is missing: %s" % relative_path
                )
                metadata = front_matter(text)
                self.assertEqual(metadata.get("lang"), expected["lang"])
                self.assertEqual(metadata.get("alternate_url"), expected["alternate_url"])
                self.assertEqual(metadata.get("permalink"), expected["permalink"])

    def test_navigation_contains_bilingual_labels(self):
        navigation = read_file("_data/navigation.yml")
        self.assertIsNotNone(navigation, "required navigation file is missing: _data/navigation.yml")
        for label in ("About Me", "Publications", "Projects", "关于我", "发表成果", "项目"):
            with self.subTest(label=label):
                self.assert_contains(navigation, label, "_data/navigation.yml")

    def test_projects_use_compact_unnumbered_entries(self):
        page_contracts = {
            "en": {
                "source": "projects.md",
                "rendered": "projects/index.html",
                "intro": "All projects below are led by Dinghao Xi.",
                "forbidden_role": "Principal Investigator",
                "forbidden_amount": r"RMB\s*[\d,]+",
                "periods": {
                    "2027–2029": 1,
                    "2026–2027": 2,
                    "2024–2026": 1,
                    "2025–2026": 1,
                    "2026–2028": 1,
                },
            },
            "zh": {
                "source": "zh/projects.md",
                "rendered": "zh/projects/index.html",
                "intro": "本人主持的项目如下。",
                "forbidden_role": "负责人：奚鼎昊",
                "forbidden_amount": r"\d+\s*万元",
                "periods": {
                    "2027—2029年": 1,
                    "2026—2027年": 2,
                    "2024—2026年": 1,
                    "2025—2026年": 1,
                    "2026—2028年": 1,
                },
            },
        }

        for language, contract in page_contracts.items():
            source = read_file(contract["source"])
            self.assertIsNotNone(
                source, "required page file is missing: %s" % contract["source"]
            )
            rendered, _ = self.rendered_page(contract["rendered"])

            for artifact, text in (("source", source), ("rendered", rendered)):
                with self.subTest(language=language, artifact=artifact):
                    self.assertEqual(text.count(contract["intro"]), 1)
                    self.assertEqual(text.count('class="project-entry"'), 6)
                    self.assertNotRegex(text, r"(?m)^\d+\.\s")
                    self.assertNotIn(contract["forbidden_role"], text)
                    self.assertNotRegex(text, contract["forbidden_amount"])
                    self.assertNotIn("project-meta__separator", text)
                    for period, count in contract["periods"].items():
                        with self.subTest(
                            language=language, artifact=artifact, period=period
                        ):
                            self.assertEqual(text.count(period), count)

    def test_sitemap_contains_all_bilingual_site_url_routes(self):
        sitemap = read_file("sitemap.xml")
        self.assertIsNotNone(sitemap, "required sitemap file is missing: sitemap.xml")
        loc_values = set(re.findall(r"<loc>\s*(.*?)\s*</loc>", sitemap or "", re.DOTALL))
        for route in ("/", "/zh/", "/publications/", "/zh/publications/", "/projects/", "/zh/projects/"):
            with self.subTest(route=route):
                expected = "{{ site.url }}" + route
                if expected not in loc_values:
                    self.fail("missing sitemap route: %s" % route)

    def test_tracked_text_sources_contain_no_legacy_site_identifiers(self):
        excluded_dirs = {".git", "docs", "tests", "node_modules", "vendor", ".bundle", "_site", ".jekyll-cache", "build", "dist"}
        excluded_files = {"LICENSE", os.path.relpath(__file__, ROOT)}
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
        )
        tracked_paths = result.stdout.decode("utf-8", errors="ignore").split("\0")
        binary_suffixes = {
            ".eot", ".gif", ".gz", ".ico", ".jpeg", ".jpg", ".mov", ".mp4",
            ".docx", ".gz", ".mp3", ".mp4", ".mov", ".pdf", ".png", ".pptx", ".tar",
            ".ttf", ".wasm", ".webp", ".woff", ".woff2", ".xlsx", ".zip",
        }
        violations = []
        for relative_path in tracked_paths:
            if not relative_path or relative_path in excluded_files:
                continue
            parts = relative_path.split("/")
            if excluded_dirs.intersection(parts):
                continue
            if os.path.splitext(relative_path)[1].lower() in binary_suffixes:
                continue
            path = os.path.join(ROOT, relative_path)
            if not os.path.isfile(path):
                self.fail("tracked text source is missing: %s" % relative_path)
            try:
                with open(path, "rb") as handle:
                    raw = handle.read()
            except OSError as error:
                self.fail("unable to read tracked text source %s: %s" % (relative_path, error))
            text = raw.decode("utf-8", errors="ignore")
            for marker in FORBIDDEN_IDENTIFIERS:
                if marker in text:
                    violations.append((relative_path, marker))
        if violations:
            self.fail("legacy markers found: %s" % ", ".join("%s:%r" % item for item in violations))

    def test_rendered_pages_have_exact_language_and_discovery_metadata(self):
        for relative_path, expected in RENDERED_PAGE_CONTRACTS.items():
            with self.subTest(page=relative_path):
                _, parsed = self.rendered_page(relative_path)
                self.assertEqual(parsed.html_langs, [expected["lang"]])
                self.assertEqual(parsed.canonical_urls, [expected["canonical"]])
                self.assertEqual(len(parsed.alternate_urls), 3)
                self.assertEqual(
                    len({language for language, _ in parsed.alternate_urls}), 3
                )
                self.assertEqual(dict(parsed.alternate_urls), expected["alternates"])

    def test_rendered_pages_have_localized_navigation_and_language_switch(self):
        for relative_path, expected in RENDERED_PAGE_CONTRACTS.items():
            with self.subTest(page=relative_path):
                _, parsed = self.rendered_page(relative_path)
                self.assertEqual(
                    tuple(link["text"] for link in parsed.navigation_links),
                    expected["navigation"],
                )
                self.assertTrue(
                    all("hreflang" not in link["attributes"] for link in parsed.navigation_links)
                )
                self.assertEqual(len(parsed.language_switch_links), 1)
                switch = parsed.language_switch_links[0]
                self.assertEqual(switch["text"], expected["switch"]["text"])
                for attribute_name in ("href", "lang", "hreflang", "aria-label"):
                    self.assertEqual(
                        switch["attributes"].get(attribute_name),
                        expected["switch"][attribute_name],
                    )

    def test_rendered_pages_contain_no_legacy_site_identifiers(self):
        violations = []
        for relative_path in RENDERED_PAGE_CONTRACTS:
            text, _ = self.rendered_page(relative_path)
            for marker in FORBIDDEN_IDENTIFIERS:
                if marker in text:
                    violations.append((relative_path, marker))
        if violations:
            self.fail(
                "legacy markers found in rendered pages: %s"
                % ", ".join("%s:%r" % item for item in violations)
            )

    def test_rendered_root_relative_links_and_assets_resolve_inside_site(self):
        site_root = os.path.realpath(SITE_ROOT)
        for relative_path in RENDERED_PAGE_CONTRACTS:
            _, parsed = self.rendered_page(relative_path)
            self.assertGreater(
                len(parsed.root_relative_targets),
                0,
                "rendered page has no root-relative href/src targets: %s"
                % relative_path,
            )
            for tag, attribute_name, value in parsed.root_relative_targets:
                with self.subTest(
                    page=relative_path,
                    tag=tag,
                    attribute=attribute_name,
                    target=value,
                ):
                    decoded_path = unquote(urlsplit(value).path)
                    target = os.path.realpath(
                        os.path.join(site_root, decoded_path.lstrip("/"))
                    )
                    self.assertEqual(
                        os.path.commonpath((site_root, target)),
                        site_root,
                        "root-relative target escapes _site: %s" % value,
                    )
                    if decoded_path.endswith("/") or os.path.isdir(target):
                        target = os.path.join(target, "index.html")
                    self.assertTrue(
                        os.path.isfile(target),
                        "unresolved root-relative target in %s: %s"
                        % (relative_path, value),
                    )

    def test_rendered_sitemap_contains_exactly_six_canonical_urls(self):
        sitemap_path = os.path.join(SITE_ROOT, "sitemap.xml")
        self.assertTrue(
            os.path.isfile(sitemap_path),
            "rendered sitemap is missing: _site/sitemap.xml; run the site build first",
        )
        try:
            document = ET.parse(sitemap_path)
        except ET.ParseError as error:
            self.fail("rendered sitemap is not valid XML: %s" % error)
        locations = [
            (element.text or "").strip()
            for element in document.findall(
                ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )
        ]
        expected = {
            contract["canonical"] for contract in RENDERED_PAGE_CONTRACTS.values()
        }
        self.assertEqual(len(locations), 6)
        self.assertEqual(len(set(locations)), 6)
        self.assertEqual(set(locations), expected)

    def test_cudrt_corresponding_author_emphasis_covers_name_and_role(self):
        contracts = (
            (
                "publications.md",
                "publications/index.html",
                "Dinghao Xi (Corresponding Author 2)",
                "Dinghao Xi **(Corresponding Author 2)**",
            ),
            (
                "zh/publications.md",
                "zh/publications/index.html",
                "Dinghao Xi (通讯作者2)",
                "Dinghao Xi **(通讯作者2)**",
            ),
        )
        for source_path, rendered_path, expected, role_only_markup in contracts:
            with self.subTest(page=source_path, layer="source"):
                source = read_file(source_path)
                self.assert_contains(source, "**%s**" % expected, source_path)
                self.assertNotIn(role_only_markup, source or "")
            with self.subTest(page=rendered_path, layer="rendered"):
                _, parsed = self.rendered_page(rendered_path)
                self.assertIn(expected, parsed.strong_texts)

    def test_adviser_labels_are_localized_and_linked_consistently(self):
        adviser_url = "https://www.comp.nus.edu.sg/disa/bio/qiaodd/"
        contracts = (
            ("index.md", "Prof. Dandan Qiao"),
            ("zh/index.md", "Dandan Qiao 教授"),
        )
        for source_path, label in contracts:
            with self.subTest(page=source_path):
                source = read_file(source_path)
                self.assert_contains(
                    source,
                    "[%s](%s)" % (label, adviser_url),
                    source_path,
                )

    def test_rendered_author_avatar_alt_is_localized(self):
        for relative_path, expected in RENDERED_PAGE_CONTRACTS.items():
            with self.subTest(page=relative_path):
                _, parsed = self.rendered_page(relative_path)
                expected_alt = (
                    "奚鼎昊个人照片"
                    if expected["lang"] == "zh-CN"
                    else "Dinghao Xi bio photo"
                )
                self.assertEqual(parsed.bio_photo_alts, [expected_alt])

    def test_root_vendor_ignore_does_not_hide_frontend_vendor_assets(self):
        gitignore = read_file(".gitignore")
        rules = [
            line.strip()
            for line in (gitignore or "").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        with self.subTest(layer="configuration"):
            self.assertIn("/vendor/", rules)
            self.assertNotIn("vendor/", rules)

        frontend_asset = "assets/js/vendor/jquery-1.9.1.min.js"
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", frontend_asset],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        with self.subTest(layer="git-behavior"):
            self.assertEqual(
                result.returncode,
                1,
                "frontend runtime asset is incorrectly ignored: %s"
                % (result.stdout or result.stderr).strip(),
            )

    def test_rendered_site_name_links_to_localized_home(self):
        for relative_path, expected in RENDERED_PAGE_CONTRACTS.items():
            with self.subTest(page=relative_path):
                _, parsed = self.rendered_page(relative_path)
                expected_home = "/zh/" if expected["lang"] == "zh-CN" else "/"
                self.assertEqual(len(parsed.site_name_links), 1)
                self.assertEqual(parsed.site_name_links[0]["text"], "Dinghao Xi")
                self.assertEqual(
                    parsed.site_name_links[0]["attributes"].get("href"),
                    expected_home,
                )

    def test_about_image_is_web_optimized_and_root_relative(self):
        image_path = os.path.join(ROOT, "ruc.jpg")
        self.assertTrue(os.path.isfile(image_path), "required image is missing: ruc.jpg")
        with self.subTest(contract="file-size"):
            self.assertLessEqual(
                os.path.getsize(image_path),
                1_000_000,
                "ruc.jpg exceeds the 1,000,000-byte web budget",
            )

        for source_path in ("index.md", "zh/index.md"):
            with self.subTest(contract="root-relative-source", page=source_path):
                source = read_file(source_path)
                self.assert_contains(source, '<img src="/ruc.jpg"', source_path)

    def test_footer_is_localized_build_date_without_technical_attribution(self):
        patterns = {
            "en": re.compile(
                r"^© (?P<year>\d{4}) Dinghao Xi · Last updated: "
                r"(?:January|February|March|April|May|June|July|August|"
                r"September|October|November|December) "
                r"(?:[1-9]|[12]\d|3[01]), (?P=year)$"
            ),
            "zh-CN": re.compile(
                r"^© (?P<year>\d{4}) Dinghao Xi · 最近更新："
                r"(?P=year)年(?:[1-9]|1[0-2])月(?:[1-9]|[12]\d|3[01])日$"
            ),
        }
        forbidden_attribution = (
            "Published with",
            "powered by",
            "Minimal Mistakes",
            "Source code for this website",
            "发布于",
            "驱动",
            "源代码",
        )
        footer_include = read_file("_includes/footer.html")
        self.assertIsNotNone(
            footer_include,
            "required footer include is missing: _includes/footer.html",
        )
        for liquid_expression in (
            "{{ site.time | date: '%Y' }}",
            "{{ site.time | date: '%B %-d, %Y' }}",
            "{{ site.time | date: '%Y年%-m月%-d日' }}",
        ):
            with self.subTest(layer="source", required=liquid_expression):
                self.assertIn(liquid_expression, footer_include)
        for obsolete_link in (
            "pages.github.com",
            "jekyllrb.com",
            "mademistakes.com",
            "github.com/DinghaoXi/DinghaoXi.github.io",
        ):
            with self.subTest(layer="source", obsolete=obsolete_link):
                self.assertNotIn(obsolete_link, footer_include)

        for relative_path, expected in RENDERED_PAGE_CONTRACTS.items():
            with self.subTest(page=relative_path):
                _, parsed = self.rendered_page(relative_path)
                self.assertEqual(len(parsed.footer_container_texts), 1)
                self.assertEqual(len(parsed.footer_texts), 1)
                footer_text = parsed.footer_texts[0]
                footer_container_text = parsed.footer_container_texts[0]
                self.assertRegex(footer_text, patterns[expected["lang"]])
                for marker in forbidden_attribution:
                    self.assertNotIn(marker, footer_container_text)


    def test_about_pages_include_localized_personal_interests(self):
        contracts = (
            {
                "source": "index.md",
                "rendered": "index.html",
                "anchor": "## Professional Service",
                "heading_line": "## Beyond Research",
                "source_lines": (
                    "- **Badminton.** Always my undisputed No. 1.",
                    "- **Games.** CS:GO, Delta Force, Overwatch, Honor of Kings, and PUBG Mobile.",
                    "- **Reading.** Agatha Christie, science fiction, and horror.",
                    "Open to academic collaborations and gaming collaborations alike—happy to advance both papers and ranks.",
                ),
                "expected_suffix": """<br>

---

## Beyond Research

- **Badminton.** Always my undisputed No. 1.
- **Games.** CS:GO, Delta Force, Overwatch, Honor of Kings, and PUBG Mobile.
- **Reading.** Agatha Christie, science fiction, and horror.

Open to academic collaborations and gaming collaborations alike—happy to advance both papers and ranks.""",
                "expected_blocks": (
                    ("h2", "Beyond Research"),
                    ("li", "Badminton. Always my undisputed No. 1."),
                    ("li", "Games. CS:GO, Delta Force, Overwatch, Honor of Kings, and PUBG Mobile."),
                    ("li", "Reading. Agatha Christie, science fiction, and horror."),
                    ("p", "Open to academic collaborations and gaming collaborations alike—happy to advance both papers and ranks."),
                ),
                "source_counterpart_markers": (
                    "学术之外",
                    "- **羽毛球。** 毫无争议的 Top 1。",
                    "- **游戏。** CS:GO、三角洲行动、守望先锋、王者荣耀和刺激战场。",
                    "- **阅读。** 阿加莎·克里斯蒂的作品，以及科幻、恐怖类读物。",
                    "欢迎学术合作，也欢迎游戏合作——既可以一起推进论文，也可以一起推进段位。",
                ),
                "visible_markers": (
                    "Beyond Research",
                    "Badminton. Always my undisputed No. 1.",
                    "Games. CS:GO, Delta Force, Overwatch, Honor of Kings, and PUBG Mobile.",
                    "Reading. Agatha Christie, science fiction, and horror.",
                    "Open to academic collaborations and gaming collaborations alike—happy to advance both papers and ranks.",
                ),
                "forbidden_heading": "学术之外",
                "forbidden_closing": "欢迎学术合作，也欢迎游戏合作",
            },
            {
                "source": "zh/index.md",
                "rendered": "zh/index.html",
                "anchor": "## 学术服务",
                "heading_line": "## 学术之外",
                "source_lines": (
                    "- **羽毛球。** 毫无争议的 Top 1。",
                    "- **游戏。** CS:GO、三角洲行动、守望先锋、王者荣耀和刺激战场。",
                    "- **阅读。** 阿加莎·克里斯蒂的作品，以及科幻、恐怖类读物。",
                    "欢迎学术合作，也欢迎游戏合作——既可以一起推进论文，也可以一起推进段位。",
                ),
                "expected_suffix": """<br>

---

## 学术之外

- **羽毛球。** 毫无争议的 Top 1。
- **游戏。** CS:GO、三角洲行动、守望先锋、王者荣耀和刺激战场。
- **阅读。** 阿加莎·克里斯蒂的作品，以及科幻、恐怖类读物。

欢迎学术合作，也欢迎游戏合作——既可以一起推进论文，也可以一起推进段位。""",
                "expected_blocks": (
                    ("h2", "学术之外"),
                    ("li", "羽毛球。 毫无争议的 Top 1。"),
                    ("li", "游戏。 CS:GO、三角洲行动、守望先锋、王者荣耀和刺激战场。"),
                    ("li", "阅读。 阿加莎·克里斯蒂的作品，以及科幻、恐怖类读物。"),
                    ("p", "欢迎学术合作，也欢迎游戏合作——既可以一起推进论文，也可以一起推进段位。"),
                ),
                "source_counterpart_markers": (
                    "Beyond Research",
                    "- **Badminton.** Always my undisputed No. 1.",
                    "- **Games.** CS:GO, Delta Force, Overwatch, Honor of Kings, and PUBG Mobile.",
                    "- **Reading.** Agatha Christie, science fiction, and horror.",
                    "Open to academic collaborations and gaming collaborations alike—happy to advance both papers and ranks.",
                ),
                "visible_markers": (
                    "学术之外",
                    "羽毛球。 毫无争议的 Top 1。",
                    "游戏。 CS:GO、三角洲行动、守望先锋、王者荣耀和刺激战场。",
                    "阅读。 阿加莎·克里斯蒂的作品，以及科幻、恐怖类读物。",
                    "欢迎学术合作，也欢迎游戏合作——既可以一起推进论文，也可以一起推进段位。",
                ),
                "forbidden_heading": "Beyond Research",
                "forbidden_closing": "Open to academic collaborations and gaming collaborations alike",
            },
        )

        for contract in contracts:
            with self.subTest(page=contract["source"], layer="source"):
                source = read_file(contract["source"])
                self.assertIsNotNone(
                    source,
                    "required page file is missing: %s" % contract["source"],
                )
                self.assertEqual(source.count(contract["heading_line"]), 1)
                self.assertGreater(
                    source.index(contract["heading_line"]),
                    source.index(contract["anchor"]),
                )
                for line in contract["source_lines"]:
                    with self.subTest(page=contract["source"], source_line=line):
                        self.assertEqual(source.count(line), 1)
                self.assertTrue(source.rstrip().endswith(contract["expected_suffix"].rstrip()))
                self.assertNotIn(contract["forbidden_heading"], source)
                self.assertNotIn(contract["forbidden_closing"], source)
                for marker in contract["source_counterpart_markers"]:
                    self.assertNotIn(marker, source)

            with self.subTest(page=contract["rendered"], layer="rendered"):
                _, parsed = self.rendered_page(contract["rendered"])
                visible_text = " ".join("".join(parsed.visible_text_parts).split())
                for marker in contract["visible_markers"]:
                    with self.subTest(page=contract["rendered"], marker=marker):
                        self.assertEqual(visible_text.count(marker), 1)
                self.assertEqual(parsed.article_blocks[-5:], list(contract["expected_blocks"]))
                self.assertNotIn(contract["forbidden_heading"], visible_text)
                self.assertNotIn(contract["forbidden_closing"], visible_text)
                article_text = " ".join(text for _, text in parsed.article_blocks)
                rendered_counterpart_markers = tuple(
                    marker.replace("- **", "").replace("**", "")
                    for marker in contract["source_counterpart_markers"][1:4]
                ) + (
                    contract["source_counterpart_markers"][4],
                    contract["source_counterpart_markers"][0],
                )
                for marker in rendered_counterpart_markers:
                    self.assertNotIn(marker, article_text)

if __name__ == "__main__":
    unittest.main()
