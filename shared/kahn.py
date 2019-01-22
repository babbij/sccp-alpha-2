import logging

from collections import deque
from random import shuffle


# duck type this if you want something sortable by kahnsort
class SortableNode:
  def __init__(self, me, predecessors):
    self.me = me
    self.predecessors = predecessors
  
  def get_id(self):
    return self.me
  
  def get_predecessors(self):
    return self.predecessors
    
  def __repr__(self):
    return f'SortableNode({self.me}, {self.predecessors})'

 

def kahnsort(graph, tolerate_incomplete_date = True, log = False):
  # determine in-degree 
  in_degree = { u : 0 for u in graph }

  total = len(graph)
  progress = 0
  
  # of each node
  for u in graph:
    if log:
      logging.debug(f'Kahnsort analysing {progress/total * 100:.2f}')
    progress += 1
    
    for v in u.get_predecessors():
      found = False
      for s in in_degree:
        if s.get_id() == v:
          found = True
          in_degree[s] += 1
      
      if not found and not tolerate_incomplete_date:
        raise Exception(f'Node {v} not found')

  # collect nodes with zero in-degree
  Q = deque()
  for u in in_degree:
    if in_degree[u] == 0:
      Q.appendleft(u)
 
  # list for order of nodes
  L = []
     
  while Q:
    if log:
      logging.debug(f'Kahnsort {len(Q)} remaining')
      
    # choose node of zero in-degree
    u = Q.pop()
    
    # and 'remove' it from graph
    L.insert(0, u)
    for v in u.get_predecessors():
      for s in in_degree:
        if s.get_id() == v:
          in_degree[s] -= 1
          if in_degree[s] == 0:
            Q.appendleft(s)
 
  if len(L) != len(graph):
    raise Exception('Could not sort, likely graph cycle')
  
  return L  


if __name__ == '__main__': 
  # exercise various sortings
  
  graph1 = [
    SortableNode('a', []),
    SortableNode('b', ['a']),
    SortableNode('c', ['b', 'a']),
    SortableNode('d', ['a']),
    SortableNode('e', ['d']),
    SortableNode('f', ['e', 'c'])
  ]
  
  shuffle(graph1)
  
  print ('\n'.join([repr(s) for s in kahnsort(graph1)]))
  print ('-----')

  # cope with missing information (may be the case with claims)
  graph2 = [
    SortableNode('a', ['x']),
    SortableNode('b', ['a']),
    SortableNode('c', ['b', 'a']),
    SortableNode('d', ['a']),
    SortableNode('e', ['d', 'q']),
    SortableNode('f', ['e', 'c']),
  ]

  shuffle(graph2)
  
  print ('\n'.join([repr(s) for s in kahnsort(graph2)]))
  print ('-----')
  
  # two separate graphs
  graph3 = [
    SortableNode('a', []),
    SortableNode('b', ['a']),
    SortableNode('c', ['b', 'a']),
    SortableNode('w', []),
    SortableNode('x', []),
    SortableNode('y', []),
    SortableNode('z', ['w', 'x', 'y'])
  ]

  print ('\n'.join([repr(s) for s in kahnsort(graph3)]))
  print ('-----')

  # jbo claims
  graph4 = [
    SortableNode('a', []),
    SortableNode('b', []),
    SortableNode('c', []),
  ]

  print ('\n'.join([repr(s) for s in kahnsort(graph4)]))
  print ('-----')
