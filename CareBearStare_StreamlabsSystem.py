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

#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "CareBearStare"
Website = "reecon820@gmail.com"
Description = "Target specific shoutouts with a single command"
Creator = "Reecon820"
Version = "1.0.1.1"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()
global StareDict
StareDict = {}

global StarePath
StarePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "stares.conf")).replace("\\", "/")

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global SettingsFile
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    global ScriptSettings
    ScriptSettings = MySettings(SettingsFile)

    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # update ui with loaded settings
    ui['Command']['value'] = ScriptSettings.Command
    ui['Cooldown']['value'] = ScriptSettings.Cooldown
    ui['Permission']['value'] = ScriptSettings.Permission
    ui['Info']['value'] = ScriptSettings.Info
    ui['ShowAlert']['value'] = ScriptSettings.ShowAlert
    ui['aPrefix']['value'] = ScriptSettings.aPrefix
    ui['bSuffix']['value'] = ScriptSettings.bSuffix
    ui['CommandAlts']['value'] = ScriptSettings.CommandAlts

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # read client id for api access from file
    try:
        with codecs.open(os.path.join(os.path.dirname(__file__), "clientid.conf"), mode='r', encoding='utf-8-sig') as f:
            global ClientID
            ClientID = f.readline()
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    LoadConfigFile()

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   only handle messages from chat
    if data.IsChatMessage() and not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command) and Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.Info):

        isComamnd = data.GetParam(0).lower() == ScriptSettings.Command

        if not isComamnd:
            alts = ScriptSettings.CommandAlts.split(" ")
            for s in alts:
                if s == data.GetParam(0).lower():
                    isCommand = True
                    break
            if not isCommand:
                return
                
        found = False
        target = ''
        response = ''
        prefix = ScriptSettings.aPrefix
        suffix = ScriptSettings.bSuffix

        # check if target was given
        if data.GetParam(1):
            target = data.GetParam(1)
            if target[0] == '@':
                target = target[1:]
        
        # check if target has custom shoutout
        if target.lower() in StareDict:
            response = StareDict[target.lower()]
        else:
            response = StareDict['default']
        
        # replace params in response string
        response = Parse(response, data.UserName, data.UserName, target, target, data.Message)
        prefix = Parse(prefix, data.UserName, data.UserName, target, target, data.Message)
        suffix = Parse(suffix, data.UserName, data.UserName, target, target, data.Message)

        # show alert?
        if ScriptSettings.ShowAlert:
            
            # get profile picture link
            headers = {'Client-ID': ClientID, 'Accept': 'application/vnd.twitchtv.v5+json'}
            result = Parent.GetRequest("https://api.twitch.tv/kraken/users?login={0}".format(target.lower()), headers)
            
            jsonResult = json.loads(result)

            if jsonResult['status'] != 200:
                Parent.Log(ScriptName, "{0}".format(jsonResult))
            else:
                jsonResult = json.loads(jsonResult['response'])
                if jsonResult['users']:
                    jsonResult = jsonResult['users'][0]

                    if ScriptSettings.ShowDecorationAlert:
                        response = "{0} {1} {2}".format(prefix.strip(), response.strip(), suffix.strip())
                    
                    jsonData = '{{"response": "{0}", "logo": "{1}" }}'.format(response, jsonResult['logo'])
                    Parent.BroadcastWsEvent("EVENT_STARE", jsonData)
                else:
                    # don't do a shoutout if the user doesn't exist
                    Parent.Log(ScriptName, "Unknown Twitch Username")
                    return
        
        # if the option is active this is already done
        if not ScriptSettings.ShowDecorationAlert:
            response = "{0} {1} {2}".format(prefix.strip(), response.strip(), suffix.strip())
        
        Parent.SendStreamMessage(response)    # Send message to chat
        Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)  # Put the command on cooldown

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
    ScriptSettings.Reload(jsonData)
    ScriptSettings.Save(SettingsFile)
    LoadConfigFile()
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
    os.startfile(StarePath)
    return

def LoadConfigFile():
    try:
        with codecs.open(StarePath, encoding="utf-8-sig", mode="r") as f:
            matches = {}
            for line in f:
                user = line.split(" ")[0].lower()
                response = re.search("\".*\"", line).group(0).strip('"')
                matches[user] = response

            global StareDict
            StareDict = matches
    except Exception as err:
        Parent.Log(ScriptName, "Could not load stares file {0}".format(err))

    return

def CopyPath():
    command = "echo " + os.path.abspath(os.path.join(os.path.dirname(__file__), "Overlays/StareOverlay.html")) + "| clip"
    os.system(command)
    return
