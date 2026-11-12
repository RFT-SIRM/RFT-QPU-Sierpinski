# IP, ownership, public disclosure and licensing

**Project:** RFT-QPU-Sierpinski  
**Project author attribution:** Evgeny Zaprudnov  
**Review date:** 12 November 2026  
**Status:** public-release documentation; not legal advice

## 1. Public research record

The repository is being prepared for public technical inspection, reproducibility, independent review and collaboration. It contains the finite Sierpiński graph model, SU(2) Hamiltonian, numerical analyses, proposed transmon mapping, coefficient tables, circuit-model studies, scripts, tests, reports and selected numerical archives.

Publication is intentional. The repository is not presented as a fabricated or experimentally validated quantum processor. See [README](README.md), [evidence boundary](docs/DISCLOSURE_BOUNDARY.md) and [validation plan](docs/VALIDATION_PLAN.md).

## 2. Source licence — BUSL-1.1

The root [LICENSE](LICENSE) applies Business Source License 1.1 (BUSL-1.1) to the original project materials that the Licensor owns or is authorised to license.

- **Current permissions:** copying, modification, derivative works, redistribution and non-production use, subject to the exact licence terms.
- **Additional Use Grant:** None.
- **Production use:** not granted during the BUSL-1.1 initial term; requires a separate written commercial licence.
- **Change Date:** 12 November 2030, or the fourth anniversary of first public distribution of the relevant version if earlier.
- **Change License:** GNU GPL version 2.0 only (GPL-2.0-only).

BUSL-1.1 is source-available, not an OSI-approved open-source licence during its initial term. It permits independent study, reproduction, experimentation and collaboration within its non-production scope. It does not grant trademark rights. The exact root LICENSE controls if this summary differs from the licence text.

The Change Date and Change License are material licence terms. At the Change Date, or the fourth anniversary of first public distribution if earlier, the rights granted under BUSL-1.1 for that version terminate and rights under the stated Change License take effect. Each later release may have its own BUSL parameters.

## 3. Supplemental patent grant

[PATENTS.md](PATENTS.md) contains a separate patent grant intended to accompany BUSL-1.1. It is non-exclusive, worldwide and royalty-free, but only covers patent claims that the Licensor actually owns or legally controls and that are necessarily infringed by the Licensor's contribution(s) alone or in combination with the Licensed Work.

The patent grant is coextensive with the activity scope of the source licence during its initial term; after the Change Date, it may also cover production uses permitted by GPL-2.0-only. It does not override BUSL-1.1's initial non-production restriction and is not an Additional Use Grant. Because the grant is perpetual and irrevocable except for defensive termination, it may pre-license qualifying claims that the Licensor later obtains or controls. This is a patent grant to recipients, not a reservation that preserves exclusivity; see PATENTS.md and obtain patent-counsel review before relying on it.

## 4. Patent status and public disclosure

No patent application number, filing date, patent office, published application or granted patent for this project was identified in this repository as of 12 November 2026. This is a repository audit observation only; it does not prove that no document exists outside the repository.

Public disclosure can affect patent novelty and filing options. The legal effect depends on jurisdiction, date, content and enabling character. Grace periods vary and must not be assumed. A later filing cannot make a prior public disclosure confidential again. Anyone considering a filing should obtain jurisdiction-specific advice before relying on any novelty or priority position.

## 5. Separate legal concepts

| Rights category | What it may cover | What it does not establish |
|---|---|---|
| Authorship attribution | Credit for original project materials | Patent inventorship or ownership of every contribution |
| Copyright | Original code, prose, diagrams, graphics and protected selection/arrangement | A monopoly over abstract mathematical ideas, facts, equations, methods or concepts as such |
| Patent rights | Only valid claims, in jurisdictions and for the term in which they exist | Protection merely because an idea or technical note appears in this repository |
| Know-how / trade secrets | Information kept confidential under legally sufficient controls | Secrecy after unrestricted public disclosure |
| Trademark / brand | Project names and marks, subject to applicable law | Rights in the underlying technical architecture |

## 6. Authorship, inventorship and chain of title

Project materials use the requested attribution **Evgeny Zaprudnov**. Patent inventorship is a separate legal determination that depends on the actual conception of each proposed claim. Coding, testing, funding, repository administration or general project leadership does not automatically resolve inventorship.

Before any commercial licence, assignment, option or patent filing, the relevant parties should confirm:
1. original notebooks, dated design records and source history;
2. all human contributors and their actual contributions;
3. applicable employment, contractor, university, grant or consultancy obligations;
4. signed assignments and permissions where required;
5. third-party software, data, images, fonts and other asset licences;
6. the correct individual or legal entity authorised to act as licensor or applicant.

The GitHub repository owner and the project-author attribution do not, by themselves, prove the complete chain of title. Third-party components remain governed by their own licences and notices.

## 7. Research collaboration

The project welcomes technically substantive review, reproducibility checks, mathematical discussion, circuit-QED review, control engineering and proposals for a physical demonstrator. Useful collaboration areas include:
- implementation of the non-commuting SU(2) link network;
- resolution of the resonant complex Z-link requirement;
- redesign and validation of the graph-wide pump/frequency allocation;
- open-system, thermal, flux-line and crosstalk modelling;
- layout extraction, EM simulation, fabrication and cryogenic measurement;
- independent review of the one-cell and two-cell demonstrator path.

Use GitHub Issues for public technical discussion and pull requests for documented corrections. Do not publish secrets, credentials, third-party confidential materials or personal data in public issues.

## 8. Commercial discussions

Separate written agreements may cover production deployment, hardware manufacture, integration, sale, patent rights (if and when valid rights exist and the Licensor controls them), defined know-how, territory, field of use, sublicensing, exclusivity, royalties, milestones, and ownership/licensing of improvements.

No exclusivity, valuation, licence, option, assignment, funding commitment or partner agreement is represented as already agreed. Repository access alone grants no commercial production right.

## 9. References

- [Business Source License 1.1 — SPDX](https://spdx.org/licenses/BUSL-1.1.html)
- [Business Source License 1.1 — MariaDB](https://mariadb.com/bsl11/)
- [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [WIPO: Patent FAQs](https://www.wipo.int/en/web/patents/faq_patents)
- [EPO: 2026 Guidelines — state of the art](https://www.epo.org/en/legal/guidelines-epc/2026/g_iv_1.html)

This document is informational and is not a legal opinion. Patent inventorship, ownership, licence authority and the effect of public disclosure require review by qualified counsel in the relevant jurisdictions.
