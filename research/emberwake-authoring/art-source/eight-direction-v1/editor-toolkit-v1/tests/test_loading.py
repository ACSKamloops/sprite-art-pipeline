import copy,json,unittest
from sprite_lab import *
from test_core import fixture,tx

class PortableJsonTests(unittest.TestCase):
    def test_integral_decimal_project_and_transaction_exact(self):
        p=fixture();text=json.dumps(p).replace('"width": 4','"width": 4.0').replace('"height": 3','"height": 3e0');q=load_project(text)
        self.assertEqual(q,p);self.assertEqual(project_hash(q),project_hash(p));self.assertIs(type(q['canvas']['width']),int);self.assertEqual(q['animations'][0]['fps'],p['animations'][0]['fps']);self.assertIs(type(q['animations'][0]['fps']),float)
        t=tx(p,{'op':'paint','cel_id':'b','points':[[2,1,2]]});decoded=load_json(json.dumps(t).replace('[2, 1, 2]','[2.0, 1e0, 2.000]'))
        self.assertEqual(apply_transaction(p,t),apply_transaction(q,decoded))
    def test_nonfinite_unsafe_and_fractional_indices_reject(self):
        for text in ['9007199254740992','NaN','Infinity','1e999']:
            with self.subTest(text=text),self.assertRaises(ValueError):load_json(text)
        p=fixture();p['cels']['a']['pixels'][1]=1.5
        with self.assertRaises(EditError):load_project(json.dumps(p))
        p['cels']['a']['pixels'][1]=9007199254740992.0
        with self.assertRaises(EditError):load_project(json.dumps(p))
