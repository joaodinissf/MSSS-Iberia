class Skill:
  def __init__(self, _id = -1, exp = 0, mot = 0):#, mem = 0):
    self._id = _id
    self.expertise = exp
    self.motivation = mot

    # !TODO
    # self.memory = mem
  def __str__(self):
    return '< id: ' + str(self._id) + \
           ', expertise: ' + str(self.expertise) + \
           ', motivation: ' + str(self.motivation) + ' >'