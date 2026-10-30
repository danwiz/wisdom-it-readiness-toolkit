"""JSON export carries explicit, unverified provenance without changing scores."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class JsonCliTests(unittest.TestCase):
    def run_score(self, fixture, *options):
        return subprocess.run(
            [sys.executable, str(ROOT/'src/cli.py'), 'score',
             str(ROOT/'assessments/quick-check-v0.1.json'),
             str(ROOT/'examples'/fixture), *options],
            capture_output=True, text=True, check=True)

    def test_complete_default_is_unverified_and_preserves_scores(self):
        result = json.loads(self.run_score('synthetic-responses.json').stdout)
        self.assertEqual(result['metadata'], {
            'assessment_id': 'WITRT-QUICK-001', 'assessment_version': '0.1.0',
            'subject': 'Assessment subject',
            'data_note': 'User-provided assessment responses',
            'provenance_basis': 'caller-supplied; not independently verified'})
        self.assertEqual(result['overall_percent'], 47.37)
        self.assertEqual(result['maturity_level'], 3)
        self.assertEqual(result['maturity_label'], 'Repeatable')
        self.assertEqual(result['domain_scores'], {
            'strategy': 83.33, 'infrastructure': 75.0,
            'security': 31.25, 'operations': 25.0})
        self.assertEqual(result['unanswered_questions'], [])
        self.assertIn('All questions answered; responses have not been independently verified.', result['limitations'])
        self.assertIn('Scores describe supplied responses, not security assurance or certification.', result['limitations'])
        self.assertIn('Priorities are workflow priorities, not vulnerability severity.', result['limitations'])

    def test_partial_explicit_provenance_is_literal_and_deterministic(self):
        options = ('--subject', '<script>probe</script> "subject"',
                   '--data-note', 'Synthetic demonstration only\nNot client data')
        first = self.run_score('partial-synthetic-responses.json', *options)
        self.assertEqual(first.stdout, self.run_score('partial-synthetic-responses.json', *options).stdout)
        result = json.loads(first.stdout)
        self.assertEqual(result['metadata']['subject'], options[1])
        self.assertEqual(result['metadata']['data_note'], options[3])
        self.assertTrue(result['coverage']['incomplete'])
        self.assertIn('Incomplete assessment: scores describe answered questions only and are provisional.', result['limitations'])
        self.assertNotIn('timestamp', result['metadata'])

    def test_committed_example_matches_explicit_cli_output(self):
        result = self.run_score('synthetic-responses.json', '--subject',
                                'Synthetic Demonstration', '--data-note',
                                'Synthetic demonstration only')
        self.assertEqual(json.loads(result.stdout), json.loads(
            (ROOT/'examples/recommendations-synthetic.json').read_text()))
