#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json
import re
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "CareBearStare"
Website = "reecon820@gmail.com"
Description = "Target specific shoutouts with a single command"
Creator = "Reecon820"
Version = "1.1.2.1"

#---------------------------
#   Settings Handling
#---------------------------
class CbsSettings:
	def __init__(self, settingsfile=None):
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
				self.__dict__ = json.load(f, encoding="utf-8")
		except:
			self.Command = "!stare"
			self.Cooldown = 10
			self.Permission = "everyone"
			self.Info = ""
			self.ShowAlert = False
			self.aPrefix = "" 
			self.bSuffix = ""
			self.CommandAlts = ""
			self.ShowDecorationAlert = False
			self.Tripwire = False

	def Reload(self, jsondata):
		self.__dict__ = json.loads(jsondata, encoding="utf-8")

	def Save(self, settingsfile):
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
				json.dump(self.__dict__, f, encoding="utf-8")
			with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
				f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
		except:
			Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------
#   Define Global Variables
#---------------------------
global cbsSettingsFile
cbsSettingsFile = ""
global cbsScriptSettings
cbsScriptSettings = CbsSettings()
global cbsStareDict
cbsStareDict = {}

global cbsStarePath
cbsStarePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "stares.conf")).replace("\\", "/")

global cbsAutoShoutouts
cbsAutoShoutouts = set()

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global cbsSettingsFile
    cbsSettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    global cbsScriptSettings
    cbsScriptSettings = CbsSettings(cbsSettingsFile)

    UpatedUi()

    # read client id for api access from file
    try:
        with codecs.open(os.path.join(os.path.dirname(__file__), "clientid.conf"), mode='r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if len(line) > 0:
                    if line[0] != '#':
                        global ClientID
                        ClientID = line
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    LoadConfigFile()

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   only handle messages from chat
    if data.IsChatMessage():
        rawMessage = data.RawData
        isPartner = False

        # get tags
        tags = rawMessage.split(" ")[0]

        if 'partner/1' in tags and cbsScriptSettings.Tripwire and not 'broadcaster/1' in tags:
            if data.UserName not in cbsAutoShoutouts:
                cbsAutoShoutouts.add(data.UserName)
                isPartner = True

        isCommand = data.GetParam(0).lower() == cbsScriptSettings.Command

        if not isCommand:
            alts = cbsScriptSettings.CommandAlts.split(" ")
            for s in alts:
                if s == data.GetParam(0).lower():
                    isCommand = True
                    break
        
        # if this is neither a partner tripwire nor a regular, propper shoutout, no need to keep going
        if not isPartner and not (isCommand and not Parent.IsOnCooldown(ScriptName, cbsScriptSettings.Command) and Parent.HasPermission(data.User, cbsScriptSettings.Permission, cbsScriptSettings.Info)):
            return

        target = ''
        response = ''
        prefix = cbsScriptSettings.aPrefix
        suffix = cbsScriptSettings.bSuffix

        # check if target was given
        if data.GetParam(1):
            target = data.GetParam(1)
            if target[0] == '@':
                target = target[1:]
        
        if isPartner:
            target = data.UserName
        
        if not target:
            return

        # check if target has custom shoutout
        if target.lower() in cbsStareDict:
            response = cbsStareDict[target.lower()]
        else:
            response = cbsStareDict['default']
        
        # replace params in response string
        response = Parse(response, data.UserName, data.UserName, target, target, data.Message)
        prefix = Parse(prefix, data.UserName, data.UserName, target, target, data.Message)
        suffix = Parse(suffix, data.UserName, data.UserName, target, target, data.Message)

        # show alert?
        if cbsScriptSettings.ShowAlert:
            
            # get profile picture link
            headers = {'Client-ID': ClientID, 'Accept': 'application/vnd.twitchtv.v5+json'}
            result = Parent.GetRequest("https://api.twitch.tv/kraken/users?login={0}".format(target.lower()), headers)
            
            jsonResult = json.loads(result)

            if jsonResult['status'] != 200:
                Parent.Log(ScriptName, "lookup user: {0}".format(jsonResult))
                return
            else:
                jsonResult = json.loads(jsonResult['response'])
                if jsonResult['users']:
                    jsonResult = jsonResult['users'][0]

                    emotesets = []

                    if cbsScriptSettings.ShowDecorationAlert:
                        response = "{0} {1} {2}".format(prefix.strip(), response.strip(), suffix.strip())
                    
                        # undocumented api endpoint from https://discuss.dev.twitch.tv/t/whats-the-best-way-to-get-a-streamers-emoteset/11253 
                        productInfo = Parent.GetRequest("https://api.twitch.tv/api/channels/{0}/product".format(Parent.GetChannelName().lower()), headers)
                        jsonEmotes = json.loads(productInfo)

                        if jsonEmotes['status'] != 200:
                            if jsonEmotes['status'] != 404: # surpress errors for non-partnered channels
                                Parent.Log(ScriptName, "Error getting emotesets: {0}".format(jsonEmotes))
                        else:
                            jsonEmotes = json.loads(jsonEmotes['response'])
                            emotes = jsonEmotes['emoticons']
                            setIds = []
                            for emote in emotes:
                                setIds.append(emote['emoticon_set'])
                            emotesets = list(set(setIds)) # remove dupilcates
                    
                    jsonData = '{{"response": "{0}", "logo": "{1}", "emotesets": {2}, "client_id": "{3}" }}'.format(response, jsonResult['logo'], emotesets, ClientID)
                    Parent.BroadcastWsEvent("EVENT_STARE", jsonData)
                else:
                    # don't do a shoutout if the user doesn't exist
                    Parent.Log(ScriptName, "Unknown Twitch Username")
                    return
        
        # if the option is active this is already done
        if not cbsScriptSettings.ShowDecorationAlert:
            response = "{0} {1} {2}".format(prefix.strip(), response.strip(), suffix.strip())
        
        Parent.SendStreamMessage(response)    # Send message to chat
        Parent.AddCooldown(ScriptName, cbsScriptSettings.Command, cbsScriptSettings.Cooldown)  # Put the command on cooldown

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    parseString = parseString.replace('$userid', userid)
    parseString = parseString.replace('$username', username)
    parseString = parseString.replace('$targetid', targetid)
    parseString = parseString.replace('$targetname', targetname)
    parseString = parseString.replace('$url', 'https://www.twitch.tv/{0}'.format(targetname.lower()))
    parseString = parseString.replace('$shorturl', 'twitch.tv/{0}'.format(targetname.lower()))
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    cbsScriptSettings.Reload(jsonData)
    cbsScriptSettings.Save(cbsSettingsFile)
    LoadConfigFile()
    UpatedUi()
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

def EditConfigFile():
    os.startfile(cbsStarePath)
    return

def LoadConfigFile():
    try:
        with codecs.open(cbsStarePath, encoding="utf-8-sig", mode="r") as f:
            matches = {}
            for line in f:
                line = line.strip()
                if len(line) > 0:
                    if line[0] != '#':
                        user = line.split(" ")[0].lower()
                        response = re.search("\".*\"", line).group(0).strip('"')
                        matches[user] = response

            global cbsStareDict
            cbsStareDict = matches
    except Exception as err:
        Parent.Log(ScriptName, "Could not load stares file {0}".format(err))

    return

def CopyPath():
    command = "echo " + os.path.abspath(os.path.join(os.path.dirname(__file__), "StareOverlay.html")) + "| clip"
    os.system(command)
    return

def UpatedUi():
    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # update ui with loaded settings
    ui['Command']['value'] = cbsScriptSettings.Command
    ui['Cooldown']['value'] = cbsScriptSettings.Cooldown
    ui['Permission']['value'] = cbsScriptSettings.Permission
    ui['Info']['value'] = cbsScriptSettings.Info
    ui['ShowAlert']['value'] = cbsScriptSettings.ShowAlert
    ui['aPrefix']['value'] = cbsScriptSettings.aPrefix
    ui['bSuffix']['value'] = cbsScriptSettings.bSuffix
    ui['CommandAlts']['value'] = cbsScriptSettings.CommandAlts
    ui['ShowDecorationAlert']['value'] = cbsScriptSettings.ShowDecorationAlert
    ui['Tripwire']['value'] = cbsScriptSettings.Tripwire

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))
