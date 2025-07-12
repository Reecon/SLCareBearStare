# Migration Plan: CareBearStare from Streamlabs Chatbot to Streamer.bot

This document outlines the plan to migrate the CareBearStare script from the Streamlabs Chatbot (IronPython) to Streamer.bot (C#).

## 1. Project Setup

*   **Directory Structure:** Create a new directory for the Streamer.bot project, for example, `CareBearStare-StreamerBot`.
*   **C# Code:** The C# code will be written as an "inline action" within Streamer.bot. For more complex logic, we can use the Visual Studio Code setup for Streamer.bot C# development.
*   **Configuration Files:** The `stares.conf` and `clientid.conf` files will still be used. We will need to provide instructions on where to place them.

## 2. Settings Migration

The settings from `UI_Config.json` will be migrated to Streamer.bot's action/trigger configuration and C# code.

*   **Command, Cooldown, Permission:** These will be configured directly in the Streamer.bot "Command" trigger.
*   **Prefix, Suffix, Alerts, Tripwire:** These settings will be managed within the C# code. We can use a JSON file (e.g., `settings.json`) to store these, similar to the original script, or use Streamer.bot's argument system.

## 3. Core Logic Migration (C#)

The core logic from `CareBearStare_StreamlabsSystem.py` will be rewritten in C#.

*   **Main Action (`!stare` command):**
    *   Create a C# inline action in Streamer.bot.
    *   This action will be triggered by a "Command" trigger for `!stare` and its aliases.
    *   The C# code will handle parsing the target user from the command.
    *   It will read the `stares.conf` file to get the custom shoutout messages.
    *   It will construct the final shoutout message with the prefix and suffix.
    *   It will send the message to the chat using `CPH.SendMessage()`.

*   **Automatic Shoutout (Tripwire):**
    *   Create a separate C# inline action for the tripwire functionality.
    *   This action will be triggered by a "Chat Message" trigger.
    *   The C# code will check if the user is a partner or has a custom shoutout message.
    *   It will also check if it's the user's first message in the session to prevent spamming shoutouts.

*   **Twitch API Integration:**
    *   The Twitch API calls will be updated from the deprecated Kraken v5 to the new Twitch API.
    *   The C# code will use `CPH.GetRequest()` to make the API calls.
    *   It will fetch the user's profile picture and last played game.
    *   The Client ID will be read from the `clientid.conf` file.

## 4. Overlay Migration

The `StareOverlay.html` will be adapted to work with Streamer.bot's browser source and WebSocket.

*   **New HTML File:** Create a new HTML file for the overlay.
*   **WebSocket Connection:** The JavaScript code will be updated to connect to the Streamer.bot WebSocket server.
*   **Event Handling:** The code will listen for a custom event from the C# script (e.g., `EVENT_STARE`).
*   **Data Parsing:** The JavaScript will parse the data sent from the C# script (profile picture URL, shoutout message).
*   **Emote Parsing:** The logic for parsing and displaying Twitch emotes will be preserved and adapted.

## 5. Helper Functions

The helper functions from the Python script will be re-implemented in C#.

*   **`LoadConfigFile`:** A C# function to read and parse the `stares.conf` file.
*   **`Parse`:** A C# function to replace variables like `$targetname`, `$lastplayed`, etc., in the shoutout message.

## 6. Step-by-Step Implementation Plan

1.  **Setup:** Create the directory structure and C# project/files.
2.  **Settings:** Implement the settings management in C#.
3.  **Config:** Implement the `stares.conf` reading logic.
4.  **`!stare` command:** Implement the main command action.
5.  **Twitch API:** Implement the Twitch API calls.
6.  **Overlay:** Create the new HTML overlay and WebSocket logic.
7.  **Alerts:** Implement the logic to trigger the on-screen alert.
8.  **Tripwire:** Implement the automatic shoutout functionality.
9.  **Testing:** Thoroughly test all features.
10. **Documentation:** Write a `README.md` with installation and configuration instructions.

This plan provides a clear path to migrating the CareBearStare script to Streamer.bot. By following these steps, we can ensure that all the original functionality is preserved and enhanced by the capabilities of Streamer.bot.
