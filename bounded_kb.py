# the logical model of the system
from z3 import *

# Some Constants
SIZE = ["large", "small"]
COLOR = ["gray", "red", "blue", "green", "brown", "purple", "cyan", "yellow"]
SHAPE = ["cube", "sphere", "cylinder"]
MATERIAL = ["rubber", "metal"]

def translate_answer(fun, z3_var):
  ftype = fun['function']
  print fun, z3_var
  if ftype in ["exist", "greater_than", 'less_than', 'equal_size',
               'equal_color', 'equal_shape', 'equal_material',
               'equal_integer']:
    return 'yes' if z3_var.__bool__() else 'no'
  if ftype in ["count"]:
    return str(z3_var.as_long())
  if 'query' in ftype:
    attr_idx = z3_var.as_long()
    if 'size' in ftype: return SIZE[attr_idx]
    if 'color' in ftype: return COLOR[attr_idx]
    if 'shape' in ftype: return SHAPE[attr_idx]
    if 'material' in ftype: return MATERIAL[attr_idx]


  print ftype
  assert 0, 'urod blyat unimplemented'

# Parses a scene object and store the relevant facts
# Given a solver instance, it can add the relevant facts as constraints
class SceneParser
  def __init__(self):
    self.objs = []
    self.size, self.color, self.shape, self.material =\
    dict(), dict(), dict(), dict()
    self.x, self.y = dict(), dict()
    self.x_rels = []
    self.y_rels = []

# a bounded (by size) Knowledge Base store
# also has the ability to infer a scene by guessing a minimum number of objects and insisting a set of facts
class BoundedKB:

  def __init__(self):
    print "i am live !"
    

# ================================= tests ================================ #
def test1():
  kb = BoundedKB()
  pstate = kb.fresh_python_state()
  print pstate

if __name__ == "__main__":
  print "hello!"
  test1()
  #test2()
  #test3()
