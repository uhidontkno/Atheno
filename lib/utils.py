import json
class TicketUtils:
 def isticketban(server_id, user_id):
    with open('extensions/data/ticket_banned.json', 'r') as file:
        data = json.load(file)
    if str(server_id) in data['servers']:
        return user_id in data['servers'][str(server_id)]
    return False
class Utils:
 def paramcheck(self,*args):
    for arg in args:
        if arg is None or (isinstance(arg, str) and arg.strip() == ""):
            return False
    return True