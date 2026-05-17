# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Note: two `Status:` vocabularies coexist in this repo

This triage vocabulary lives in `.scratch/<feature>/issues/<NN>-*.md` (Matt Pocock skills).

A different `Status:` enum lives in `docs/plans/` and `docs/specs/` files, defined by SC `<doc_output_convention>`: `draft | review | approved-for-plan | implementing | complete | deprecated`.

Both use the literal `Status:` key. They are disjoint by directory — never grep `^Status:` across `.scratch/` and `docs/` together.

