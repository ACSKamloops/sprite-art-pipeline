"""Portable JSON boundary: JavaScript-compatible integral number normalization.
Core objects still require actual ints for integer fields.
"""
import json,math
from .core import require,validate_project

def _integer(text):
    value=int(text);require(abs(value)<=9007199254740991,'Unsafe JSON integer');return value

def _number(text):
    value=float(text);require(math.isfinite(value),'Nonfinite JSON number')
    return int(value)if value.is_integer()and abs(value)<=9007199254740991 else value

def _constant(text):
    raise ValueError('Nonfinite JSON constant '+text)

def load_json(text):
    """Decode JSON, normalizing safe finite integral decimals; keep fractions."""
    return json.loads(text,parse_int=_integer,parse_float=_number,parse_constant=_constant)

def load_project(text):
    project=load_json(text);validate_project(project);return project
