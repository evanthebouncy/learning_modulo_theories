import random
import copy

# takes in a scene and permute it
def permute_scene(scene):
  print scene
  # make a permutation
  n_objs = len(scene['objects'])
  perm = [_ for _ in range(n_objs)]
  random.shuffle(perm)

  # permute the objects
  scene_copy = copy.deepcopy(scene)
  print scene_copy
  # reorder the objects
  for idx in range(n_objs):
    scene_copy['objects'][perm[idx]] = scene['objects'][idx]

  new_fronts = [None for _ in range(n_objs)]
  new_lefts = [None for _ in range(n_objs)]

  for f_id, front in enumerate(scene['relationships']['front']):
    new_front = [perm[f] for f in front]
    new_fronts[perm[f_id]] = new_front

  for f_id, left in enumerate(scene['relationships']['left']):
    new_left = [perm[f] for f in left]
    new_lefts[perm[f_id]] = new_left

  scene_copy['relationships']['front'] = new_fronts
  scene_copy['relationships']['left'] = new_lefts

  return scene_copy

def subset_objects_scene(scene):
  n_objs = len(scene['objects'])
  sub_n = random.randint(0, n_objs)
  print n_objs, sub_n
  scene_copy = copy.deepcopy(scene)

  # take a subset of objects
  scene_copy['objects'] = scene['objects'][:sub_n]

  new_fronts = [None for _ in range(sub_n)]
  new_lefts = [None for _ in range(sub_n)]

  for f_id, front in enumerate(scene['relationships']['front']):
    new_front = [perm[f] for f in front]
    new_fronts[perm[f_id]] = new_front

  for f_id, left in enumerate(scene['relationships']['left']):
    new_left = [perm[f] for f in left]
    new_lefts[perm[f_id]] = new_left

  scene_copy['relationships']['front'] = new_fronts
  scene_copy['relationships']['left'] = new_lefts

  return scene_copy

# test question answer is invariant under permutation of objects
def test1():
  from logic_model import *
  l_scene = LogicalScene()
  scenes_loc = './CLEVR_v1.0/scenes/scenes_1000.json'
  questions_loc = './CLEVR_v1.0/questions/questions_1000.json'
  import json
  scenes = json.load(open(scenes_loc))
  questions = json.load(open(questions_loc))

  for i in range(100):
    for j in range(10):
      #  for i in [0]:
   # for j in [0]:
      print "running for {} {}".format(i, j)
      scene = scenes['scenes'][i]
      scene = permute_scene(scene)
      question = questions['questions'][i*10+j]

      print scene['image_filename'], question['image_filename']
      assert scene['image_filename'] == question['image_filename'], "not same file Kappa"

      l_scene.parse_scene(scene)
      l_scene.dump_z3()
      qry_ans = l_scene.query(question['program'])
      qry_ans_translated = translate_answer(question['program'][-1], qry_ans) 
      print "ground truth ", question['answer'], "prediction ", qry_ans_translated
      assert question['answer'] == qry_ans_translated, "i, j " + str(i) + " " + str(j)


# test subset of objects are consistent
def test2():
  from logic_model import *
  l_scene = LogicalScene()
  scenes_loc = './CLEVR_v1.0/scenes/scenes_1000.json'
  questions_loc = './CLEVR_v1.0/questions/questions_1000.json'
  import json
  scenes = json.load(open(scenes_loc))
  questions = json.load(open(questions_loc))

  for i in range(100):
    for j in range(10):
      #  for i in [0]:
   # for j in [0]:
      print "running for {} {}".format(i, j)
      scene = scenes['scenes'][i]
      scene = subset_scene(scene)
      assert 0
      question = questions['questions'][i*10+j]

      print scene['image_filename'], question['image_filename']
      assert scene['image_filename'] == question['image_filename'], "not same file Kappa"

      l_scene.parse_scene(scene)
      l_scene.dump_z3()
      qry_ans = l_scene.query(question['program'])
      qry_ans_translated = translate_answer(question['program'][-1], qry_ans) 
      print "ground truth ", question['answer'], "prediction ", qry_ans_translated
      assert question['answer'] == qry_ans_translated, "i, j " + str(i) + " " + str(j)

  print "g r e a t   s u c c e s s"

if __name__ == "__main__":
  test2()
