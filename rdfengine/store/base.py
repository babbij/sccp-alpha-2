import logging

from rdflib.store import Store
from six import iteritems



__all__ = ['BaseStore']


ANY = Any = None


"""
Derived from IOMemory store built-in to rdflib, this is the preliminary stab at a remote
fetch implementation of the RDF store. 
"""
class BaseStore(Store):
  context_aware = True
  graph_aware = True
  formula_aware = True

  def __init__(self, configuration = None, identifier = None):
    super(BaseStore, self).__init__()

    self.__length = 0
    self.__namespace = {}
    self.__prefix = {}

    # Indexes for each triple part, and a list of contexts for each triple

    self.__subjectIndex = {}                # key: subject    val: set(triples)
    self.__predicateIndex = {}              # key: predicate  val: set(triples)
    self.__objectIndex = {}                 # key: object     val: set(triples)
    self.__tripleContexts = {}              # key: triple     val: {context1: quoted, context2: quoted ...}
    self.__contextTriples = {None: set()}   # key: context    val: set(triples)

    self.__all_contexts = set()             # all contexts used in store (unencoded)
    self.__defaultContexts = None           # default context information for triples

  def __len__(self, context = None):
    # this is a very rough and silly way to do this.
    return self.__length

  def bind(self, prefix, namespace):
    self.__prefix[namespace] = prefix
    self.__namespace[prefix] = namespace

  def namespace(self, prefix):
    return self.__namespace.get(prefix, None)

  def prefix(self, namespace):
    return self.__prefix.get(namespace, None)

  def namespaces(self):
    for prefix, namespace in iteritems(self.__namespace):
      yield prefix, namespace

  def add(self, triple, context, quoted = False):
    # logging.debug(f'BaseStore add {triple}')
    
    self.__length += 1
    
    Store.add(self, triple, context, quoted)

    if context is not None:
        self.__all_contexts.add(context)

    sub, pre, obj = triple
    
    self.__addTripleContext(triple, context, quoted)

    if sub in self.__subjectIndex:
      self.__subjectIndex[sub].add(triple)
    else:
      self.__subjectIndex[sub] = set([triple])

    if pre in self.__predicateIndex:
      self.__predicateIndex[pre].add(triple)
    else:
      self.__predicateIndex[pre] = set([triple])

    if obj in self.__objectIndex:
      self.__objectIndex[obj].add(triple)
    else:
      self.__objectIndex[obj] = set([triple])

  def remove(self, triplepat, context = None):
    logging.debug(f'BaseStore remove {triplepat} {context}')
    
    Store.remove(self, triplepat, context)
    
    for triple, contexts in self.localtriples(triplepat, context):
      for ctx in self.__getTripleContexts(triple):
        if context is not None and context != ctx:
          continue

        self.__removeTripleContext(triple, ctx)

      ctxs = self.__getTripleContexts(triple, skipQuoted=True)

      if None in ctxs and (context is None or len(ctxs) == 1):
        self.__removeTripleContext(triple, None)

      if len(self.__getTripleContexts(triple)) == 0:
        # triple has been removed from all contexts
        sub, pre, obj = triple
        self.__subjectIndex[sub].remove(triple)
        self.__predicateIndex[pre].remove(triple)
        self.__objectIndex[obj].remove(triple)

        del self.__tripleContexts[triple]

      if not context is None and context in self.__contextTriples and len(self.__contextTriples[context]) == 0:
        # all triples are removed out of this context
        # and it's not the default context so delete it
        del self.__contextTriples[context]

      if triplepat == (None, None, None) and context in self.__all_contexts and not self.graph_aware:
        # remove the whole context
        self.__all_contexts.remove(context)

  # separate these methods so we can safely override triples without causing infinite recursions
  def triples(self, triplein, context = None):
    return self.localtriples(triplein, context)

  def localtriples(self, triplein, context = None):
    # logging.debug(f'BaseStore triples {triplein}')
    
    if context is not None:
      if context == self:  # hmm...does this really ever happen?
        context = None

    sub, pre, obj = triplein

    # all triples case (no triple parts given as pattern)
    if sub is None and pre is None and obj is None:
      return self.__all_triples(context)

    # optimize "triple in graph" case (all parts given)
    if sub is not None and pre is not None and obj is not None:
      if sub in self.__subjectIndex and triplein in self.__subjectIndex[sub] and self.__tripleHasContext(triplein, context):
        return ((triplein, self.__contexts(triplein)) for i in [0])
      else:
        return self.__emptygen()

    # remaining cases: one or two out of three given
    sets = []
    if sub is not None:
      if sub in self.__subjectIndex:
        sets.append(self.__subjectIndex[sub])
      else:
        return self.__emptygen()

    if pre is not None:
      if pre in self.__predicateIndex:
        sets.append(self.__predicateIndex[pre])
      else:
        return self.__emptygen()

    if obj is not None:
      if obj in self.__objectIndex:
        sets.append(self.__objectIndex[obj])
      else:
        return self.__emptygen()

    # to get the result, do an intersection of the sets (if necessary)
    if len(sets) > 1:
      triples = sets[0].intersection(*sets[1:])
    else:
      triples = sets[0].copy()

    return ((triple, self.__contexts(triple)) for triple in triples if self.__tripleHasContext(triple, context))

  def contexts(self, triple=None):
    if triple is None or triple is (None,None,None):
      return (context for context in self.__all_contexts)

    sub, pre, obj = triple
    if sub in self.__subjectIndex and triple in self.__subjectIndex[sub]:
      return self.__contexts(triple)
    else:
      return self.__emptygen()

  def add_graph(self, graph):
    if not self.graph_aware:
      Store.add_graph(self, graph)
    else:
      self.__all_contexts.add(graph)

  def remove_graph(self, graph):
    if not self.graph_aware:
      Store.remove_graph(self, graph)
    else:
      self.remove((None,None,None), graph)
      try:
        self.__all_contexts.remove(graph)
      except KeyError:
        pass # we didn't know this graph, no problem

  # internal utility methods below

  def __addTripleContext(self, triple, context, quoted):
    """add the given context to the set of contexts for the triple"""

    sub, pre, obj = triple
    if sub in self.__subjectIndex and triple in self.__subjectIndex[sub]:
      # we know the triple exists somewhere in the store
      if triple not in self.__tripleContexts:
        # triple exists with default ctx info
        # start with a copy of the default ctx info
        self.__tripleContexts[triple] = self.__defaultContexts.copy()

      self.__tripleContexts[triple][context] = quoted
      if not quoted:
        self.__tripleContexts[triple][None] = quoted

    else:
      # the triple didn't exist before in the store
      if quoted:  # this context only
          self.__tripleContexts[triple] = {context: quoted}
      else:  # default context as well
          self.__tripleContexts[triple] = {context: quoted, None: quoted}

    # if the triple is not quoted add it to the default context
    if not quoted:
      self.__contextTriples[None].add(triple)

    # always add the triple to given context, making sure it's initialized
    if context not in self.__contextTriples:
      self.__contextTriples[context] = set()
    self.__contextTriples[context].add(triple)

    # if this is the first ever triple in the store, set default ctx info
    if self.__defaultContexts is None:
      self.__defaultContexts = self.__tripleContexts[triple]

    # if the context info is the same as default, no need to store it
    if self.__tripleContexts[triple] == self.__defaultContexts:
      del self.__tripleContexts[triple]

  def __getTripleContexts(self, triple, skipQuoted=False):
    """return a list of (encoded) contexts for the triple, skipping
       quoted contexts if skipQuoted==True"""

    ctxs = self.__tripleContexts.get(triple, self.__defaultContexts)

    if not skipQuoted:
      return ctxs.keys()

    return [context for context, quoted in ctxs.items() if not quoted]

  def __tripleHasContext(self, triple, context):
    """return True iff the triple exists in the given context"""
    ctxs = self.__tripleContexts.get(triple, self.__defaultContexts)
    return (context in ctxs)

  def __removeTripleContext(self, triple, context):
    """remove the context from the triple"""
    ctxs = self.__tripleContexts.get(triple, self.__defaultContexts).copy()
    del ctxs[context]
    
    if ctxs == self.__defaultContexts:
        del self.__tripleContexts[triple]
    else:
        self.__tripleContexts[triple] = ctxs

    self.__contextTriples[context].remove(triple)

  def __all_triples(self, context):
    """return a generator which yields all the triples (unencoded)
       of the given context"""
    if context not in self.__contextTriples:
        return

    for triple in self.__contextTriples[context].copy():
        yield triple, self.__contexts(triple)

  def __contexts(self, triple):
    """return a generator for all the non-quoted contexts
       (unencoded) the encoded triple appears in"""
    return (context for context in self.__getTripleContexts(triple, skipQuoted=True) if context is not None)

  def __emptygen(self):
    """return an empty generator"""
    if False:
      yield
      
      
      
if __name__ == '__main__':
  from rdflib.term import Literal
  
  store = BaseStore()
  
  triple = (Literal('a'), Literal('b'), Literal('c'))
  triple2 = (Literal('a'), Literal('z'), Literal('c'))
  
  store.add(triple, None, False)
  store.add(triple2, None, False)
  
  print(list(store.triples(triple)))
  print(list(store.triples((None, None, None))))
  print(list(store.triples((Literal('a'), None, None))))
  
  store.remove((None, Literal('b'), None))

  print(list(store.triples(triple)))  
  print(list(store.triples((None, None, None))))
  print(list(store.triples((Literal('a'), None, None))))
  

