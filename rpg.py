#!/usr/bin/env python
import random
import os
import json
from collections import deque

# --- Constants ---
MAP_WIDTH = 40
MAP_HEIGHT = 20
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 15
MAX_DUNGEON_LEVEL = 5
HIGHSCORE_FILE = "rpg_highscores.json"

# --- UI Elements ---
UI = {
    "player": "🤺",
    "warrior": "🤺",
    "mage": "🧙",
    "archer": "🏹",
    "goblin": "👺",
    "orc": "👹",
    "troll": "👾",
    "dragon": "🐉",
    "potion": "🧪",
    "weapon": "⚔️",
    "armor": "🛡️",
    "wall": "🧱",
    "floor": "⬛",
    "stairs": "🔽",
    "hp": "❤️",
    "xp": "✨",
    "mana": "💧",
    "attack": "💥",
    "defense": "🛡️",
    "level": "🌟"
}


# --- Character Classes ---
CLASSES = {
    "warrior": {"hp": 120, "attack": 15, "defense": 10, "icon": UI["warrior"], "weapon": "Sword", "mana": 0},
    "mage": {"hp": 80, "attack": 20, "defense": 5, "icon": UI["mage"], "weapon": "Staff", "mana": 20},
    "archer": {"hp": 100, "attack": 12, "defense": 8, "icon": UI["archer"], "weapon": "Bow", "mana": 0}
}

# --- Enemy Types ---
ENEMIES = {
    "goblin": {"hp": 30, "attack": 8, "defense": 2, "xp": 50, "icon": UI["goblin"]},
    "orc": {"hp": 50, "attack": 12, "defense": 4, "xp": 100, "icon": UI["orc"]},
    "troll": {"hp": 80, "attack": 15, "defense": 6, "xp": 150, "icon": UI["troll"]},
    "dragon": {"hp": 250, "attack": 25, "defense": 15, "xp": 1000, "icon": UI["dragon"]}
}

# --- Items ---
class Item:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

class Potion(Item):
    def __init__(self, name, hp_gain):
        super().__init__(name, UI["potion"])
        self.hp_gain = hp_gain

    def use(self, target):
        target.hp = min(target.max_hp, target.hp + self.hp_gain)
        return f'{target.name} used {self.name} and gained {self.hp_gain} HP.'

class Weapon(Item):
    def __init__(self, name, attack_bonus):
        super().__init__(name, UI["weapon"])
        self.attack_bonus = attack_bonus

class Armor(Item):
    def __init__(self, name, defense_bonus):
        super().__init__(name, UI["armor"])
        self.defense_bonus = defense_bonus

# --- Pre-defined Items ---
WEAPONS = [
    Weapon("Dagger", 3),
    Weapon("Short Sword", 5),
    Weapon("Long Sword", 7),
    Weapon("Battle Axe", 10)
]

ARMOR = [
    Armor("Leather Armor", 3),
    Armor("Chainmail", 5),
    Armor("Plate Armor", 7)
]

# --- Entities ---
class Entity:
    def __init__(self, x, y, name, hp, attack, defense, icon):
        self.x = x
        self.y = y
        self.name = name
        self.base_attack = attack
        self.base_defense = defense
        self.max_hp = hp
        self.hp = hp
        self.icon = icon

    @property
    def attack(self):
        bonus = self.weapon.attack_bonus if hasattr(self, 'weapon') and self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = self.armor.defense_bonus if hasattr(self, 'armor') and self.armor else 0
        return self.base_defense + bonus

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

class Player(Entity):
    def __init__(self, x, y, name, char_class):
        super().__init__(x, y, name, CLASSES[char_class]["hp"], CLASSES[char_class]["attack"], CLASSES[char_class]["defense"], CLASSES[char_class]["icon"])
        self.char_class = char_class
        self.xp = 0
        self.level = 1
        self.inventory = [Weapon(CLASSES[char_class]["weapon"], 5)]
        self.weapon = self.inventory[0]
        self.armor = None
        self.max_mana = CLASSES[char_class]["mana"]
        self.mana = self.max_mana
        self.skill_cooldown = 0

    def gain_xp(self, xp):
        self.xp += xp
        if self.xp >= self.level * 100:
            return self.level_up()
        return None

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.base_attack += 5
        self.base_defense += 2
        self.max_mana += 5
        self.mana = self.max_mana
        self.xp = 0
        return f'\n{self.name} leveled up to level {self.level}! Stats increased.'

class Enemy(Entity):
    def __init__(self, x, y, enemy_type):
        super().__init__(x, y, enemy_type.capitalize(), ENEMIES[enemy_type]["hp"], ENEMIES[enemy_type]["attack"], ENEMIES[enemy_type]["defense"], ENEMIES[enemy_type]["icon"])
        self.xp = ENEMIES[enemy_type]["xp"]

# --- Map Generation ---
class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Dungeon:
    def __init__(self, width, height, level):
        self.width = width
        self.height = height
        self.level = level
        self.grid = [[UI["wall"] for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.items = []
        self.enemies = []
        self.stairs_down = None

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.grid[y][x] = UI["floor"]

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = UI["floor"]

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = UI["floor"]

    def generate(self):
        for _ in range(MAX_ROOMS):
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = random.randint(0, self.width - w - 1)
            y = random.randint(0, self.height - h - 1)

            new_room = Rect(x, y, w, h)
            if any(new_room.intersects(other_room) for other_room in self.rooms):
                continue

            self.create_room(new_room)
            (new_x, new_y) = new_room.center()

            if self.rooms:
                (prev_x, prev_y) = self.rooms[-1].center()
                if random.randint(0, 1) == 1:
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                else:
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)
            
            self.place_content(new_room)
            self.rooms.append(new_room)
        
        # Place stairs
        if self.level < MAX_DUNGEON_LEVEL:
            last_room = self.rooms[-1]
            self.stairs_down = last_room.center()
            self.grid[self.stairs_down[1]][self.stairs_down[0]] = UI["stairs"]
        else: # Boss level
            boss_room = self.rooms[-1]
            boss_x, boss_y = boss_room.center()
            self.enemies.append(Enemy(boss_x, boss_y, "dragon"))

    def place_content(self, room):
        # Place enemies
        num_enemies = random.randint(0, 3)
        for _ in range(num_enemies):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(e.x == x and e.y == y for e in self.enemies):
                enemy_type = random.choice(list(ENEMIES.keys() - {'dragon'}))
                self.enemies.append(Enemy(x, y, enemy_type))
        
        # Place items
        num_items = random.randint(0, 2)
        for _ in range(num_items):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(i.x == x and i.y == y for i in self.items):
                item_choice = random.random()
                if item_choice < 0.4:
                    item = Potion("Health Potion", 20)
                elif item_choice < 0.7:
                    item = random.choice(WEAPONS)
                else:
                    item = random.choice(ARMOR)
                item.x = x
                item.y = y
                self.items.append(item)


# --- Game ---
class Game:
    def __init__(self):
        self.players = []
        self.dungeon = None
        self.current_player_idx = 0
        self.game_over = False
        self.dungeon_level = 1
        self.messages = deque(maxlen=5)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def add_message(self, msg):
        self.messages.append(msg)

    def print_game(self):
        self.clear_screen()
        # Draw map
        print(f'--- Dungeon Level {self.dungeon_level} ---')
        # Double check if the terminal is printing the emojis correctly
        # For windows, we might need to set the encoding
        if os.name == 'nt':
            os.system('chcp 65001')

        for y in range(self.dungeon.height):
            row = []
            for x in range(self.dungeon.width):
                icon = self.dungeon.grid[y][x]
                
                # Check for items
                item_on_tile = False
                for item in self.dungeon.items:
                    if item.x == x and item.y == y:
                        icon = item.icon
                        item_on_tile = True
                        break
                if item_on_tile:
                    row.append(icon)
                    continue

                # Check for enemies
                enemy_on_tile = False
                for enemy in self.dungeon.enemies:
                    if enemy.x == x and enemy.y == y:
                        icon = enemy.icon
                        enemy_on_tile = True
                        break
                if enemy_on_tile:
                    row.append(icon)
                    continue
                
                # Check for players
                player_on_tile = False
                for player in self.players:
                    if player.x == x and player.y == y:
                        icon = player.icon
                        player_on_tile = True
                        break
                if player_on_tile:
                    row.append(icon)
                    continue
                
                row.append(icon)
            print("".join(row))
        
        # Print status
        self.print_status()
        # Print messages
        print("\n--- Messages ---")
        for msg in self.messages:
            print(msg)

    def print_status(self):
        print("\n--- Party ---")
        for p in self.players:
            weapon_name = p.weapon.name if p.weapon else "None"
            armor_name = p.armor.name if p.armor else "None"
            mana_str = f'| {UI["mana"]} {p.mana}/{p.max_mana}' if p.max_mana > 0 else ""
            print(f'{p.icon} {p.name} ({p.char_class}) | {UI["level"]} {p.level} | {UI["hp"]} {p.hp}/{p.max_hp} {mana_str} | {UI["xp"]} {p.xp}/{p.level*100} | {UI["attack"]} {p.attack} | {UI["defense"]} {p.defense} | {UI["weapon"]} {weapon_name} | {UI["armor"]} {armor_name}')

    def setup_game(self):
        self.clear_screen()
        num_players = 0
        while not (1 <= num_players <= 3):
            try:
                num_players = int(input("Enter number of heroes (1-3): "))
                if not (1 <= num_players <= 3):
                    print("Please enter a number between 1 and 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        for i in range(num_players):
            name = input(f"Enter name for hero {i+1}: ")
            class_choice = ""
            while class_choice not in CLASSES:
                class_choice = input(f"Choose class for {name} (warrior, mage, archer): ").lower()
                if class_choice not in CLASSES:
                    print("Invalid class. Please choose from warrior, mage, or archer.")
            self.players.append(Player(0, 0, name, class_choice))
        
        self.new_level()

    def new_level(self):
        self.dungeon = Dungeon(MAP_WIDTH, MAP_HEIGHT, self.dungeon_level)
        self.dungeon.generate()
        start_room = self.dungeon.rooms[0]
        for player in self.players:
            player.x, player.y = start_room.center()
        self.add_message(f"You have entered dungeon level {self.dungeon_level}.")

    def main_loop(self):
        while not self.game_over:
            self.print_game()
            player = self.players[self.current_player_idx]
            if player.skill_cooldown > 0:
                player.skill_cooldown -= 1

            action = input(f"\n{player.name}'s turn. Move (w/a/s/d), (i)nventory, or (q)uit: ").lower()

            if action == 'q':
                self.game_over = True
                continue
            
            if action in ['w', 'a', 's', 'd']:
                self.move_player(player, action)
            elif action == 'i':
                self.show_inventory(player)

            if not self.game_over:
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def move_player(self, player, direction):
        dx, dy = 0, 0
        if direction == 'w': dy = -1
        if direction == 's': dy = 1
        if direction == 'a': dx = -1
        if direction == 'd': dx = 1

        new_x, new_y = player.x + dx, player.y + dy
        
        if not (0 <= new_x < self.dungeon.width and 0 <= new_y < self.dungeon.height):
            self.add_message("You can't move off the map.")
            return

        if self.dungeon.grid[new_y][new_x] == UI["stairs"]:
            self.dungeon_level += 1
            self.new_level()
            return

        if self.dungeon.grid[new_y][new_x] == UI["floor"]:
            enemies_in_pos = [e for e in self.dungeon.enemies if e.x == new_x and e.y == new_y]
            if enemies_in_pos:
                self.start_combat(enemies_in_pos)
            else:
                player.x = new_x
                player.y = new_y
                for item in list(self.dungeon.items):
                    if item.x == new_x and item.y == new_y:
                        player.inventory.append(item)
                        self.dungeon.items.remove(item)
                        self.add_message(f"{player.name} picked up a {item.name}.")
        else:
            self.add_message("You can't move there.")

    def show_inventory(self, player):
        self.print_game()
        print("\n--- Inventory ---")
        print(f"Weapon: {player.weapon.name if player.weapon else 'None'}")
        print(f"Armor: {player.armor.name if player.armor else 'None'}")
        print("\nItems:")
        for i, item in enumerate(player.inventory):
            print(f"{i+1}. {item.name}")
        
        action = input("\n(u)se, (e)quip, or (c)ancel: ").lower()
        if action == 'u':
            self.use_potion(player)
        elif action == 'e':
            self.equip_item(player)

    def use_potion(self, player):
        potions = [item for item in player.inventory if isinstance(item, Potion)]
        if not potions:
            self.add_message("You have no potions to use.")
            return
        
        for i, p in enumerate(potions):
            print(f"{i+1}. {p.name}")
        choice = input("Choose a potion to use: ")
        if choice.isdigit() and 0 < int(choice) <= len(potions):
            potion = potions[int(choice)-1]
            msg = potion.use(player)
            self.add_message(msg)
            player.inventory.remove(potion)
        else:
            self.add_message("Invalid choice.")

    def equip_item(self, player):
        equippable = [item for item in player.inventory if isinstance(item, (Weapon, Armor))]
        if not equippable:
            self.add_message("You have nothing to equip.")
            return

        for i, item in enumerate(equippable):
            print(f"{i+1}. {item.name}")
        choice = input("Choose an item to equip: ")
        if choice.isdigit() and 0 < int(choice) <= len(equippable):
            item = equippable[int(choice)-1]
            if isinstance(item, Weapon):
                if player.weapon:
                    player.inventory.append(player.weapon)
                player.weapon = item
                player.inventory.remove(item)
                self.add_message(f"{player.name} equipped {item.name}.")
            elif isinstance(item, Armor):
                if player.armor:
                    player.inventory.append(player.armor)
                player.armor = item
                player.inventory.remove(item)
                self.add_message(f"{player.name} equipped {item.name}.")
        else:
            self.add_message("Invalid choice.")

    def start_combat(self, enemies):
        self.add_message("You've entered combat!")
        turn_order = self.players + enemies
        random.shuffle(turn_order)

        while any(p.is_alive() for p in self.players) and any(e.is_alive() for e in enemies):
            for entity in turn_order:
                if not entity.is_alive(): continue
                
                self.print_game()
                print("\n--- Combat ---")
                for p in self.players: print(f"{p.name} HP: {p.hp}/{p.max_hp}")
                for e in enemies: print(f"{e.name} HP: {e.hp}")

                if isinstance(entity, Player):
                    action = input(f"\n{entity.name}'s turn. (1) Attack, (2) Skill, (3) Inventory: ").lower()
                    if action == '1':
                        alive_enemies = [e for e in enemies if e.is_alive()]
                        if alive_enemies:
                            target = random.choice(alive_enemies)
                            damage = max(0, entity.attack - target.defense)
                            target.take_damage(damage)
                            self.add_message(f"{entity.name} hits {target.name} for {damage} damage.")
                    elif action == '2':
                        self.use_skill(entity, enemies)
                    elif action == '3':
                        self.show_inventory(entity)
                else: # Enemy turn
                    alive_players = [p for p in self.players if p.is_alive()]
                    if alive_players:
                        target = random.choice(alive_players)
                        damage = max(0, entity.attack - target.defense)
                        target.take_damage(damage)
                        self.add_message(f"{entity.name} hits {target.name} for {damage} damage.")
        
        if any(p.is_alive() for p in self.players):
            if any(e.name == 'Dragon' for e in enemies):
                self.add_message("Congratulations! You have defeated the Dragon and won the game!")
                self.game_over = True
            else:
                self.add_message("You won the battle!")
            total_xp = sum(e.xp for e in enemies)
            xp_per_player = total_xp // len(self.players) if self.players else 0
            for p in self.players:
                if p.is_alive():
                    msg = p.gain_xp(xp_per_player)
                    if msg: self.add_message(msg)
            self.dungeon.enemies = [e for e in self.dungeon.enemies if e not in enemies]
        else:
            self.add_message("Your party has been defeated. Game Over.")
            self.game_over = True
            self.update_highscores()

    def use_skill(self, player, enemies):
        if player.char_class == "warrior":
            if player.skill_cooldown > 0:
                self.add_message(f"Power Strike is on cooldown for {player.skill_cooldown} more turns.")
                return
            target = random.choice([e for e in enemies if e.is_alive()])
            damage = player.attack * 2
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            player.skill_cooldown = 3
        elif player.char_class == "mage":
            if player.mana < 10:
                self.add_message("Not enough mana for Fireball.")
                return
            self.add_message(f"{player.name} casts Fireball!")
            for enemy in enemies:
                if enemy.is_alive():
                    damage = player.attack // 2
                    enemy.take_damage(damage)
                    self.add_message(f"Fireball hits {enemy.name} for {damage} damage.")
            player.mana -= 10
        elif player.char_class == "archer":
            if player.skill_cooldown > 0:
                self.add_message(f"Double Shot is on cooldown for {player.skill_cooldown} more turns.")
                return
            self.add_message(f"{player.name} uses Double Shot!")
            for _ in range(2):
                target = random.choice([e for e in enemies if e.is_alive()])
                damage = player.attack
                target.take_damage(damage)
                self.add_message(f"{player.name} shoots {target.name} for {damage} damage.")
            player.skill_cooldown = 2

    def update_highscores(self):
        scores = []
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, 'r') as f:
                    scores = json.load(f)
            except json.JSONDecodeError:
                scores = []
        
        total_xp = sum(p.xp for p in self.players)
        party_names = ", ".join([p.name for p in self.players])
        scores.append({"party": party_names, "level": self.dungeon_level, "xp": total_xp})
        
        scores = sorted(scores, key=lambda x: (x['level'], x['xp']), reverse=True)[:10]

        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=4)
        
        print("\n--- Highscores ---")
        for score in scores:
            print(f"Party: {score['party']}, Level: {score['level']}, XP: {score['xp']}")

if __name__ == "__main__":
    # For Windows, set console to utf-8
    if os.name == 'nt':
        os.system('chcp 65001')
        os.system('cls')
    game = Game()
    game.setup_game()
    game.main_loop()
