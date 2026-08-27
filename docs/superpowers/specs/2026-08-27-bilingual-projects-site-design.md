# Bilingual Academic Site and Projects Page Design

Date: 2026-08-27
Repository: `DinghaoXi/DinghaoXi.github.io`

## Objective

Convert the current academic homepage into a maintainable English/Chinese site, add a Projects section containing Dinghao Xi's six current projects, and remove inherited pages, media, configuration, and tracking that belong to the former template owner. Preserve the current visual style and all existing valid English URLs.

## Confirmed Requirements

- Keep English as the default language at the existing routes.
- Put Chinese counterparts under `/zh/`.
- Provide bilingual versions of About, Publications, and Projects.
- Add a page-level language switch that opens the corresponding page in the other language.
- Do not redirect automatically based on browser language.
- Retain the current typography, spacing, sidebar, and text-oriented page style.
- Translate and polish the Chinese content from the current English source; create accurate English translations for the supplied Chinese project records.
- Group Projects into Research Projects and Teaching Reform and Course Development Projects.
- Mark Dinghao Xi as Principal Investigator for all six projects.
- Show each project's funding amount, but do not show a combined total.
- Remove old or third-party site content and configuration. Git history remains the recovery mechanism.

## Architecture

Use paired static Jekyll pages rather than client-side translation or a multilingual plugin. English routes remain `/`, `/publications/`, and `/projects/`; Chinese routes are `/zh/`, `/zh/publications/`, and `/zh/projects/`.

Each page declares `lang` and `alternate_url` in its front matter. Navigation labels and URLs are stored by language in `_data/navigation.yml`. The existing navigation include selects the correct language set and renders a final `中文` or `EN` link to `alternate_url`. The document layout reads `page.lang` for the HTML `lang` attribute. The head include publishes canonical and reciprocal `hreflang` links for paired pages.

No JavaScript is required for language switching. A missing or invalid alternate route must never generate a broken switch: every published core page must have a paired counterpart before deployment.

## Page Content

### English

- About Me: preserve the verified personal profile, academic background, research interests, news, and professional service, with only language and grammar polishing that does not change factual meaning.
- Publications: preserve publication titles, authors, venues, years, and source links; normalize headings and obvious typographical errors without changing scholarly claims.
- Projects: publish the six supplied records in the user's confirmed order, with funding program, project or course title, role, period, and funding amount.

### Chinese

- 关于我: a faithful professional translation of the current English About page.
- 发表成果: preserve original publication titles and source links; translate section labels and publication metadata prose while retaining names and official venue titles.
- 项目: use the supplied Chinese wording as the factual authority, lightly normalizing punctuation and layout only.

Funding is formatted as `30万元`, `9万元`, and so on in Chinese and as `RMB 300,000`, `RMB 90,000`, and so on in English. No total is displayed.

## Projects Records

### Research Projects

1. National Natural Science Foundation of China Young Scientists Fund project, “Differentiated Causal Pathways and Temporal Dynamics through Which Interaction Credibility in Emotional Companion Agents Shapes User Trust,” 2027–2029, Principal Investigator, RMB 300,000.
2. China UnionPay commissioned research project, “Prospects for the Application of Artificial Intelligence and Other Emerging Technologies in Money-Laundering Risk Prevention and Anti-Money Laundering Compliance,” 2026–2027, Principal Investigator, RMB 300,000.
3. Fundamental Research Funds for the Central Universities project at Shanghai University of Finance and Economics, “Predicting Consumer Behavior in E-commerce Livestreaming Based on Multimodal Deep Learning,” 2024–2026, Principal Investigator, RMB 90,000.

### Teaching Reform and Course Development Projects

1. 2025 Integrated Practice Course Development Project at Shanghai University of Finance and Economics, development of the undergraduate course “Applications of Large Language Models in Economics and Management,” 2025–2026, Principal Investigator, RMB 30,000.
2. Key Undergraduate Teaching Reform Project at Shanghai University of Finance and Economics, “Scenario-Based Teaching Reform for Interdisciplinary Courses Empowered by AR/VR,” based on the undergraduate course “Applications of Large Language Models in Economics and Management,” 2026–2028, Principal Investigator, RMB 60,000.
3. 2026 Graduate “AI+” Development Project at Shanghai University of Finance and Economics, development of the graduate course “Data Science,” 2026–2027, Principal Investigator, RMB 50,000.

## Legacy Cleanup

Delete inherited pages and assets that clearly identify Cai Hanlin, GuangLun, Fuzhou University, or the old template site, including the old awards, hobbies, blogs, projects content, backup folder, IDE metadata, Hanlin CV files, `mypaper/`, and media referenced only by those pages. Rebuild `/projects/` rather than removing the route.

Remove the stale `caihanlin.com` CNAME, sitemap entries, Disqus integration, analytics/counter identifiers, former-owner source links, and identity comments. Generate a correct sitemap for the six core routes. Preserve the theme license where required, all runtime layout/include dependencies, Dinghao Xi's current profile and publication files, current photographs/icons, and maintainable CSS/JavaScript source files.

The unlinked `file/DinghaoXi_ch.pdf` is treated as a remaining obsolete resume artifact and removed because the Resume section has already been retired. The Search Console verification file is preserved unless it is conclusively attributable to the former owner.

## Quality and Deployment Gates

1. Build the site locally with the repository's supported Jekyll configuration.
2. Verify all six core routes and all language switches.
3. Verify `lang`, canonical, and reciprocal `hreflang` metadata.
4. Scan rendered output for broken internal links and missing local assets.
5. Scan source and rendered output for former-owner names, domains, analytics IDs, Disqus IDs, and deleted-file references.
6. Visually inspect English and Chinese About, Publications, and Projects pages at desktop and narrow/mobile widths.
7. Commit the tested changes and deploy through GitHub Pages.
8. Confirm the GitHub Pages workflow succeeds, the six live routes render, language switches work, and selected removed artifacts return 404.

## Rollback

All changes are committed to Git. If a deployment problem is found, revert the implementation commit or restore a specific file from the last known-good commit `e82770d`.
