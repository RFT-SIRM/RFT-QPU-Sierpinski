# Public branch map

**Audit date:** 12 November 2026  
**Comparison base:** `main` at `617bddf107a07e4301851f8c9fb14846523562d9`  
**Canonical branch:** `main`

## Canonical source

Use `main` as the current public project baseline. The other branch names listed below are retained work branches and historical snapshots; they are not automatically part of the canonical release. The branch comparison is a point-in-time comparison against the audit base above.

GitHub branch metadata reported `main` as **not protected** at the time of this audit. That means the repository does not currently enforce a branch-protection rule on `main` through the setting reported by GitHub. For a more controlled public collaboration process, configure a rule requiring pull requests, passing status checks, no force pushes and no branch deletion.

## Other public branches

| Branch | Commits ahead of main | Main commits missing from branch | Interpretation |
|---|---:|---:|---|
| `docs/evgeny-zaprudnov-documentation-review-2026-11-11` | 1 | 4 | Earlier documentation snapshot; main contains later licensing/public-release updates |
| `docs/qpu-architecture-site-2026-11-11` | 2 | 8 | Earlier HTML/site development branch; main contains later presentation and status corrections |
| `docs/strategic-pre-release-polish-2026-11-11` | 0 | 4 | Fully behind main at audit time; no branch-only commits |
| `engineering/complex-z-parametric-plan-2026-11-11` | 4 | 7 | Active-looking technical work branch with additional complex-Z/circuit-model commits not merged into main |
| `engineering/physical-prototype-v0.1-2026-11-10` | 2 | 9 | Older v0.1 engineering snapshot |
| `engineering/pre-release-v0.4-rc1-2026-11-11` | 1 | 6 | Earlier v0.4-rc1 pre-release snapshot |
| `engineering/stage11b-requantized-gate-2026-11-11` | 2 | 5 | Earlier Stage 11B development branch; main carries the reviewed Stage 11B baseline |

The ahead/behind counts come from GitHub's compare endpoint. “Ahead” means commits reachable from that branch but not from `main`; it does not by itself prove that every change is useful, safe or ready to merge.

## How to contribute

- Start from a fresh checkout of `main`.
- Create a focused branch for a specific change.
- Submit a pull request against `main`.
- Wait for the repository test and numerical-reproduction workflow.
- Keep all numerical claims tied to tracked artifacts, commands and model assumptions.

Do not merge the complex-Z branch or any other historical branch solely because it is ahead. Review its diff, reproduce its calculations, and check the physical assumptions first. Do not delete historical branches merely to make the branch list look tidy; deleting a ref does not erase public commits or copies already made.
