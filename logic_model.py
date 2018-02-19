# the logical model of the system
from z3 import *

# Some Constants
SIZE = ["large", "small"]
COLOR = ["gray", "red", "blue", "green", "brown", "purple", "cyan", "yellow"]
SHAPE = ["cube", "sphere", "cylinder"]
MATERIAL = ["rubber", "metal"]
X = list(range(20))
Y = list(range(20))
N_OBJ = 20

class LogicalScene:

  def __init__(self):
    print "initializing logical scene"
    self.objs = []
    self.size, self.color, self.shape, self.material =\
    dict(), dict(), dict(), dict()
    self.x, self.y = dict(), dict()
    self.x_rels = []
    self.y_rels = []

  def add_obj(self):
    self.objs.append(len(self.objs))

  def add_attr(self, obj_id, attr_type, attr):
    if attr_type == "size": self.size[obj_id] = attr
    if attr_type == "color": self.color[obj_id] = attr
    if attr_type == "shape": self.shape[obj_id] = attr
    if attr_type == "material": self.material[obj_id] = attr
    if attr_type == "x": self.x[obj_id] = attr
    if attr_type == "y": self.y[obj_id] = attr

  def add_rel(self, rel_type, obj_id1, obj_id2):
    if rel_type == "x": self.x_rels.append( (obj_id1, obj_id2) )
    if rel_type == "y": self.y_rels.append( (obj_id1, obj_id2) )

  def parse_scene(self, scene):
    print scene.keys()
    for idx, obj in enumerate(scene['objects']):
      self.add_obj()
      print obj
      self.add_attr(idx, 'size', obj['size'])
      self.add_attr(idx, 'color', obj['color'])
      self.add_attr(idx, 'shape', obj['shape'])
      self.add_attr(idx, 'material', obj['material'])
    for idx1, left in enumerate(scene['relationships']['left']):
      for idx2 in left:
        self.add_rel('x', idx1, idx2)
    for idx1, front in enumerate(scene['relationships']['front']):
      for idx2 in front:
        self.add_rel('y', idx1, idx2)

  def dump_z3(self):
    # make solver and relations
    self.s = Solver()
    self.s_size, self.s_color, self.s_shape, self.s_material =\
      Function('size', IntSort(), IntSort()),\
      Function('color', IntSort(), IntSort()),\
      Function('shape', IntSort(), IntSort()),\
      Function('material', IntSort(), IntSort())
    self.s_x, self.s_y =\
      Function('x', IntSort(), IntSort()),\
      Function('y', IntSort(), IntSort())

    # a list of bit of existence of objects
    self.s_obj = [Bool('obj_{}'.format(i)) for i in range(N_OBJ)]
    for obj_idx in range(N_OBJ):
      if obj_idx in self.objs:
        self.s.add(self.s_obj[obj_idx] == True)
      else:
        self.s.add(self.s_obj[obj_idx] == False)

    # add attribute facts
    for obj in self.size:
      self.s.add(self.s_size(obj) == SIZE.index(self.size[obj]))
    for obj in self.color:
      self.s.add(self.s_color(obj) == COLOR.index(self.color[obj]))
    for obj in self.shape:
      self.s.add(self.s_shape(obj) == SHAPE.index(self.shape[obj]))
    for obj in self.material:
      self.s.add(self.s_material(obj) == MATERIAL.index(self.material[obj]))
    for obj in self.x:
      self.s.add(self.s_x(obj) == self.x[obj])
    for obj in self.y:
      self.s.add(self.s_y(obj) == self.y[obj])

    # add relational facts
    for x_rel in self.x_rels:
      obj1, obj2 = x_rel
      self.s.add(self.s_x(obj1) < self.s_x(obj2))
    for y_rel in self.y_rels:
      obj1, obj2 = y_rel
      self.s.add(self.s_y(obj1) < self.s_y(obj2))

    self.s.check()
    return self.s.model()
    
# ================================= Some Test Code ================================= #
def test1():
  l_scene = LogicalScene()
  # add objects
  l_scene.add_obj()
  l_scene.add_attr(0, "size", "large")
  l_scene.add_attr(0, "color", "gray")
  l_scene.add_attr(0, "shape", "cylinder")
  l_scene.add_attr(0, "material", "metal")
  l_scene.add_attr(0, "x", 5)
  l_scene.add_attr(0, "y", 15)
  l_scene.add_obj()
  l_scene.add_attr(1, "size", "large")
  l_scene.add_attr(1, "color", "brown")
  l_scene.add_attr(1, "shape", "cube")
  l_scene.add_attr(1, "material", "rubber")
  l_scene.add_attr(1, "x", 12)
  l_scene.add_attr(1, "y", 15)
  l_scene.add_obj()
  l_scene.add_attr(2, "size", "small")
  l_scene.add_attr(2, "color", "brown")
  l_scene.add_attr(2, "shape", "cube")
  l_scene.add_attr(2, "material", "rubber")
  l_scene.add_attr(2, "x", 10)
  l_scene.add_attr(2, "y", 3)

  # add spacial relations
  #                       
  #    0           1      
  #                       
  #                       
  #         2             
  #                       
  l_scene.add_rel("x", 0, 1)
  l_scene.add_rel("x", 0, 2)
  l_scene.add_rel("y", 2, 0)
  l_scene.add_rel("y", 2, 1)

  print l_scene.dump_z3()

def test2():
  l_scene = LogicalScene()
  scenes_loc = './CLEVR_v1.0/scenes/scenes_1000.json'
  import json
  scenes = json.load(open(scenes_loc))
  print "scenes loaded ", len(scenes['scenes'])
  scene0 = scenes['scenes'][0]
  l_scene.parse_scene(scene0)
  print l_scene.dump_z3()

if __name__ == "__main__":
  print "hello!"
  # test1()
  test2()
