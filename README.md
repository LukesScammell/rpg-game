# Python RPG Adventure

This file documents the development of a command-line RPG created with the help of a large language model. It tracks the game's evolution through different versions, detailing the features added at each stage and the prompts used to generate them.

## Version History

### v1.0: Initial Implementation

*   **Prompt:** "give me python code to replace the rpg game which adds the features enemy icons, room generation, loot and potions, multiple player or character at once (control multiple hero's and have a turn system for fights), having multiple enemies able to be in an encounter, Leaderboard/highscore for the longest run or the best loot or a specific thing to be ranked on, have characyer classes which have different stats and weapons and movement buffs or debuffs"
*   **Changes:**
    *   Replaced the original `rpg.py` with a more advanced version.
    *   Added core features like character classes, procedural dungeon generation, and a highscore system.

### v1.1: Bug Fixes

*   **Prompt:** "there was the error on line 370, 237 and 71"
*   **Changes:**
    *   Fixed several bugs that were causing the game to crash.
    *   Added input validation and error handling to improve stability.

### v1.2: Expanded Item System

*   **Prompt:** "it runs great could you add armour pieces and different weapons that the player can find in the dungeon and add the mechanics for those"
*   **Changes:**
    *   Introduced equippable armor and a wider variety of weapons.
    *   Updated the player and combat systems to handle the new items.

### v1.3: Dungeon Levels and Improved Inventory

*   **Prompt:** "could you make it so there are different levels of the dungeons and at the last level there is a boss and also can you have a better item chooser so that the armour and weapons are seperate and you can kinda do an equip type feature"
*   **Changes:**
    *   Added multiple dungeon floors with a final boss on the last level.
    *   Created a dedicated inventory screen for easier item management.

### v1.4: Emoji-Based UI

*   **Prompt:** "could you make the ui of the game look a bit better using emojis or could i possibly use gui"
*   **Changes:**
    *   Replaced all text-based icons with emojis for a more visual experience.
    *   Updated the map and status display to use the new emoji set.

### v1.5: Class-Specific Skills

*   **Prompt:** "Please continue."
*   **Changes:**
    *   Added unique skills for each character class (Power Strike, Fireball, Double Shot).
    *   Introduced mana and cooldown systems to make combat more strategic.

## Features

*   **Character Classes:** Choose from three distinct classes: Warrior, Mage, and Archer.
*   **Procedural Dungeons:** Explore randomly generated dungeons with unique layouts every time.
*   **Loot and Equipment:** Find and equip a variety of weapons and armor.
*   **Turn-Based Combat:** Engage in strategic turn-based combat with multiple enemies.
*   **Party System:** Control a party of up to three heroes.
*   **Highscore Leaderboard:** Compete for the highest score.
*   **Dungeon Levels:** Descend through multiple dungeon floors, with a final boss at the end.
*   **Emoji UI:** A vibrant and visually appealing emoji-based user interface.
*   **Class-Specific Skills:** Unleash powerful, unique abilities for each character class.