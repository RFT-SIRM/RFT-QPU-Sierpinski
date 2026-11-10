# Site publication status

## Current state

The responsive architecture presentation is maintained at [index.html](index.html), with self-contained SVG assets under `docs/assets/`. It is intended to be reviewable from the repository checkout and contains no external JavaScript, font, analytics or image dependency.

**The site is not currently deployed.** The repository is private and GitHub Pages is not enabled for it. The former `rft-sirm.github.io/RFT-QPU-Sierpinski/` homepage URL therefore must not be advertised as a live website.

## Publication boundary

Do not make this repository public merely to turn on Pages. The repository contains proprietary implementation material, a Business 1.0 license, patent-oriented working documents, detailed coupler coefficient exports and hardware planning data.

The safe publication route is a separate, curated public site release containing only content explicitly cleared for disclosure. The source repository should remain private. The release bundle should be reviewed for:

- patent-counsel disclosure timing and any planned filing;
- ownership, licensing and third-party reference requirements;
- absence of internal netlists, detailed coefficients, private analysis and non-public working documents;
- consistency between every public numerical claim and the evidence boundary.

## Activation checklist

1. Prepare and review a curated public export of the site and approved SVG artwork.
2. Choose a hosting repository/account and confirm that public publication is authorized.
3. Configure the hosting source and deployment permissions there.
4. Verify the deployed URL, relative asset paths, mobile layout and accessibility.
5. Only after a successful deployment, replace the README architecture-brief badge with a live-site badge and set the repository Homepage field to the verified URL.

Until those steps pass, the README links to the architecture documentation and the old Live Demo badge remains removed.
