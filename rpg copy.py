#!/usr/bin/env python
import random
import os

class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.xp = 0
        self.level = 1
        self.x = 0
        self.y = 0

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def gain_xp(self, xp):
        self.xp += xp
        if self.xp >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack += 5
        self.defense += 2
        self.xp = 0
        print(f"\n{self.name} leveled up to level {self.level}! Stats increased.")

class Monster:
    def __init__(self, name, hp, attack, defense, xp):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.xp = xp

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

class Game:
    def __init__(self):
        self.player = None
        self.map_size = 10
        self.game_map = [['.' for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.monsters = [
            Monster("Goblin", 30, 8, 2, 50),
            Monster("Orc", 50, 12, 4, 100),
            Monster("Dragon", 200, 25, 10, 500)
        ]
        self.boss = self.monsters[-1]
        self.game_over = False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_map(self):
        for y in range(self.map_size):
            for x in range(self.map_size):
                if self.player.x == x and self.player.y == y:
                    print('P', end=' ')
                else:
                    print(self.game_map[y][x], end=' ')
            print()

    def print_status(self):
        print(f"\n{self.player.name} | Level: {self.player.level} | HP: {self.player.hp}/{self.player.max_hp} | XP: {self.player.xp}/{self.player.level * 100}")

    def start(self):
        self.clear_screen()
        player_name = input("Enter your hero's name: ")
        self.player = Player(player_name)
        self.game_map[self.map_size - 1][self.map_size - 1] = 'B' # Boss
        self.main_loop()

    def main_loop(self):
        while not self.game_over:
            self.clear_screen()
            self.print_map()
            self.print_status()
            action = input("\nMove (w/a/s/d) or quit (q): ").lower()

            if action == 'q':
                self.game_over = True
                continue

            if action in ['w', 'a', 's', 'd']:
                self.move_player(action)
            else:
                print("Invalid action.")
                input("Press Enter to continue...")

            if self.player.x == self.map_size - 1 and self.player.y == self.map_size - 1:
                self.start_combat(self.boss)
            elif random.random() < 0.2: # 20% chance of random encounter
                monster = random.choice(self.monsters[:-1])
                self.start_combat(Monster(monster.name, monster.hp, monster.attack, monster.defense, monster.xp))


    def move_player(self, direction):
        if direction == 'w' and self.player.y > 0:
            self.player.y -= 1
        elif direction == 's' and self.player.y < self.map_size - 1:
            self.player.y += 1
        elif direction == 'a' and self.player.x > 0:
            self.player.x -= 1
        elif direction == 'd' and self.player.x < self.map_size - 1:
            self.player.x += 1

    def start_combat(self, monster):
        self.clear_screen()
        print(f"A wild {monster.name} appears!")
        input("Press Enter to begin combat...")

        while self.player.is_alive() and monster.is_alive():
            self.clear_screen()
            print(f"{self.player.name} HP: {self.player.hp}/{self.player.max_hp}")
            print(f"{monster.name} HP: {monster.hp}")
            print("\n1. Attack")
            print("2. Run")
            action = input("Choose your action: ")

            if action == '1':
                player_damage = max(0, self.player.attack - monster.defense)
                monster.take_damage(player_damage)
                print(f"You hit the {monster.name} for {player_damage} damage.")

                if monster.is_alive():
                    monster_damage = max(0, monster.attack - self.player.defense)
                    self.player.take_damage(monster_damage)
                    print(f"The {monster.name} hits you for {monster_damage} damage.")
                input("Press Enter to continue...")
            elif action == '2':
                if random.random() < 0.5:
                    print("You successfully ran away!")
                    input("Press Enter to continue...")
                    return
                else:
                    print("You failed to run away!")
                    monster_damage = max(0, monster.attack - self.player.defense)
                    self.player.take_damage(monster_damage)
                    print(f"The {monster.name} hits you for {monster_damage} damage.")
                    input("Press Enter to continue...")

        if self.player.is_alive():
            print(f"You defeated the {monster.name}!")
            self.player.gain_xp(monster.xp)
            if monster == self.boss:
                print("\nCongratulations! You have defeated the final boss and won the game!")
                self.game_over = True
        else:
            print("You have been defeated. Game Over.")
            self.game_over = True
        input("Press Enter to continue...")


if __name__ == "__main__":
    game = Game()
    game.start()
