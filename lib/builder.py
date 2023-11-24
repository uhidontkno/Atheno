import discord
class ErrorTypes:
    GENERIC = 0
    USER_NO_PERMS = 1
    BOT_NO_PERMS = 2
    COOLDOWN = 3
    INVALID_PARAMS = 4
    lang = ["Error","Insufficient Permission(s)","Insufficient Permission(s)","You are on cooldown!","Not enough parameters given."]
    desc = ["```{{0}}```","You do not have the {{0}} permission(s) to use this command", "The bot does not have the {{0}} permission(s) in order to run this command.","You are on cooldown for: {{0}}","Please make sure all parameters are valid before using this command: {{0}}"]
class MessageTypes:
    GENERIC = 0
    SUCCESS = 1
    WARNING = 2
    INFO = 3
    HELP = 4
    color = [discord.Color.blurple(),discord.Color.green(),discord.Color.yellow(),discord.Color.blue(),discord.Color.dark_blue()]
    title = [None,"Success","Warning","Information","Help"]
class MessageBuilder:
    def error(self,type = 1,vars=[]):
        return discord.Embed(color=discord.Color.red(),
                             title=ErrorTypes.lang[type],
                             description=self.template(vars,type)
                             )
    def message(self,type = MessageTypes.GENERIC):
        return discord.Embed(
            color=MessageTypes.color[type],
            title=MessageTypes.title[type]
            )
    def template(vars,type):
        msg = ErrorTypes.desc[type]
        start = 0
        end = 0
        try: start = msg.index('{{') 
        except: pass
        try: end = msg.index('}}') 
        except: pass
        msg = msg.replace(msg[start:end],vars[0])
        msg = msg.replace("}}",'')
        return msg
