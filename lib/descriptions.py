import json
class CommandDescriptions:
 def get(name: str):
  with open('extensions/data/full_descriptions.json', "r") as jsondata:
    desc = json.load(jsondata)
  try:
   return desc[name]
  except:
   raise KeyError('The full description of this command cannot be found.')
