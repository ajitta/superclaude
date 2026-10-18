from pathlib import Path

import pytest
import yaml

FLAGS = Path(__file__).resolve().parents[1] / "flags"


@pytest.mark.parametrize("path", sorted(FLAGS.glob("*.yaml")), ids=lambda p: p.name)
def test_flag_file_is_valid(path):
    flags = yaml.safe_load(path.read_text(encoding="utf-8"))["flags"]
    for name, flag in flags.items():
        assert isinstance(flag["rollout"], int) and 0 <= flag["rollout"] <= 100, name
        assert isinstance(flag["tags"], list) and flag["tags"], name
        assert isinstance(flag["owner"], str), name
