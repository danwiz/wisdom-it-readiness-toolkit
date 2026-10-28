"""Exercise an installed CLI in a temporary directory without source imports."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

executable = str(Path(sys.argv[1]).resolve())
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    response = root/'responses.json'
    response.write_text('{"STR-01":2}', encoding='utf-8')
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    def run(*args):
        return subprocess.run([executable,*args],cwd=root,env=env,capture_output=True,text=True,timeout=30)
    result = run('score','builtin:quick-check',str(response))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['overall_percent'] == 100
    output = root/'report.md'
    result = run('report','builtin:quick-check',str(response),'--output',str(output))
    assert result.returncode == 0 and 'Overall score' in output.read_text(), result.stderr
    original = output.read_bytes()
    for payload in ['{', '[]','{"STR-01":true}','{"STR-01":3}', '{"private-value-marker":1}', '{"STR-01":0,"STR-01":2}']:
        response.write_text(payload,encoding='utf-8')
        result = run('report','builtin:quick-check',str(response),'--output',str(output))
        assert result.returncode == 2, result.stderr
        assert not result.stdout and 'Traceback' not in result.stderr and 'private-value-marker' not in result.stderr
        assert output.read_bytes() == original
        assert response.read_text() == payload
    response.write_bytes(b'\xff')
    assert run('score','builtin:quick-check',str(response)).returncode == 2
    response.write_text('{"STR-01":2}',encoding='utf-8')
    result = run('report','builtin:quick-check',str(response),'--output',str(response))
    assert result.returncode == 2 and response.read_text() == '{"STR-01":2}'
    result = run('score','missing-assessment.json',str(response))
    assert result.returncode == 1 and not result.stdout and 'Traceback' not in result.stderr
    # Existing directory is not a report file, including under privileged test users.
    result = run('report','builtin:quick-check',str(response),'--output',str(root))
    assert result.returncode == 1 and not result.stdout and 'Traceback' not in result.stderr
print('Installed CLI success/error and preservation checks passed outside checkout.')
