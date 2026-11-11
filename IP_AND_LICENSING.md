# IP, ownership, confidentiality and licensing framework

**Internal working document · 11 November 2026 · Project author attribution: Evgeny Zaprudnov**

This document organises the project's IP diligence. It does not create a patent right, prove ownership, replace an assignment, or grant a commercial licence.

## 1. Repository audit at this review point

The Sierpinski repository is private. The repository contains an attribution placeholder in its former citation metadata, a broad proprietary notice, a patent-oriented technical specification and engineering records. This revision corrects the attribution to Evgeny Zaprudnov and separates authorship, copyright, patent rights and trade-secret controls.

The following items are **not recorded in this repository** as of 11 November 2026:

- patent application number, filing date, patent office or priority claim;
- granted patent or published patent application;
- signed invention assignment, contributor assignment or employment/consulting IP agreement;
- signed NDA register or disclosure chronology;
- signed commercial licence, option, term sheet or evaluation agreement.

These are repository findings only. They do not prove that no such documents exist outside the repository.

## 2. Keep the repository private

Maintain private visibility while counsel reviews filing options and ownership. Before sharing access, review GitHub collaborators, teams, tokens, connected applications, forks and mirrors. Use individual accounts with multi-factor authentication, least-privilege access and a documented access list. Keep dated backups of the repository and source artifacts.

Private repository settings are a useful access control, not a substitute for an NDA, an invention assignment or patent filing. The repository's current private status does not establish that no earlier public or non-confidential disclosure occurred.

Do not distribute enabling technical details, raw coupling maps, claim concepts, full circuit drawings or source code to prospective partners until the disclosure boundary and agreement are approved.

## 3. Separate the different rights

| Rights category | What it can cover | What it does not establish |
|---|---|---|
| Authorship attribution | Who is credited for the project materials | Legal ownership of every work or invention |
| Copyright | Original source code, prose, diagrams, graphics and qualifying selection/arrangement | A monopoly over abstract mathematical facts, ideas, methods or system concepts |
| Patent rights | Only the subject matter within valid claims of an application/patent, if granted | Protection merely because a technical disclosure or claim concept is written in this repository |
| Trade secrets / know-how | Confidential technical information maintained under effective secrecy controls | Protection after unrestricted public disclosure; ownership without a title chain |
| Trademark / brand | Project or product names and marks, subject to applicable law | Rights in the technical architecture itself |

The old wording that attempted to prohibit copying of mathematical parameters or the architecture as such has been removed. A repository notice should not imply that copyright alone protects abstract equations, ideas or methods. Patent and trade-secret protection are separate legal questions.

## 4. Authorship, inventorship and chain of title

Project documents should credit **Evgeny Zaprudnov** as the project author, as requested. Inventorship is a separate legal determination. Counsel should identify the actual human contributor(s) to the conception of each proposed patent claim; authorship of the repository, coding, testing or funding alone does not automatically resolve inventorship.

Before licensing or assigning rights, assemble a chain-of-title file:

1. dated notebooks, source history and original design records;
2. names and contributions of all collaborators;
3. employment, contractor, university, grant and consultancy terms that may allocate IP;
4. signed assignments from relevant inventors/authors where required;
5. third-party software, libraries, fonts, images, data and other licence obligations;
6. confirmation that RFT-SIRM is authorised to act as owner, licensor or applicant if rights are to be held or exercised through that organisation.

The GitHub account or repository owner is not, by itself, proof of ownership of every invention or work in the repository.

## 5. Patent strategy — questions for counsel

The highest-value patent review is likely to focus on specific technical embodiments rather than the abstract Sierpinski graph or the spectral-moment formula alone. Candidate areas for counsel to investigate are:

- a physical mode-pair and coupler network implementing a specified graph Hamiltonian with non-commuting SU(2) links;
- a concrete phase-engineered exchange implementation that resolves the resonant complex Z edge;
- calibration and phase-consistency methods for a multi-channel parametric network;
- preparation, control and readout of the selected two-dimensional subspace;
- a realizable two-cell differential-density interaction and its control sequence;
- measurement-based validation of the effective Hamiltonian, projected controls and leakage criteria.

The current complex Z link remains unresolved. Do not draft a claim as if the single-real-static-coupler problem has already been solved. The Stage 11B A–coupler–B gate model is a separate three-mode simulation, not proof of the full twelve-mode tile.

The European Patent Office's 2026 guidance distinguishes abstract mathematical methods from technical implementations and assesses whether a mathematical method contributes to technical character. Novelty, inventive step, industrial applicability and sufficiency still need examination. Counsel must select the filing jurisdiction and claim strategy.

## 6. Confidentiality and disclosure chronology

Create a dated record for every external disclosure, including:

- preprints, articles, posters, conference talks and competitions;
- websites, GitHub Pages, public source mirrors and downloadable archives;
- demonstrations, investor meetings, pitch decks and technical calls;
- emails, messaging threads and attachments;
- disclosure to suppliers, universities, foundries or engineering contractors;
- access by people not bound by confidentiality.

For each disclosure, retain the material version, date, recipient, channel, whether it was public, NDA status and supporting evidence. Use [the disclosure log template](docs/DISCLOSURE_LOG_TEMPLATE.md).

Before filing, WIPO recommends avoiding non-confidential pre-filing disclosure; any grace period depends on jurisdiction and the type of disclosure. For unavoidable investor or partner disclosure, obtain a signed NDA before providing enabling detail. An NDA does not replace a patent filing or grant a licence.

## 7. Partner access model

1. **Non-confidential overview:** use a short, sanitised brief that explains the problem, proposed architecture class, evidence categories and development milestones without exposing enabling implementation detail.
2. **Confidential discussion:** execute an NDA signed by the correct legal parties before sharing technical detail.
3. **Controlled technical evaluation:** define the permitted purpose, access persons, data-room rules, no-publication obligations, reverse-engineering restrictions where enforceable, return/deletion obligations and ownership of feedback or improvements.
4. **Commercial negotiation:** identify background IP, foreground IP, improvements, territories, fields of use, sublicensing and patent cost responsibilities.
5. **Definitive agreement:** execute only after rights-holder and inventorship checks.

## 8. Commercial licensing structure

A future licence can be structured separately for:

- **software and documentation:** source access, internal evaluation, modification, derivative works, redistribution and support;
- **patent rights:** only claims and territories actually owned or controlled;
- **know-how:** defined confidential packages and controlled access;
- **hardware implementation:** manufacturing, integration, field of use, territory and sublicensing;
- **improvements:** ownership, disclosure, licence-back and prosecution responsibilities.

Possible commercial terms include an evaluation fee, milestone payments, field-of-use exclusivity, annual minimums, royalties, sublicensing rights, audit rights, patent cost allocation and termination/return obligations. No commercial term should be presented as already agreed.

## 9. Counsel checklist before external circulation

- [ ] Confirm the legal name and contact details of the intended author/applicant/rights holder.
- [ ] Confirm all actual inventors claim by claim.
- [ ] Review original source records and the chain of title.
- [ ] Inventory third-party dependencies and assets.
- [ ] Search prior art and freedom to operate.
- [ ] Review novelty and technical character in intended jurisdictions.
- [ ] Review whether the written disclosure enables each proposed technical embodiment.
- [ ] Resolve or bound the complex Z-link implementation.
- [ ] Verify all prior disclosure dates and recipients.
- [ ] Decide filing route, filing date, priority strategy and international budget.
- [ ] Approve NDA and technical-evaluation templates.
- [ ] Approve a sanitized external brief and a controlled technical data room.

## 10. Official references

- WIPO — How to Protect Inventions through Patents: https://www.wipo.int/en/web/patents/protection
- WIPO — Patent FAQs: https://www.wipo.int/en/web/patents/faq_patents
- WIPO — Technology Transfer FAQs: https://www.wipo.int/en/web/technology-transfer/faq
- EPO — 2026 Guidelines, mathematical methods: https://www.epo.org/en/legal/guidelines-epc/2026/g_ii_3_3.html
- EPO — 2026 Guidelines, simulation/design/modelling: https://www.epo.org/en/legal/guidelines-epc/2026/g_ii_3_3_2.html

**Decision recorded for this repository:** keep the repository private. Do not treat the current patent specification or proprietary notice as evidence of a filed patent or completed chain of title.
