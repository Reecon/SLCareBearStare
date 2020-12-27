Gives you the ability to have target specific shoutouts for channel friends with only one command.

A default message will be shown if the target has no configured blurb.

You can also set an option automatically shout out streamers with the partnered badge on their first message in chat.

supported parameters are:
- $targetname for the targets username 
- $url for the targets twitch url `https://www.twitch.tv/targetname`
- $shorturl shorter version of the twitch url `twitch.tv/targetname`
- $lastplayed last game category the target streamed under

one target per line, line beginning with target's username followed by a space and the response enclosed by quotation marks
i.e.
```
kaypikefashion "$targetname is THE Bodypainter -> $url"
```

### Installation
* Download the [latest release](https://github.com/Reecon/SLCareBearStare/releases/latest)
* Import the zip-file into the bot
* Open the scripts-folder and remove the the `.example` file extension from `clientid.conf.example` and `stares.conf.example` and reload the script
* Right-click the script in the bot and select "Insert API Key" and confirm
* Click the `Copy Overlaypath to Clipboard` button and use this as the path to a local browser source in your streaming software

__Note:__ The client-id is only neccesarry when you use the overlay as it queries data from the Twitch API.

## AlertBox
You need to add a client id from twitch to use the on screen alert as it makes a request to twitch's api. See for more info https://dev.twitch.tv/docs/v5/

CSS classes for the alert box to customize in OBS are
'alertbox' for the entire box
'logo' for the profile picture
'response' for the response text

i.e.
```
.logo{float: right;}
.response {font-size:42px; color: red;}
.alertbox{background-color: blue;}
```

with fancy animation (paste into OBS custom ccs window)
```
body { background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }
.logo{
    float: left; 
    height:250px;
    margin: 10px;
}
.response {
    font-size:32px;
    color: white;
    text-shadow: 1px 1px 15px blue;
}
div .alertbox {
    right: -800px;
    position: relative;
    animation-name: slidein;
    animation-duration: 20s;
    word-wrap: break-word;
    word-break: keep-all;
}
@keyframes slidein {
    0%   {right:-800px;}
    5%  {right:0px;}
    95%  {right:0px;}
    100% {right:-800px;}
}
```