import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from scorer import score_assessment, parse_json
ROOT = Path(__file__).resolve().parents[1]

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.assessment = json.loads((ROOT/'assessments/quick-check-v0.1.json').read_text())
        self.responses = json.loads((ROOT/'examples/synthetic-responses.json').read_text())

    def test_legacy_golden_result(self):
        r = score_assessment(self.assessment, self.responses)
        self.assertEqual({k: v for k, v in r.__dict__.items() if k not in ("coverage", "recommendations")}, dict(overall_percent=47.37, maturity_level=3,
            maturity_label='Repeatable', domain_scores=dict(strategy=83.33,infrastructure=75.0,security=31.25,operations=25.0), unanswered_questions=[]))
        r = score_assessment(self.assessment, {'STR-01': 2})
        self.assertEqual(r.overall_percent, 100)
        self.assertEqual(r.domain_scores, {'strategy': 100})
        self.assertEqual(len(r.unanswered_questions), 8)

    def test_invalid_assessments_even_when_question_unanswered(self):
        def q(a): return a['domains'][0]['questions'][0]
        mutations = [
            lambda a: a.pop('version'), lambda a: a.update(version='9.0.0'),
            lambda a: a.update(version=[]), lambda a: a.update(domains=[None]),
            lambda a: a['domains'].append(copy.deepcopy(a['domains'][0])),
            lambda a: a['domains'][0]['questions'].append(copy.deepcopy(q(a))),
            lambda a: a['domains'][0].update(id=[]),
            lambda a: q(a).update(id=' '), lambda a: q(a).update(weight=True),
            lambda a: q(a).update(weight=float('nan')), lambda a: q(a).update(weight=float('inf')),
            lambda a: q(a).update(weight=0), lambda a: q(a).update(weight=10**400),
            lambda a: a.update(scale={'0':'No','2':'Yes'}),
            lambda a: a.update(scale={'00':'No','1':'Yes'}),
            lambda a: a['maturity_bands'][0].update(maximum_percent=24),
            lambda a: a['maturity_bands'][1].update(minimum_percent=24.99),
            lambda a: a['maturity_bands'][0].update(level=True),
            lambda a: a['maturity_bands'][1].update(level=1),
            lambda a: a['maturity_bands'][0].update(label=''),
            lambda a: a['maturity_bands'][-1].update(maximum_percent=99.99),
            lambda a: a['maturity_bands'][0].update(maximum_percent=24.999),
        ]
        for mutate in mutations:
            a = copy.deepcopy(self.assessment); mutate(a)
            with self.subTest(mutation=mutations.index(mutate)), self.assertRaises(ValueError):
                score_assessment(a, {'SEC-01': 1})

    def test_invalid_responses(self):
        for response in [[], None, {}, {'unknown': 1}, {'STR-01': True}, {'STR-01': 1.5}, {'STR-01': 3}]:
            with self.subTest(response=response), self.assertRaises(ValueError):
                score_assessment(self.assessment, response)

    def test_json_rejects_duplicates_constants_and_nonobjects(self):
        for text in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '[]', '{', '{"nested":{"x":1,"x":2}}']:
            with self.subTest(text=text), self.assertRaises(ValueError): parse_json(text)

    def test_band_boundaries(self):
        a = copy.deepcopy(self.assessment)
        a['domains'] = [{'id':'d','questions':[{'id':'yes','weight':1},{'id':'no','weight':1}]}]
        for percent, level in [(0,1),(24.99,1),(25,2),(44.99,2),(45,3),(64.99,3),(65,4),(84.99,4),(85,5),(100,5)]:
            with self.subTest(percent=percent):
                if percent in (0,100):
                    response={'yes': 0 if percent==0 else 2}
                else:
                    a['domains'][0]['questions'][0]['weight']=percent
                    a['domains'][0]['questions'][1]['weight']=100-percent
                    response={'yes':2,'no':0}
                self.assertEqual(score_assessment(a,response).maturity_level,level)
