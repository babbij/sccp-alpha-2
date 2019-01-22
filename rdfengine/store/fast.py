import logging

from rdflib.store import Store
from collections import defaultdict

from weakref import WeakSet, WeakKeyDictionary, WeakValueDictionary


__all__ = ['FastStore']


def _emptygen():
  return
  yield


def _make_matches(sub, pre, obj):
  # for patterns with 'None' in certain positions these will duplicate
  # but they're being added to a set, which will sort it out to just unique patterns
  return {
    # pick 0 from 3
    (None, None, None),

    # pick 1 from 3  
    (sub, None, None),
    (None, pre, None),
    (None, None, obj),

    # pick 2 from 3
    (sub, pre, None),
    (None, pre, obj),
    (sub, None, obj),

    # pick 3 from 3
    (sub, pre, obj),
  }


# wrapper for context to allow safe use in weak dicts/sets
class Context: 
  def __init__(self, context):
    self.__context = context
    self.__statements = WeakSet()

  def __hash__(self):
    return hash(self.__context)

  def __eq__(self, other):
    try:
      return str(other) == self.__context
    except AttributeError:
      return False

  def __str__(self):
    return str(self.__context)

  def __repr__(self):
    return f'Context({self.__context})'
    
  def __len__(self):
    return len(self.__statements)
    
  def unwrap(self):
    return self.__context
    
  def add_statement(self, stmt):
    self.__statements.add(stmt)
    
  def remove_statement(self, stmt):
    self.__statements.discard(stmt)
    
  def statements(self):
    return self.__statements


# a Statement is mapped by a Triple and has some contexts
class Statement:
  def __init__(self, initial_context = None, quoted = False):
    self.quoted = quoted
    self.__contexts = set()
    
    if initial_context is not None:
      self.add_context(initial_context)

  def __repr__(self):
    return f'Statement({self.__contexts})'
  
  def contexts(self):
    return map(lambda c: c.unwrap(), self.__contexts)
  
  def add_context(self, context):
    context.add_statement(self)
    self.__contexts.add(context)
  
  # returns
  # True if statement should be retained
  # False if statement should be discarded
  def remove_context(self, context):
    if context is None:
      self.__contexts.clear() # remove self from 
      return False
    else:
      self.__contexts.discard(context)
      context.remove_statement(self)

      return (len(self.__contexts) > 0)# or (not self.quoted)



class FastStore(Store):
  context_aware = True
  graph_aware = True
  formula_aware = True
  
  def __init__(self, configuration = None, identifier = None):
    super(FastStore, self).__init__()

    self.__namespace = {}
    self.__prefix = {}
    
    # a map of complete fully specified Triples to Statements
    self.__statements = {}
    
    # a precomputed map of possible Patterns to the Triple objects they match
    # this is a WeakDictionary so that when a triple is removed from __triples 
    # they will be deleted here too. 
    self.__matches = defaultdict(WeakValueDictionary)

    # since self.__matches for (None, None, None) is just all triples
    # be clever and just override this as an optimisation
    self.__matches[(None, None, None)] = self.__statements

    # dict of all contexts, data to obj. Weak?
    self.__contexts = {}

  def __context_of(self, context):
    if context is not None:
      ctx = self.__contexts.get(context, None)
      if ctx is None:
        ctx = Context(context)
        self.__contexts[context] = ctx

      return ctx
    else:
      return None

  def __len__(self, context = None):
    if context is None:
      return len(self.__statements)
    elif context in self.__contexts:
      return len(self.__contexts[context])
    else:
      return 0

  def bind(self, prefix, namespace):
    self.__prefix[namespace] = prefix
    self.__namespace[prefix] = namespace

  def namespace(self, prefix):
    return self.__namespace.get(prefix, None)

  def prefix(self, namespace):
    return self.__prefix.get(namespace, None)

  def namespaces(self):
    for prefix, namespace in self.__namespace.items():
      yield prefix, namespace

  def add(self, triple, context, quoted = False):
    stmt = self.__statements.get(triple, None)
    if stmt:
      if context:
        stmt.add_context(self.__context_of(context))
        
      # if the stmt was quoted and is now not quoted, unquote
      if not quoted:
        stmt.quoted = False

    else:
      stmt = Statement(self.__context_of(context), quoted)
      # generate additional mappings
      # since this includes (None, None, None) don't need to add separately to self.__statements
      for match in _make_matches(*triple):
        self.__matches[match][triple] = stmt

  def remove(self, triplepat, context = None):
    for triple, triple_context in self.triples(triplepat, context):
      stmt = self.__statements[triple]
      if not stmt.remove_context(self.__context_of(context)):
        # remove from the (None, None, None) list and the WeakRefs take care of the rest
        del self.__statements[triple]

  # separate these methods so we can safely override triples without causing infinite recursions
  def triples(self, triplein, context = None):
    return [
      (
        triple, stmt.contexts()
      )
      for triple, stmt 
      in self.__matches.get(triplein, {}).items()
    ]

  def contexts(self, triple = None):
    if triple is None or triple is (None, None, None):
      return self.__contexts.keys()
    
    if triple in self.__statements:
      return self.__statements[triple].contexts()
    
    return _emptygen()
    
  def statements(self):
    return self.__statements

  def add_graph(self, graph):
    raise NotImplementedError()

  def remove_graph(self, graph):
    raise NotImplementedError()


class Foo:
  def __init__(self, val):
    self.val = val


if __name__ == '__main__':
  from rdflib.term import Literal
  store = FastStore()