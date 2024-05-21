import random

import attack
import character

class DiceRoller:
    def get_roll(self, dice, count):
        return [random.randint(1, dice) for i in range(count)]
    
    def get_roll_character(self, character, parameter):
        roll = random.randint(1, 20)
        return roll + character.modificators_.get(parameter, 0)
    
    def get_roll_damage(self, character, attack):
        roll = sum(self.get_roll(attack.dice_, attack.count_))
        return roll + character.modificators_.get(attack.modificator_, 0)

class AdvantageDiceRoller(DiceRoller):
    def get_roll(self, dice, count):
        rolls = [max(random.randint(1, dice), random.randint(1, dice)) for i in range(count)]
        return rolls

    def get_roll_character(self, character, parameter):
        roll = max(random.randint(1, 20), random.randint(1, 20))
        return roll + character.modificators_.get(parameter, 0)
    
    def get_roll_damage(self, character, attack):
        roll = sum(self.get_roll(attack.dice_, attack.count_))
        return roll + character.modificators_.get(attack.modificator_, 0)

class DisadvantageDiceRoller(DiceRoller):
    def get_roll(self, dice, count):
        rolls = [min(random.randint(1, dice), random.randint(1, dice)) for i in range(count)]
        return rolls

    def get_roll_character(self, character, parameter):
        roll = min(random.randint(1, 20), random.randint(1, 20))
        return roll + character.modificators_.get(parameter, 0)
    
    def get_roll_damage(self, character, attack):
        roll = sum(self.get_roll(attack.dice_, attack.count_))
        return roll + character.modificators_.get(attack.modificator_, 0)
