"""Every file of every revision of each retired skill (generated).

Written by scripts/gen_shipped_names.py from
tests/fixtures/shipped_names_history.json; regenerate, do not edit.
{skill: {path in the skill directory: sha256 of each revision with LF
line endings, first 16 hex digits}}, read by
``install_paths.legacy_skill_files``.
"""

from typing import Dict, Tuple

RETIRED_SKILL_FILES: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "brainstorming": {
        "SKILL.md": (
            "10271c555d435a7b",
            "51fe3e9a91c4ba0c",
            "6ec8d057d2043cc1",
        ),
    },
    "confidence-check": {
        "SKILL.md": (
            "093e2c6cba32d69e",
            "2066f9274d2bdf59",
            "219e6a0312444ad6",
            "3092c4f57bf9cc3c",
            "3868d6e216f813f5",
            "41337bf901a80b5a",
            "45925a2f4e9674df",
            "5077c299b15dc3bd",
            "51fdef103b4b5615",
            "53d821472b37e9d4",
            "633bdf03f2baa723",
            "64d151ed5758f017",
            "6cf848c110dcc5de",
            "6de5472d76632183",
            "6f1805320580cb8f",
            "6f9774694ca8835e",
            "74aa7d4821df6409",
            "758f5a51d1a5f887",
            "7b4bebd7802bb937",
            "87f5dcd0938730b4",
            "8d801d7bd789043d",
            "98fdabacbe2b1f46",
            "9bdf5abe3e40cf40",
            "9d4ea93588c8744a",
            "a84a8d29a4c351bc",
            "b7f79438885e7c57",
            "bf94b98d64f55f2b",
            "c425e17264998059",
            "c8836d38511bf20e",
            "d2ab3593cec50d92",
            "d998d72952ba1c40",
            "ddbee1d49c796559",
            "ec37cb90a65e0d35",
            "f0c20427c562d6b1",
        ),
        "__init__.py": ("e3b0c44298fc1c14",),
        "canary.yaml": ("07d8a56816ff3d14",),
        "confidence.ts": (
            "5e0202a4a51c44ed",
            "787fa5433cb844b2",
            "9d736858e423158e",
            "a0b60e99ab360f6d",
            "c1517ef5dab45c0f",
        ),
        "references/checks-detail.md": ("3f8879e021dfd891",),
        "scripts/validate_confidence_context.py": (
            "31629b48ced8325a",
            "7f2be31bf48d5ba2",
        ),
    },
    "dispatching-parallel-agents": {
        "SKILL.md": (
            "5202a10d7bf01a27",
            "885fec2019497e8f",
            "fa96fe849432c2f7",
        ),
    },
    "executing-plans": {
        "SKILL.md": (
            "7784bb2723ad9759",
            "b2456676e60c750b",
            "f8e715bec50a1224",
        ),
    },
    "finishing-a-development-branch": {
        "SKILL.md": (
            "173a141f20c02783",
            "1df4d47dc8607e16",
            "44b390fc668c130c",
            "4cd166b198942479",
            "4da78fbc6c104bb4",
            "5b4b05b15a53a8dc",
            "85b9cb0dac3b3238",
            "aa3c3335d28eb498",
            "aa4665b180099ec4",
            "affa2bcac4938e4e",
            "b4a4e310571f74bc",
            "d138a935e9b790d3",
            "e6ce95f72ec51328",
            "f2ba69c806f2b268",
            "f3ff99e7e6428df3",
            "f769e61958babb60",
        ),
    },
    "receiving-code-review": {
        "SKILL.md": (
            "01aeebd6d8d07c30",
            "6a2e90c6598701db",
            "f266ad098558da84",
        ),
    },
    "requesting-code-review": {
        "SKILL.md": (
            "13b0cd6e4ec39d9f",
            "e63ca1f14ff16f31",
            "f6f3b5b56b4d46bd",
        ),
    },
    "ship": {
        "SKILL.md": (
            "212af326e94dfff6",
            "3caa0bfd7389ee92",
            "47daeca418555ef9",
            "5a5b8547706b1fca",
            "656f4fa3c7eddb8f",
            "6dd964673c6fcea6",
            "6e2904b8a9db7ed6",
            "759133dbc162a83d",
            "a776e69b214cf814",
            "aab1c90e60d285bd",
            "b57a96f73e1b12b2",
            "ef01fd68320fa318",
            "effc1fcd33a55d7e",
            "f250bc99bced709c",
        ),
        "references/conventions.md": (
            "525038a038edeccd",
            "5b7220530f1f68cd",
            "c67af1816dcf2dee",
        ),
    },
    "simplicity-coach": {
        "SKILL.md": (
            "06970b665c30fd19",
            "173f40fe58e80ec8",
            "1e09fd4fa61005b6",
            "314816b5bd012a62",
            "316c38c88e4d8a1c",
            "32abc06a93563b9b",
            "36930e07fe01d06d",
            "61c970e49651b13f",
            "66440ccb4790d748",
            "668e03b4936311b2",
            "71d33bf2705bf6b6",
            "72d3a708eda46f4a",
            "922a7eb18901e37a",
            "99d88c90ab676682",
            "9a6c5c58f098c199",
            "a4bbdc495ff60137",
            "b8dba1aa7c811808",
            "c5c7815b44e95400",
            "d0f14dd05b062ab4",
            "dbb5f2f3b8ebc4d4",
            "f2fb762d0c48e579",
            "f8f05e0fd2fcf1be",
            "f93e363586264f3c",
            "fa90ce9d14658226",
            "fc23f01090d092da",
        ),
        "assets/dependency-audit-checklist.md": (
            "0ae4309796b011fc",
            "c4c6010f118910be",
            "c7de661310377ea5",
            "eab907e49a212763",
        ),
        "assets/example_asset.txt": (
            "30db099ca9940002",
            "f019b05e3425cf41",
        ),
        "references/api_reference.md": (
            "2e4e4148bc6094d3",
            "5a094ba4a533769b",
        ),
        "references/orient-step-learn-examples.md": (
            "0b88eae9b8203258",
            "9ca7e9d54a182856",
            "a646843bcba2e0f2",
            "b9ca15456241fe27",
        ),
        "references/practices-reference.md": (
            "14e4df704ad91a82",
            "5e08242067540203",
            "7aea602810adf41c",
        ),
        "scripts/dependency-audit.py": (
            "23642e013834ff17",
            "581d720e8fb1d230",
            "c2101dd50db95269",
            "e13713311c345890",
        ),
        "scripts/example.py": (
            "c2101dd50db95269",
            "df734ca44c2277bf",
        ),
    },
    "systematic-debugging": {
        "SKILL.md": (
            "2d64bfcd9722c5bd",
            "4f8a6935ab718be5",
            "808f10944972e555",
        ),
    },
    "test-driven-development": {
        "SKILL.md": (
            "00b8e1038b8f3632",
            "2c6a4f2ecd844437",
            "3d19797a2d43b1b0",
        ),
    },
    "using-git-worktrees": {
        "SKILL.md": (
            "14b7a72c1a1d9e53",
            "49ab5ba6add4038b",
            "b52de69df7b96e67",
        ),
    },
    "using-superclaude": {
        "SKILL.md": (
            "60f2391008995b87",
            "907aa83297e622a8",
            "a2833a5ea4cbed45",
            "cae1bcd2dc926a8f",
        ),
    },
    "verbalized-sampling": {
        "SKILL.md": (
            "2c21ce95bfe3620d",
            "2f192421b8da9e42",
            "44fdaf9a497fc4b0",
            "6509d07a8430c964",
            "6732ba6645494d3b",
            "7017e4cacc349337",
            "a04ce3628dee4250",
            "bcdaa496c26ccb19",
            "c34e36fb5f12ac7d",
            "c5d3a7014d7413c8",
            "e3bffb0ea8da083b",
            "eeb3e30bc51ad9e4",
        ),
        "canary.yaml": ("b48022c56de5ffe3",),
        "references/examples.md": (
            "312a8de663b37e7a",
            "31523f1862bbc169",
            "603d7b30e67d57ed",
            "b18c0a559abe4e0b",
            "c9e60328af18a6cb",
        ),
        "references/paper-methodology.md": (
            "1061e09d0978b687",
            "857e1d33263fa21b",
        ),
        "references/theory.md": (
            "4502263e6f1af28a",
            "499f7f1197b56056",
        ),
    },
    "verification-before-completion": {
        "SKILL.md": (
            "1eadb466bc837878",
            "c1fb276d216b35d0",
            "f05e8dcc020a36cd",
        ),
    },
    "writing-plans": {
        "SKILL.md": (
            "40b4ead954e03b2c",
            "6bc43e1d273d0b8a",
            "bd92e4f7cf565177",
        ),
    },
}
