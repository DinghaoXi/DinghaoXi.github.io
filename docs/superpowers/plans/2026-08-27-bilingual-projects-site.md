# Bilingual Academic Site and Projects Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a tested English/Chinese academic site with a new six-item Projects section and remove inherited former-owner content and configuration.

**Architecture:** Use six paired static Jekyll pages. English keeps the existing routes; Chinese lives under `/zh/`. Page front matter supplies `lang` and `alternate_url`; language-keyed data drives navigation and the existing layout renders metadata and the alternate link without JavaScript.

**Tech Stack:** GitHub Pages, Jekyll 3.x, Liquid, Markdown/Kramdown, HTML/CSS, Python 3 standard-library verification, GitHub Actions.

---

### Task 1: Add a failing site contract test

**Files:**
- Create: `tests/test_site.py`

- [ ] **Step 1: Write source-level contract tests**

Create a `unittest` suite that defines the six page pairs, exact routes, navigation labels, required project funding and role markers, correct sitemap routes, and forbidden former-owner identifiers.

```python
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {
    "index.md": ("en", "/zh/"),
    "publications.md": ("en", "/zh/publications/"),
    "projects.md": ("en", "/zh/projects/"),
    "zh/index.md": ("zh-CN", "/"),
    "zh/publications.md": ("zh-CN", "/publications/"),
    "zh/projects.md": ("zh-CN", "/projects/"),
}
FORBIDDEN = (
    "caihanlin.com", "Cai Hanlin", "Hanlin CAI", "蔡汉霖",
    "GuangLun2000", "lancecai", "G-T5N5JY1E21", "4c8f7caa",
)

class SiteContractTest(unittest.TestCase):
    def test_page_pairs(self):
        for relative, (lang, alternate) in PAIRS.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^lang:\\s*{re.escape(lang)}\\s*$")
            self.assertRegex(text, rf"(?m)^alternate_url:\\s*{re.escape(alternate)}\\s*$")

    def test_navigation_and_projects(self):
        nav = (ROOT / "_data/navigation.yml").read_text(encoding="utf-8")
        for marker in ("About Me", "Publications", "Projects", "关于我", "发表成果", "项目"):
            self.assertIn(marker, nav)
        projects = (ROOT / "projects.md").read_text(encoding="utf-8")
        for marker in ("Principal Investigator", "RMB 300,000", "RMB 90,000", "RMB 60,000"):
            self.assertIn(marker, projects)

    def test_no_former_owner_identifiers(self):
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "docs" in path.parts or path.name == "LICENSE":
                continue
            if path.suffix.lower() not in {".md", ".html", ".xml", ".yml", ".yaml", ".js"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in FORBIDDEN:
                self.assertNotIn(marker, text, f"{marker!r} remains in {path.relative_to(ROOT)}")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest -v tests/test_site.py`

Expected: FAIL because `_data/navigation.yml` and the three `zh/` pages do not exist and former-owner identifiers remain.

- [ ] **Step 3: Commit the failing contract**

Run: `git add tests/test_site.py && git commit -m "test: define bilingual site contract"`

### Task 2: Implement the bilingual site shell

**Files:**
- Create: `_data/navigation.yml`
- Modify: `_config.yml`
- Modify: `_includes/navigation.html`
- Modify: `_includes/head.html`
- Modify: `_includes/footer.html`
- Modify: `_includes/scripts.html`
- Modify: `_layouts/page.html`

- [ ] **Step 1: Create language-keyed navigation data**

```yaml
en:
  - title: About Me
    url: /
  - title: Publications
    url: /publications/
  - title: Projects
    url: /projects/
zh-CN:
  - title: 关于我
    url: /zh/
  - title: 发表成果
    url: /zh/publications/
  - title: 项目
    url: /zh/projects/
```

- [ ] **Step 2: Clean `_config.yml`**

Keep Dinghao Xi's owner profile and Google verification token. Remove the old `links` array, former-owner social comments, and Disqus block. Exclude `docs`, `tests`, `scripts`, `vendor`, and `Gemfile*` from published output.

- [ ] **Step 3: Render localized navigation and the page-paired switch**

Use `site.data.navigation[page.lang | default: 'en']`, retain active-page styling, and render `中文` or `EN` to `page.alternate_url` with `lang` and `hreflang` attributes.

- [ ] **Step 4: Localize document and social metadata**

Set the HTML `lang` from page front matter. In `head.html`, derive `og:locale`, use absolute canonical URLs, and publish `hreflang="en"`, `hreflang="zh-CN"`, and `hreflang="x-default"`. Remove references to missing Apple touch icons.

- [ ] **Step 5: Remove former-owner tracking and footer identity**

Remove Counter.dev and Google Analytics from the active page layout and `_includes/scripts.html`. Keep jQuery and `main.min.js`. Point the footer source link to `DinghaoXi/DinghaoXi.github.io` and remove former-owner comments.

- [ ] **Step 6: Run focused tests and commit**

Run: `python3 -m unittest -v tests/test_site.py`

Expected: only content-pair and remaining legacy-file assertions fail.

Run: `git add _config.yml _data/navigation.yml _includes _layouts/page.html && git commit -m "feat: add bilingual site navigation shell"`

### Task 3: Publish paired About pages

**Files:**
- Modify: `index.md`
- Create: `zh/index.md`

- [ ] **Step 1: Add English pairing metadata**

Use `permalink: /index.html`, `lang: en`, `alternate_url: /zh/`, and an English description. Preserve verified facts and links; correct grammar without changing meaning.

- [ ] **Step 2: Create the Chinese counterpart**

Use `permalink: /zh/index.html`, `lang: zh-CN`, and `alternate_url: /`. Translate every visible section while preserving dates, affiliations, links, and service records. Required headings are `关于我`, `教育与工作经历`, `研究兴趣`, `新闻与动态`, and `学术服务`.

- [ ] **Step 3: Test and commit**

Run: `python3 -m unittest -v tests.test_site.SiteContractTest.test_page_pairs`

Expected: only Publications/Projects Chinese-pair failures remain.

Run: `git add index.md zh/index.md && git commit -m "content: add bilingual about pages"`

### Task 4: Publish paired Publications pages

**Files:**
- Modify: `publications.md`
- Delete: `publications-zh.md`
- Create: `zh/publications.md`

- [ ] **Step 1: Pair and normalize the English page**

Add `lang: en` and `alternate_url: /zh/publications/`. Preserve every publication title, author list, venue, year, and link. Correct only obvious English labels and typos such as `Lastest`, singular section headings, and `Volumn`.

- [ ] **Step 2: Replace the inherited Chinese page**

Create `/zh/publications/` with `lang: zh-CN` and `alternate_url: /publications/`. Retain original English paper titles, names, official venue titles, volumes, years, and links; translate section headings and surrounding metadata prose.

- [ ] **Step 3: Verify URL parity and commit**

Extract ordered external Markdown URLs from both files with Python and assert equality. Expected: identical link count and order.

Run: `git add publications.md publications-zh.md zh/publications.md && git commit -m "content: add bilingual publications pages"`

### Task 5: Rebuild Projects in both languages

**Files:**
- Replace: `projects.md`
- Create: `zh/projects.md`

- [ ] **Step 1: Replace the English page**

Use `/projects/`, `lang: en`, and `alternate_url: /zh/projects/`. Render Research Projects and Teaching Reform and Course Development Projects in the user's final order. Each entry includes funding program, translated title or course, `Principal Investigator`, period, and its RMB amount.

- [ ] **Step 2: Create the Chinese page**

Use `/zh/projects/`, `lang: zh-CN`, and `alternate_url: /projects/`. Preserve the exact distinctions `建设本科生课程`, `依托本科生课程`, and `建设研究生课程`. Every entry includes `负责人：奚鼎昊`, period, and its amount. Do not display a total.

- [ ] **Step 3: Verify records and commit**

Use Python assertions for all five distinct periods, six project entries, two 30万元/RMB 300,000 entries, the four smaller amounts, and absence of `83万元`/`RMB 830,000`.

Run: `git add projects.md zh/projects.md && git commit -m "content: publish bilingual projects"`

### Task 6: Remove inherited content and stale configuration

**Files:**
- Delete: `.idea/`, `backup/`, `blogs/`, `blogs.md`, `awards.md`, `awards-zh.md`, `hobbies.md`
- Delete: `mypaper/`, all Hanlin CV files, `file/DinghaoXi_ch.pdf`
- Delete: former-owner-only project/hobby/blog images from the design audit
- Delete: `CNAME`, `_includes/disqus.html`, legacy README fragments, `.github/FUNDING.yml`
- Review: retained layouts/includes for identity comments and analytics

- [ ] **Step 1: Delete confirmed targets explicitly**

Use `git rm` on the exact targets above. Preserve `LICENSE`, `README.md`, `index.md`, `publications.md`, `ruc.jpg`, `xdh.jpg`, `images/xdh.jpg`, current icons, active layouts/includes, and CSS/JavaScript/font runtime assets.

- [ ] **Step 2: Remove stale references from retained source**

Run `rg` for every forbidden identifier and remove matches outside `LICENSE` and engineering documentation. Preserve the MIT license because the site remains derived from the licensed theme.

- [ ] **Step 3: Test tracked paths and commit**

Run: `python3 -m unittest -v tests/test_site.py`

Run: `git ls-files | rg '(^|/)(awards|blogs|backup|mypaper|hobbies|CV-Hanlin|Resume-Hanlin|DinghaoXi_ch)'`

Expected: tests pass and the path scan returns no output.

Run: `git add -A && git commit -m "chore: remove inherited site content and tracking"`

### Task 7: Add a correct sitemap and reproducible build

**Files:**
- Modify: `sitemap.xml`
- Create: `Gemfile`

- [ ] **Step 1: Publish only the six canonical sitemap routes**

Use `{{ site.url }}` with `/`, `/publications/`, `/projects/`, `/zh/`, `/zh/publications/`, and `/zh/projects/`. Use the standard namespace `http://www.sitemaps.org/schemas/sitemap/0.9`.

- [ ] **Step 2: Add the GitHub Pages dependency**

```ruby
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
```

- [ ] **Step 3: Install locally and build**

Run:

```bash
gem install --user-install bundler -v 2.4.22
bundle _2.4.22_ config set --local path vendor/bundle
bundle _2.4.22_ install
bundle _2.4.22_ exec jekyll build --trace
```

Expected: exit 0 and all six HTML files under `_site/`.

- [ ] **Step 4: Commit build inputs**

Run: `git add sitemap.xml Gemfile Gemfile.lock && git commit -m "build: add reproducible GitHub Pages build"`

### Task 8: Verify rendered pages and visual behavior

**Files:**
- Modify: `tests/test_site.py`

- [ ] **Step 1: Add rendered-output checks**

Parse all six generated HTML files. Assert exact HTML language, canonical and reciprocal `hreflang`, localized navigation labels, paired language-switch URLs, and absence of former-owner identifiers. Extract root-relative `href`/`src` targets and assert each local target exists in `_site`.

- [ ] **Step 2: Run complete verification**

Run:

```bash
bundle _2.4.22_ exec jekyll build --trace
python3 -m unittest -v tests/test_site.py
git diff --check
```

Expected: build succeeds, every test passes, and `git diff --check` prints nothing.

- [ ] **Step 3: Serve and inspect**

Run `bundle _2.4.22_ exec jekyll serve --host 127.0.0.1 --port 4000`. Inspect every route at desktop and approximately 390px width. Confirm current styling, Chinese wrapping, Projects readability, active navigation, and every language switch.

- [ ] **Step 4: Commit rendered checks**

Run: `git add tests/test_site.py && git commit -m "test: verify rendered bilingual site"`

### Task 9: Review, deploy, and verify live

**Files:**
- Review: all changes since `e82770d`

- [ ] **Step 1: Re-run all gates**

Run: `git diff --check e82770d..HEAD`

Run: `bundle _2.4.22_ exec jekyll build --trace`

Run: `python3 -m unittest -v tests/test_site.py`

Expected: all commands exit 0 and the diff contains only approved bilingual content, cleanup, tests, and documentation.

- [ ] **Step 2: Publish without force-push**

Use the available authenticated GitHub route to put the tested commits on `main`. Confirm `main` points at the final implementation commit.

- [ ] **Step 3: Verify deployment**

Wait for the Pages workflow to report `Success`; record the run URL and commit SHA.

- [ ] **Step 4: Verify live behavior**

Open all six live routes. Confirm headings, navigation, language switches, six project records, roles, periods, and amounts. Confirm representative removed CV/blog/media URLs return 404 and live HTML contains none of the removed analytics identifiers.

- [ ] **Step 5: Report completion**

Report commits, deployment run, live routes, tests, cleanup scope, and Git-history recovery.
