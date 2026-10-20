"""Canonical UTF-8 JSON: sorted UTF-16 keys and ECMAScript numeric spelling."""
import hashlib,json,math
from decimal import Decimal

def canonical_json(value):
    def encode(v):
        if v is None:return 'null'
        if isinstance(v,bool):return 'true' if v else 'false'
        if isinstance(v,str):
            v.encode('utf-8') # reject unpaired surrogates
            return json.dumps(v,ensure_ascii=False,separators=(',',':'))
        if isinstance(v,(int,float)):
            if not math.isfinite(v):raise ValueError('Nonfinite JSON number')
            if isinstance(v,int):
                if abs(v)>9007199254740991:raise ValueError('JSON integer exceeds exact JavaScript range')
                return str(v)
            if v==0:return '0'
            s=repr(v).lower();a=abs(v)
            if 1e-6<=a<1e21:
                s=format(Decimal(s),'f')
                if '.' in s:s=s.rstrip('0').rstrip('.')
                return s
            if 'e' not in s:s=format(v,'.15e')
            mantissa,exponent=s.split('e');mantissa=mantissa.rstrip('0').rstrip('.') if '.'in mantissa else mantissa
            n=int(exponent);return mantissa+'e'+('+' if n>=0 else '-')+str(abs(n))
        if isinstance(v,list):return '['+','.join(encode(x)for x in v)+']'
        if isinstance(v,dict):
            if not all(isinstance(k,str)for k in v):raise ValueError('JSON keys must be strings')
            return '{'+','.join(encode(k)+':'+encode(v[k])for k in sorted(v,key=lambda s:s.encode('utf-16-be')))+'}'
        raise ValueError('Not a JSON value')
    return encode(value)
def content_hash(value):return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()
