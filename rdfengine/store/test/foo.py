from types import MappingProxyType
from collections import ChainMap
from collections.abc import Mapping


class FrozenDict(ChainMap):
    def project(self, vars):
        return FrozenDict(
            (x for x in self.items() if x[0] in vars))

    def disjointDomain(self, other):
        return not bool(set(self).intersection(other))

    def compatible(self, other):
        for k in self:
            try:
                if self[k] != other[k]:
                    return False
            except KeyError:
                pass

        return True

    def merge(self, other):
        res = FrozenDict(
            itertools.chain(self.items(), other.items()))

        return res


foo = { 'a': 1, 'b': 2 }

fooro = FrozenDict(foo)

print (fooro['a'])

fooro['c'] = 3