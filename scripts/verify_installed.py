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
    score = json.loads(result.stdout)
    assert score['overall_percent'] == 100
    assert score['coverage']['answered'] == 1 and score['coverage']['total'] == 9
    assert score['coverage']['incomplete'] is True
    assert any(item['rule_id'] == 'complete-evidence' for item in score['recommendations'])
    assert run('score','builtin:quick-check',str(response)).stdout == result.stdout
    output = root/'report.md'
    result = run('report','builtin:quick-check',str(response),'--output',str(output))
    assert result.returncode == 0 and 'Overall score' in output.read_text(), result.stderr
    original = output.read_bytes()
    assert b'Answered 1 of 9' in original and b'complete-evidence' in original
    assert run('report','builtin:quick-check',str(response),'--output',str(output)).returncode == 0
    assert output.read_bytes() == original
    html_output = root/'report.html'
    result = run('report','builtin:quick-check',str(response),'--format','html','--subject','<script>probe</script>','--output',str(html_output))
    assert result.returncode == 0, result.stderr
    html_original = html_output.read_bytes()
    assert b'<!doctype html>' in html_original and b'Answered 1 of 9' in html_original
    assert b'&lt;script&gt;probe&lt;/script&gt;' in html_original and b'<script>' not in html_original
    assert run('report','builtin:quick-check',str(response),'--format','html','--subject','<script>probe</script>','--output',str(html_output)).returncode == 0
    assert html_output.read_bytes() == html_original
    # Explicit format controls content, regardless of extension; default stays Markdown.
    assert run('report','builtin:quick-check',str(response),'--output',str(root/'default.html')).returncode == 0
    assert (root/'default.html').read_text().startswith('# ')
    assert run('report','builtin:quick-check',str(response),'--format','pdf','--output',str(html_output)).returncode == 2
    assert html_output.read_bytes() == html_original
    for payload in ['{', '[]','{"STR-01":true}','{"STR-01":3}', '{"private-value-marker":1}', '{"STR-01":0,"STR-01":2}']:
        response.write_text(payload,encoding='utf-8')
        result = run('report','builtin:quick-check',str(response),'--output',str(output))
        assert result.returncode == 2, result.stderr
        assert not result.stdout and 'Traceback' not in result.stderr and 'private-value-marker' not in result.stderr
        assert output.read_bytes() == original
        html_result = run('report','builtin:quick-check',str(response),'--format','html','--output',str(html_output))
        assert html_result.returncode == 2 and html_output.read_bytes() == html_original
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
