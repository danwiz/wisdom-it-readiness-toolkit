import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from scorer import score_assessment
from report import generate_markdown_report
ROOT = Path(__file__).resolve().parents[1]

class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.a=json.loads((ROOT/'assessments/quick-check-v0.1.json').read_text())
        self.responses=json.loads((ROOT/'examples/synthetic-responses.json').read_text())

    def test_thresholds(self):
        self.a['domains']=[{'id':'d','questions':[{'id':'yes','weight':1},{'id':'no','weight':1}]}]
        cases=[(44.99,'high','establish-baseline'),(45,'medium','standardize-practices'),
               (64.99,'medium','standardize-practices'),(65,'low','verify-consistency'),
               (84.99,'low','verify-consistency'),(85,'low','maintain-evidence')]
        for pct,priority,rule in cases:
            with self.subTest(percent=pct):
                self.a['domains'][0]['questions'][0]['weight']=pct
                self.a['domains'][0]['questions'][1]['weight']=100-pct
                r=score_assessment(self.a,{'yes':2,'no':0})
                self.assertEqual(r.overall_percent,pct)
                self.assertEqual(len(r.recommendations),1)
                rec=r.recommendations[0]
                self.assertEqual((rec['priority'],rec['rule_id']),(priority,rule))
                self.assertIn(f'{pct:.2f}%',rec['rationale'])
                self.assertIn(r.maturity_label,rec['rationale'])

    def test_missing_domain_is_unavailable_and_high_priority(self):
        r=score_assessment(self.a,{'STR-01':2})
        self.assertEqual(r.coverage['answered'],1)
        self.assertEqual(r.coverage['total'],9)
        self.assertTrue(r.coverage['incomplete'])
        self.assertEqual(r.coverage['domains']['security'],{'answered':0,'total':3,'incomplete':True})
        security=[x for x in r.recommendations if x['domain_id']=='security']
        self.assertEqual(len(security),1)
        self.assertEqual(security[0]['rule_id'],'complete-evidence')
        self.assertEqual(security[0]['priority'],'high')
        self.assertIn('unavailable',security[0]['rationale'])
        report=generate_markdown_report(self.a,r)
        self.assertIn('Answered 1 of 9',report)
        self.assertIn('provisional',report)
        self.assertIn('unavailable (no answered questions)',report)

    def test_partial_domain_keeps_both_rules(self):
        r=score_assessment(self.a,{'STR-01':0})
        rules=[x['rule_id'] for x in r.recommendations if x['domain_id']=='strategy']
        self.assertEqual(rules,['complete-evidence','establish-baseline'])

    def test_tie_order_and_repeated_outputs(self):
        r=score_assessment(self.a,self.responses)
        self.assertFalse(r.coverage['incomplete'])
        self.assertEqual([(x['priority'],x['domain_id']) for x in r.recommendations],
                         [('high','operations'),('high','security'),('low','infrastructure'),('low','strategy')])
        original=copy.deepcopy(self.a)
        original_responses=copy.deepcopy(self.responses)
        for _ in range(3):
            other=score_assessment(self.a,dict(reversed(list(self.responses.items()))))
            self.assertEqual(json.dumps(r.__dict__,sort_keys=True),json.dumps(other.__dict__,sort_keys=True))
            self.assertEqual(generate_markdown_report(self.a,r),generate_markdown_report(self.a,other))
        self.assertEqual(self.a,original)
        self.assertEqual(self.responses,original_responses)
        reordered=copy.deepcopy(self.a);reordered['domains'].reverse()
        self.assertEqual(score_assessment(reordered,self.responses).recommendations,r.recommendations)

    def test_json_and_markdown_have_same_rules(self):
        r=score_assessment(self.a,self.responses)
        report=generate_markdown_report(self.a,r)
        for item in r.recommendations:
            self.assertIn(item['rule_id'],report)
            self.assertIn(item['next_action'],report)
        self.assertIn('not vulnerability severity',report)

    def test_invalid_or_empty_inputs_cannot_emit_guidance(self):
        for responses in [{},{'unknown':1},{'STR-01':True}]:
            with self.assertRaises(ValueError): score_assessment(self.a,responses)

    def test_untrusted_markdown_text_is_literal(self):
        self.a['title']='<script>alert(1)</script>\n# injected'
        r=score_assessment(self.a,self.responses)
        text=generate_markdown_report(self.a,r,subject='[link](https://example.invalid)',data_note='*bold*')
        self.assertNotIn('<script>',text)
        self.assertNotIn('\n# injected',text)
        self.assertIn('\\[link\\]',text)
        self.assertIn('\\*bold\\*',text)
