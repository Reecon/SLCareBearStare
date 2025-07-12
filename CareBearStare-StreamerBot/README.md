# CareBearStare for Streamer.bot

This is a migration of the CareBearStare script from Streamlabs Chatbot to Streamer.bot.

## Installation

1.  Open Streamer.bot and go to the "Actions" tab.
2.  Right-click and select "Add".
3.  Name the action "CareBearStare".
4.  In the "Actions" list, right-click and select "Add Action" -> "C#" -> "Execute C# Code".
5.  Copy the code from `CareBearStare.cs` and paste it into the C# code window.
6.  Click "Compile" and then "Save".

## Configuration

1.  **Commands:**
    *   Go to the "Settings" -> "Commands" tab.
    *   Add a new command with the command `!stare`.
    *   Set the action to the "CareBearStare" action you created.
    *   Configure the permission and cooldown as desired.

2.  **Tripwire:**
    *   Go to the "Actions" tab.
    *   Create a new action named "CareBearStare Tripwire".
    *   Add a "C#" -> "Execute C# Code" action.
    *   Paste the same code from `CareBearStare.cs`.
    *   Go to the "Settings" -> "Events" -> "Chat" tab.
    *   Add a new event for "Chat Message".
    *   Set the action to the "CareBearStare Tripwire" action.

3.  **Files:**
    *   Place the `stares.conf` file in the root of your Streamer.bot installation directory.

4.  **Overlay:**
    *   Add a new browser source in your streaming software.
    *   Set the URL to the `StareOverlay.html` file.

## Settings

The following settings can be configured at the top of the `CareBearStare.cs` file:

*   `Command`: The main command to trigger the shoutout.
*   `Cooldown`: The cooldown in seconds for the command.
*   `Permission`: The required permission to use the command.
*   `ShowAlert`: Whether to show the on-screen alert.
*   `Prefix`: Text to add before the shoutout message.
*   `Suffix`: Text to add after the shoutout message.
*   `CommandAlts`: Alternative commands separated by spaces.
*   `ShowDecorationAlert`: Whether to show the prefix and suffix in the alert.
*   `Tripwire`: Enable automatic shoutouts for partnered streamers.
*   `TripwireCustom`: Enable automatic shoutouts for streamers with custom messages.