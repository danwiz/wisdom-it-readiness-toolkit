"""Standalone, deterministic HTML; no scripts, remote resources or active user markup."""
from html import escape
from typing import Any
from scorer import ScoreResult


def generate_html_report(assessment: dict[str, Any], result: ScoreResult, *,
                         subject: str = 'Assessment subject',
                         data_note: str = 'User-provided assessment responses') -> str:
    def e(value: Any) -> str:
        return escape(str(value), quote=True)
    title = e(assessment.get('title', 'Technology Readiness Assessment'))
    titles = {str(d['id']): str(d.get('title', d['id'])) for d in assessment.get('domains', [])}
    lines = ['<!doctype html>', '<html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">',
             f'<title>{title} — Readiness report</title>',
             '<style>body{font-family:system-ui,sans-serif;color:#172536;background:#fff;line-height:1.6;margin:0}main{max-width:70rem;margin:auto;padding:2rem}h1{line-height:1.2}h2{border-bottom:2px solid #526579;padding-bottom:.3rem}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;border:1px solid #526579;padding:.65rem;overflow-wrap:anywhere}caption{text-align:left;font-weight:600}li{margin-bottom:1rem}p,dd{overflow-wrap:anywhere}.notice{background:#eef3f7;padding:1rem;border-left:4px solid #284e70}dt{font-weight:700}dd{margin:0 0 .6rem}@media(max-width:40rem){main{padding:1rem}th,td{padding:.35rem}}@media print{main{max-width:none;padding:0}h2,h3{break-after:avoid}li,tr{break-inside:avoid}}</style>',
             '</head><body><main>', f'<h1>{title} — Report</h1>',
             '<dl>', f'<dt>Subject</dt><dd>{e(subject)}</dd>',
             f'<dt>Assessment</dt><dd>{e(assessment.get("assessment_id", "unknown"))} v{e(assessment.get("version", "unknown"))}</dd>',
             f'<dt>Data</dt><dd>{e(data_note)}</dd>',
             f'<dt>Overall score</dt><dd>{result.overall_percent:.2f}%</dd>',
             f'<dt>Maturity</dt><dd>Level {e(result.maturity_level)} — {e(result.maturity_label)}</dd></dl>',
             '<h2>Coverage</h2>']
    if result.coverage:
        lines.append(f'<p>Answered {e(result.coverage["answered"])} of {e(result.coverage["total"])} questions.</p>')
    else:
        lines.append('<p>Coverage unavailable for this result.</p>')
    lines.append('<p class="notice">' + ('Incomplete assessment: scores describe answered questions only and are provisional.' if result.coverage.get('incomplete', True) else 'All questions answered; responses have not been independently verified.') + '</p>')
    lines += ['<h2>Domain results</h2>', '<table><caption>Scores and response coverage by domain</caption><thead><tr><th scope="col">Domain</th><th scope="col">Score</th><th scope="col">Answered / total</th></tr></thead><tbody>']
    domains = sorted(set(result.domain_scores) | set(result.coverage.get('domains', {})))
    for domain in domains:
        score = f'{result.domain_scores[domain]:.2f}%' if domain in result.domain_scores else 'Unavailable (no answered questions)'
        coverage = result.coverage.get('domains', {}).get(domain)
        count = f'{coverage["answered"]} / {coverage["total"]}' if coverage else 'Unavailable'
        lines.append(f'<tr><th scope="row">{e(titles.get(domain, domain))}</th><td>{e(score)}</td><td>{e(count)}</td></tr>')
    lines += ['</tbody></table>', '<h2>Priority actions</h2>']
    if result.recommendations:
        lines.append('<ol>')
        for item in result.recommendations:
            lines += [f'<li><h3>{e(item["priority"].upper())} — {e(titles.get(item["domain_id"], item["domain_id"]))}</h3>',
                      f'<p>Rule: <code>{e(item["rule_id"])}</code></p>',
                      f'<p><strong>Rationale:</strong> {e(item["rationale"])}</p>',
                      f'<p><strong>Next action:</strong> {e(item["next_action"])}</p></li>']
        lines.append('</ol>')
    else:
        lines.append('<p>Recommendations unavailable for this result.</p>')
    lines += ['<h2>Limitations</h2>', '<p>Priorities are workflow priorities, not vulnerability severity. Scores describe supplied responses, not security assurance or certification. Review evidence with an accountable owner before acting.</p>',
              '<h2>Evidence required for closure</h2><ul><li>Named owner and target date for each remediation action</li><li>Configuration, policy, checklist, or system evidence</li><li>Verification record showing the control operates as intended</li><li>Updated risk and action registers</li></ul>']
    if result.unanswered_questions:
        lines.append('<h2>Incomplete responses</h2><ul>')
        lines.extend(f'<li>{e(q)}</li>' for q in result.unanswered_questions)
        lines.append('</ul>')
    lines += ['</main></body></html>']
    return '\n'.join(lines) + '\n'
