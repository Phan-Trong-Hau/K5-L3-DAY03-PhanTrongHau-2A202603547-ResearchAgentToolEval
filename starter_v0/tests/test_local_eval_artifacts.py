"""Controls for the local prompt-only/schema-only optimization experiment."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_local_rounds_change_only_the_declared_artifact():
    versions = ROOT / 'artifacts'
    v3 = versions / 'versions/v3'
    v4 = versions / 'local_versions/v4-local'
    v5 = versions / 'local_versions/v5-local'
    assert (v4 / 'tools.yaml').read_bytes() == (v3 / 'tools.yaml').read_bytes()
    assert (v4 / 'system_prompt.md').read_bytes() != (v3 / 'system_prompt.md').read_bytes()
    assert (v5 / 'system_prompt.md').read_bytes() == (v4 / 'system_prompt.md').read_bytes()
    assert (v5 / 'tools.yaml').read_bytes() != (v4 / 'tools.yaml').read_bytes()


def test_local_schema_preserves_tools_and_parameter_types():
    versions = ROOT / 'artifacts/local_versions'
    before = yaml.safe_load((versions / 'v4-local/tools.yaml').read_text())['tools']
    after = yaml.safe_load((versions / 'v5-local/tools.yaml').read_text())['tools']
    assert [t['name'] for t in before] == [t['name'] for t in after]
    assert len(after) == 11
    for old, new in zip(before, after):
        old_props, new_props = old['parameters']['properties'], new['parameters']['properties']
        assert old_props.keys() == new_props.keys()
        for name in old_props:
            assert old_props[name]['type'] == new_props[name]['type']
            assert old_props[name].get('enum') == new_props[name].get('enum')
    clarify = next(t for t in after if t['name'] == 'clarify')
    assert 'response_type' in clarify['parameters']['required']
