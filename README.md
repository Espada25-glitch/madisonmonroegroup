# Madison & Monroe website

Custom static HTML/CSS site for https://www.madisonmonroegroup.com/.
No framework, package installation, or application build is required.

## Review and deployment

GitHub's recorded `pages build and deployment` runs publish `main` through the managed `dynamic/pages/pages-build-deployment` workflow. No deployment workflow was checked into the original repository. `CNAME` holds the existing custom domain. This change does not alter domain, email, Pages settings, or the production branch.

The `codex/growth-advisory-redesign` branch is for review. **Do not merge until the owner approves the design and copy:** merging to `main` may publish automatically. The added validation workflow only reads and tests files; it has no deployment step.

## Local preview and checks

Run `python3 -m http.server 8765 --bind 127.0.0.1` from the repository and open http://127.0.0.1:8765/.
Run `python3 -m unittest discover -s tests -v` for metadata, landmarks, internal links/fragments, JSON-LD, six-service coverage, sitemap/robots consistency, and first-party file-size budgets.

## Content and structured data

The homepage retains the existing founder credentials and revenue history, explicitly attributed to John's prior organizations rather than Madison & Monroe client engagements. These are inherited owner-published claims, not independently audited financial results. The founder remains responsible for confirming that appointments and figures are current before release.

Removed the incomplete `Event` node for the Frontiers in Service conference and its WebPage mention reference. This homepage is a firm's introduction, not an event listing. The visible conference credential and external link remain. Organization, Person, WebSite, WebPage, Article and six Service nodes describe the actual visible content. Each service page includes its own Service and breadcrumb schema. No fabricated event dates, ratings, prices, or client outcomes were added.

Reference: https://developers.google.com/search/docs/appearance/structured-data/event and https://schema.org/Service.

After an approved production release, use Search Console URL Inspection and request validation/recrawling. The code change alone cannot clear Google's cached report before deployment and recrawl.

## Verification on 2026-11-11

- Five automated regression checks pass across eight HTML pages.
- Homepage layout measured at 1440px and 375px: no horizontal document overflow.
- Commercial-performance page measured at 375px: no horizontal document overflow.
- Browser verified homepage-to-service navigation, expandable fee FAQ, and loaded HubSpot form with labeled fields.
- Mobile visual inspection completed. Desktop screenshot capture was clipped by the preview surface; desktop document geometry was checked but full desktop visual QA remains a review item.
- Existing HubSpot form, analytics identifiers, contact email, social preview image and favicon assets preserved. No test lead was submitted.
- No Lighthouse score or comprehensive assistive-technology audit is claimed. Third-party form and analytics performance depends on their providers; size budgets cover first-party files only.
