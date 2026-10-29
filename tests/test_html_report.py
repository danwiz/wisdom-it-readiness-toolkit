import copy
from dataclasses import replace
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from html_report import generate_html_report
from scorer import load_json, score_assessment

ROOT = Path(__file__).resolve().parents[1]

class Parsed(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags=[]; self.text=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def handle_data(self, data):
        self.text.append(data)

class HtmlReportTests(unittest.TestCase):
    def setUp(self):
        self.assessment = load_json(ROOT/'assessments/quick-check-v0.1.json')
        self.responses = load_json(ROOT/'examples/synthetic-responses.json')
    def test_semantics_and_no_active_or_external_content(self):
        result=score_assessment(self.assessment,self.responses)
        parsed=Parsed(generate_html_report(self.assessment,result))
        tags=[tag for tag, _ in parsed.tags]
        self.assertEqual(tags.count('h1'),1)
        self.assertEqual(tags.count('main'),1)
        self.assertIn(('html',{'lang':'en'}),parsed.tags)
        self.assertIn('caption',tags)
        self.assertTrue(all(attrs.get('scope') in ('col','row') for tag,attrs in parsed.tags if tag=='th'))
        self.assertFalse(set(tags)&{'script','iframe','form','input','img','link','object','embed','svg'})
        self.assertFalse(any(k in ('href','src','action') or k.startswith('on') for _,attrs in parsed.tags for k in attrs))
        headings=[int(tag[1:]) for tag in tags if tag in ('h1','h2','h3')]
        self.assertTrue(all(b<=a+1 for a,b in zip(headings,headings[1:])))
    def test_untrusted_text_is_literal(self):
        attack='<script>alert(1)</script><img src="https://invalid.test" onerror="alert(1)">&'
        self.assessment['title']=attack
        self.assessment['domains'][0]['title']=attack
        result=score_assessment(self.assessment,self.responses)
        result.recommendations[0]['rationale']=attack
        result.recommendations[0]['next_action']=attack
        result=replace(result, maturity_label=attack)
        text=generate_html_report(self.assessment,result,subject=attack,data_note=attack)
        parsed=Parsed(text)
        self.assertNotIn('<script>',text)
        self.assertNotIn('img',[t for t,_ in parsed.tags])
        self.assertIn(attack,''.join(parsed.text))
    def test_partial_unavailable_and_recommendation_parity(self):
        result=score_assessment(self.assessment,{'STR-01':2})
        text=generate_html_report(self.assessment,result,data_note='Synthetic partial fixture')
        plain=' '.join(Parsed(text).text)
        self.assertIn('Answered 1 of 9',plain)
        self.assertIn('provisional',plain)
        self.assertIn('Unavailable (no answered questions)',plain)
        for item in result.recommendations:
            for key in ('rationale','next_action','rule_id'):
                self.assertIn(item[key],plain)
        self.assertIn('not security assurance or certification',plain)
    def test_determinism_and_no_mutation(self):
        before=copy.deepcopy(self.assessment)
        result=score_assessment(self.assessment,self.responses)
        saved=copy.deepcopy(result)
        text=generate_html_report(self.assessment,result)
        self.assertEqual(text,generate_html_report(self.assessment,result))
        self.assertEqual(before,self.assessment)
        self.assertEqual(saved,result)

if __name__=='__main__':
    unittest.main()
