class Skill:
  def __init__(self, _id = -1, exp = 0, mot = 0):
    self._id = _id
    self.expertise = [exp]
    self.motivation = [mot]

  def __str__(self):
    return '< skill_id: ' + str(self._id) + \
           ', expertise: ' + str(self.expertise) + \
           ', motivation: ' + str(self.motivation) + ' >'