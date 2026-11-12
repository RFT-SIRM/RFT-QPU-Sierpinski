# Site publication status

## Current state

The repository is **public**. The repository metadata currently reports `has_pages=false` and an empty Homepage field. There is no Pages deployment workflow in `.github/workflows/`; the existing workflow runs tests and numerical reproductions only.

`docs/index.html` is a static, self-contained architecture presentation. It is stored in the repository as source material; GitHub does not automatically publish or execute it merely because the file exists. Its seven local SVG references were checked against the current tree and all are present. The page has embedded CSS, no JavaScript runtime and no external stylesheet dependency.

**The website is not currently deployed.** The expected project-site address, once Pages is enabled and verified, is:

`https://rft-sirm.github.io/RFT-QPU-Sierpinski/`

Do not advertise this as a live site until it loads successfully over HTTPS and the asset paths are verified in the browser.

## How to publish this page

If the maintainer wants the HTML page to be the public landing page:

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select branch `main` and folder `/docs`.
4. Save, then open the expected URL above and test the page, every diagram, mobile layout and accessibility.

The entry file is already at the top level of the selected `/docs` folder, and its image references are relative to that folder. No custom build pipeline is required for this static page.

## Keep the repository and site distinct

The README is the canonical technical entry point. The HTML page is a visual summary only; it must not replace the README, technical reports, LICENSE, PATENTS.md or evidence-boundary documents. It must continue to distinguish model outputs from fabricated or measured hardware.

Before enabling Pages:
- confirm that every displayed number matches the current model evidence;
- keep the complex Z-link and nine-tone schedule blockers visible;
- label numerical process overlap and state fidelity as closed-system model outputs, not measured device fidelity;
- ensure the footer links to the repository and current licensing documents.

Until deployment is verified, link to the repository README rather than advertising the expected Pages URL as live.
