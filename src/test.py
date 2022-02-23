from dataclasses import dataclass
from enum import Enum


class Name(Enum):
    JOHN = 1,
    WILLIAM = 2,
    OLIVER = 3
@dataclass
class Person:
    name: Name
    age: int
    
d = { 'William': Person(Name.WILLIAM, 11), 'yJohn': Person(Name.JOHN, 10), 'Oliver': Person(Name.OLIVER, 9), 'John': Person(Name.JOHN, 41), 'yWilliam': Person(Name.WILLIAM, 2)}
def score(d):
    nd = {}
    for k, v in d:
       nd[k] = nd[k].name.value * 10   
print(d.items())
s = sorted(d, key=lambda k:d[k].name.value)
print(s)