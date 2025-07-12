using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;

public class CPHInline
{
    // Configuration
    private const string StaresConfigFile = @"stares.conf";
    private const string ClientIdFile = @"clientid.conf";

    // Settings - these will be configurable in Streamer.bot
    public string Command = "!stare";
    public int Cooldown = 10;
    public string Permission = "everyone";
    public bool ShowAlert = false;
    public string Prefix = "";
    public string Suffix = "";
    public string CommandAlts = "";
    public bool ShowDecorationAlert = false;
    public bool Tripwire = false;
    public bool TripwireCustom = false;

    private Dictionary<string, string> stareDict = new Dictionary<string, string>();
    private string clientId;

    public bool Execute()
    {
        // Load configuration
        LoadStaresConfig();
        LoadClientId();

        // Check if the command is triggered
        if (args.ContainsKey("command") && (args["command"].ToString().ToLower() == Command || Array.Exists(CommandAlts.Split(' '), s => s == args["command"].ToString().ToLower())))
        {
            // Handle the !stare command
            StareCommand(args);
        }
        else if (Tripwire || TripwireCustom)
        {
            // Handle the tripwire functionality
            TripwireCheck(args);
        }

        return true;
    }

    private void StareCommand(Dictionary<string, object> args)
    {
        // Check for cooldown and permission
        if (CPH.IsOnCooldown(Command, Permission) || !CPH.HasPermission(args["user"].ToString(), Permission, ""))
        {
            return;
        }

        string target = args.ContainsKey("target") ? args["target"].ToString() : "";
        if (string.IsNullOrEmpty(target) && args.ContainsKey("message"))
        {
            var match = Regex.Match(args["message"].ToString(), @"^@?(\w+)");
            if (match.Success)
            {
                target = match.Groups[1].Value;
            }
        }

        if (string.IsNullOrEmpty(target))
        {
            return;
        }

        string response = GetStareMessage(target);
        string lastPlayed = GetLastPlayed(target);

        response = Parse(response, args["user"].ToString(), args["user"].ToString(), lastPlayed, target, target, args["message"].ToString());
        string prefix = Parse(Prefix, args["user"].ToString(), args["user"].ToString(), lastPlayed, target, target, args["message"].ToString());
        string suffix = Parse(Suffix, args["user"].ToString(), args["user"].ToString(), lastPlayed, target, target, args["message"].ToString());

        if (ShowAlert)
        {
            TriggerAlert(response, target);
        }

        if (!ShowDecorationAlert)
        {
            response = $"{prefix} {response} {suffix}";
        }

        CPH.SendMessage(response);
        CPH.AddCooldown(Command, Cooldown);
    }

        private void TripwireCheck(Dictionary<string, object> args)
    {
        string user = args["user"].ToString();
        bool isPartner = args.ContainsKey("isPartner") && (bool)args["isPartner"];

        if ((isPartner && Tripwire) || (stareDict.ContainsKey(user.ToLower()) && TripwireCustom))
        {
            if (!CPH.GetGlobalVar<List<string>>("cbsAutoShoutouts", true).Contains(user))
            {
                CPH.GetGlobalVar<List<string>>("cbsAutoShoutouts", true).Add(user);
                StareCommand(new Dictionary<string, object> { { "command", Command }, { "target", user }, { "user", user }, { "message", "" } });
            }
        }
    }

    private Dictionary<string, object> GetTwitchUser(string username)
    {
        string url = $"https://api.twitch.tv/helix/users?login={username}";
        var response = CPH.GetRequest(url, new Dictionary<string, string> { { "Client-ID", clientId }, { "Authorization", $"Bearer {CPH.GetGlobalVar<string>("twitchAccessToken", true)}" } });
        var json = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, object>>(response);
        if (json.ContainsKey("data"))
        {
            var data = (Newtonsoft.Json.Linq.JArray)json["data"];
            if (data.Count > 0)
            {
                return data[0].ToObject<Dictionary<string, object>>();
            }
        }
        return null;
    }

    private Dictionary<string, object> GetTwitchChannel(string userId)
    {
        string url = $"https://api.twitch.tv/helix/channels?broadcaster_id={userId}";
        var response = CPH.GetRequest(url, new Dictionary<string, string> { { "Client-ID", clientId }, { "Authorization", $"Bearer {CPH.GetGlobalVar<string>("twitchAccessToken", true)}" } });
        var json = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, object>>(response);
        if (json.ContainsKey("data"))
        {
            var data = (Newtonsoft.Json.Linq.JArray)json["data"];
            if (data.Count > 0)
            {
                return data[0].ToObject<Dictionary<string, object>>();
            }
        }
        return null;
    }


    private string GetStareMessage(string target)
    {
        if (stareDict.ContainsKey(target.ToLower()))
        {
            return stareDict[target.ToLower()];
        }
        else if (stareDict.ContainsKey("default"))
        {
            return stareDict["default"];
        }
        return "";
    }

            private string GetLastPlayed(string target)
    {
        var userInfo = CPH.TwitchGetUserInfoByLogin(target);
        if (userInfo != null)
        {
            return userInfo.Game.Name;
        }
        return "N/A";
    }

    private void TriggerAlert(string response, string target)
    {
        var userInfo = CPH.TwitchGetUserInfoByLogin(target);
        if (userInfo != null)
        {
            var data = new Dictionary<string, object>
            {
                { "response", response },
                { "logo", userInfo.LogoUrl },
                { "emotesets", new int[] { } } // Emote sets are not easily available in the new API
            };
            CPH.WebsocketBroadcastJson(Newtonsoft.Json.JsonConvert.SerializeObject(data));
        }
    }

    private string Parse(string parseString, string userId, string username, string lastPlayed, string targetId, string targetName, string message)
    {
        return parseString
            .Replace("$userid", userId)
            .Replace("$username", username)
            .Replace("$targetid", targetId)
            .Replace("$targetname", targetName)
            .Replace("$lastplayed", lastPlayed)
            .Replace("$url", $"https://www.twitch.tv/{targetName.ToLower()}")
            .Replace("$shorturl", $"twitch.tv/{targetName.ToLower()}");
    }

    private void LoadStaresConfig()
    {
        if (File.Exists(StaresConfigFile))
        {
            stareDict.Clear();
            var lines = File.ReadAllLines(StaresConfigFile);
            foreach (var line in lines)
            {
                if (!string.IsNullOrWhiteSpace(line) && !line.StartsWith("#"))
                {
                    var parts = line.Split(new[] { ' ' }, 2);
                    if (parts.Length == 2)
                    {
                        var user = parts[0].ToLower();
                        var response = parts[1].Trim('"');
                        stareDict[user] = response;
                    }
                }
            }
        }
    }

    
}