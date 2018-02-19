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
    self.clear_state()

  def clear_state(self):
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
    # clear internal states when parsing a scene for supervised learning
    self.clear_state()
    for idx, obj in enumerate(scene['objects']):
      self.add_obj()
      print obj
      self.add_attr(idx, 'size', obj['size'])
      self.add_attr(idx, 'color', obj['color'])
      self.add_attr(idx, 'shape', obj['shape'])
      self.add_attr(idx, 'material', obj['material'])
    # objects to the left of idx1
    for idx1, left in enumerate(scene['relationships']['left']):
      for idx2 in left:
        self.add_rel('x', idx2, idx1)
    # objects to the front of idx1
    for idx1, front in enumerate(scene['relationships']['front']):
      for idx2 in front:
        self.add_rel('y', idx2, idx1)

  # express the query as constraints. evaluate the query.
  # assume the z3 formula has been already constructed via dump_z3
  def query(self, query_program):
    for qq in query_program:
      print qq
    partial_evals = [None for _ in range(len(query_program))]
    for idx, fun in enumerate(query_program):
      ftype = fun['function']

      # the scene function returns a bit-mask of all objects constrained on their existence
      # aka the solver s_obj already created by dump_z3
      if ftype == 'scene':
        partial_evals[idx] = self.s_obj
        continue

      # the filtering functions additionally create bit-mask of the output of filtering 
      if 'filter' in ftype:
        # get the input objects to the filter function
        input_value = partial_evals[fun['inputs'][0]]
        # create variables for the next function call
        nxt_objs = [Bool('filter_{}_{}'.format(idx, i)) for i in range(N_OBJ)]
        partial_evals[idx] = nxt_objs
        # add constraints depends on the filtered type and filterd values
        if 'size' in ftype:
          size_value = SIZE.index(fun['value_inputs'][0])
          for ii in range(N_OBJ):
            self.s.add(nxt_objs[ii] == And(input_value[ii], self.s_size(ii) == size_value))
          continue
        if 'color' in ftype:
          color_value = COLOR.index(fun['value_inputs'][0])
          for ii in range(N_OBJ):
            self.s.add(nxt_objs[ii] == And(input_value[ii], self.s_color(ii) == color_value))
          continue
        if 'shape' in ftype:
          shape_value = SHAPE.index(fun['value_inputs'][0])
          for ii in range(N_OBJ):
            self.s.add(nxt_objs[ii] == And(input_value[ii], self.s_shape(ii) == shape_value))
          continue
        if 'material' in ftype:
          material_value = MATERIAL.index(fun['value_inputs'][0])
          for ii in range(N_OBJ):
            self.s.add(nxt_objs[ii] == And(input_value[ii], self.s_material(ii) == material_value))
          continue

      # count the number of existing objects in the input bitmask by adding
      if ftype == 'count':
        # get the input objects to the filter function
        input_value = partial_evals[fun['inputs'][0]]
        # add a integer z3 value to keep track of how many
        cnt = Int('cnt_{}'.format(idx))
        partial_evals[idx] = cnt 
        # constrain it to the size
        one_counts = [Int('one_count_{}_{}'.format(idx, ii)) for ii in range(N_OBJ)]
        for ii in range(N_OBJ):
          self.s.add(one_counts[ii] == If(input_value[ii], 1, 0))
        self.s.add(cnt == sum(one_counts))
        continue

      # take 2 z3 integer values and compare if it is greater
      if ftype == 'greater_than':
        input_value1 = partial_evals[fun['inputs'][0]]
        input_value2 = partial_evals[fun['inputs'][1]]
        # add a bool z3 value to keep track of if greater
        gt = Int('gt_{}'.format(idx))
        partial_evals[idx] = gt
        self.s.add(gt == input_value1 > input_value2)
        continue
      
      # takes in a list of objects and return the only one that exists as a Int index
      if ftype == 'unique':
        input_value = partial_evals[fun['inputs'][0]]
        # add a integer z3 value to keep track of the index
        unique = Int('unique_{}'.format(idx))
        partial_evals[idx] = unique 
        # add the constraint for the index of it
        self.s.add(Or(*input_value))
        for ii in range(N_OBJ):
          self.s.add(Implies(input_value[ii], unique == ii))
        continue

      # return a bitmask of objects with same attr as the index object (except not the index)
      if 'same' in ftype:
        input_value = partial_evals[fun['inputs'][0]]
        existence = self.s_obj
        # create variables for the next function call
        same_objs = [Bool('same_{}_{}'.format(idx, i)) for i in range(N_OBJ)]
        partial_evals[idx] = same_objs
        # add constraints depends on the filtered type and filterd values
        # to be added, it needs to first exist, and same attribute, and not the same id as index
        if 'size' in ftype:
          size_value = self.s_size(input_value)
          for ii in range(N_OBJ):
            self.s.add(same_objs[ii] == And(existence[ii],
                                            self.s_size(ii) == size_value,
                                            input_value != ii))
          continue
        if 'color' in ftype:
          color_value = self.s_color(input_value)
          for ii in range(N_OBJ):
            self.s.add(same_objs[ii] == And(existence[ii],
                                            self.s_color(ii) == color_value,
                                            input_value != ii))
          continue
        if 'shape' in ftype:
          shape_value = self.s_shape(input_value)
          for ii in range(N_OBJ):
            self.s.add(same_objs[ii] == And(existence[ii],
                                            self.s_shape(ii) == shape_value,
                                            input_value != ii))
          continue
        if 'material' in ftype:
          material_value = self.s_material(input_value)
          for ii in range(N_OBJ):
            self.s.add(same_objs[ii] == And(existence[ii],
                                            self.s_material(ii) == material_value,
                                            input_value != ii))
          continue

      if 'query' in ftype:
        input_value = partial_evals[fun['inputs'][0]]
        # add a integer z3 value to keep track of the queried attribute
        query_attr = Int('query_{}'.format(idx))
        partial_evals[idx] = query_attr 
        # grab the appropriate attributes
        if 'size' in ftype: self.s.add(query_attr == self.s_size(input_value))
        if 'color' in ftype: self.s.add(query_attr == self.s_color(input_value))
        if 'shape' in ftype: self.s.add(query_attr == self.s_shape(input_value))
        if 'material' in ftype: self.s.add(query_attr == self.s_material(input_value))
        continue

      if 'equal' in ftype:
        input_value1 = partial_evals[fun['inputs'][0]]
        input_value2 = partial_evals[fun['inputs'][1]]
        # add a bool z3 value to keep track of if greater
        eq = Bool('eq_{}'.format(idx))
        partial_evals[idx] = eq
        self.s.add(eq == (input_value1 == input_value2))
        continue

      if ftype == 'relate':
        input_value = partial_evals[fun['inputs'][0]]
        existence = self.s_obj
        # create variables for the next function call
        rel_objs = [Bool('rel_{}_{}'.format(idx, i)) for i in range(N_OBJ)]
        partial_evals[idx] = rel_objs
        if fun['value_inputs'][0] == 'left':
          for ii in range(N_OBJ):
            self.s.add(rel_objs[ii] == And(existence[ii], self.s_x(ii) < self.s_x(input_value)))
          continue
        if fun['value_inputs'][0] == 'right':
          for ii in range(N_OBJ):
            self.s.add(rel_objs[ii] == And(existence[ii], self.s_x(ii) > self.s_x(input_value)))
          continue
        if fun['value_inputs'][0] == 'in front':
          for ii in range(N_OBJ):
            self.s.add(rel_objs[ii] == And(existence[ii], self.s_y(ii) < self.s_y(input_value)))
          continue
        if fun['value_inputs'][0] == 'behind':
          for ii in range(N_OBJ):
            self.s.add(rel_objs[ii] == And(existence[ii], self.s_y(ii) > self.s_y(input_value)))
          continue

      if ftype == 'intersect':
        input_value1 = partial_evals[fun['inputs'][0]]
        input_value2 = partial_evals[fun['inputs'][1]]
        # create variables for the next function call
        int_objs = [Bool('int_{}_{}'.format(idx, i)) for i in range(N_OBJ)]
        partial_evals[idx] = int_objs
        for ii in range(N_OBJ):
          self.s.add(int_objs[ii] == And(input_value1[ii], input_value2[ii]))
        continue
        
      print ftype
      print fun
      assert 0, "[UROD BLLYAT] not implemented for this ftype "
    for pe in partial_evals:
      print pe
      print
    result = partial_evals[-1]
    self.s.check()
    model = self.s.model()
    for x in partial_evals[12]:
      print "i am exist ", x, model[x]
    print model[partial_evals[4]]
    print self.x_rels
    return self.s.model()[result]

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
  for scene in scenes['scenes']:
    # scene = scenes['scenes'][2]
    l_scene.parse_scene(scene)
    print l_scene.dump_z3()

def test3():
  l_scene = LogicalScene()
  scenes_loc = './CLEVR_v1.0/scenes/scenes_1000.json'
  questions_loc = './CLEVR_v1.0/questions/questions_1000.json'
  import json
  scenes = json.load(open(scenes_loc))
  questions = json.load(open(questions_loc))

  scene = scenes['scenes'][0]
  question = questions['questions'][3]

  print scene['image_filename'], question['image_filename']
  assert scene['image_filename'] == question['image_filename'], "not same file Kappa"

  print question['question']

  l_scene.parse_scene(scene)
  l_scene.dump_z3()
  qry_ans = l_scene.query(question['program'])

  print qry_ans
  print question['answer']



if __name__ == "__main__":
  print "hello!"
  # test1()
  #test2()
  test3()
