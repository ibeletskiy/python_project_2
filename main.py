import telebot
import sqlite3
from telebot import types

import config
from db import DataBase
from dice_roller import AdvantageDiceRoller
from dice_roller import DiceRoller
from dice_roller import DisadvantageDiceRoller

bot = telebot.TeleBot(config.API_TOKEN)

db = DataBase()

commands = {
    'start': 'Start interacting with the bot and register your user.',
    'help': 'Show all available commands and instructions.',
    'add_character': 'Add a new character.',
    'set_modificator': 'Set a modificator for a character.',
    'add_attack': 'Add an attack to a character.',
    'roll': 'Roll dice with certain amount of edges count times. Format: roll dice count',
    'roll_character': 'Roll dice for a character parameter. Format: roll character parameter',
    'roll_attack': 'Roll dice for an attack. Format: roll character attack',
    'list_characters': 'List all your characters.',
    'list_attacks': 'List all attacks for a given character.',
    'set_dice_roller': 'Set your dice roller.'
}

@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    db.add_user(username)
    bot.reply_to(message, "Welcome to DnD Dice Roller Bot! Use /addcharacter to add your character. Use /help to see all commands.")

@bot.message_handler(commands=['help'])
def help(message):
    help_text = "Available commands:\n"
    for command, description in commands.items():
        help_text += f"/{command} - {description}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['set_dice_roller'])
def set_dice_roller(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    rollers = ['Normal', 'Advantage', 'Disadvantage']
    for roller in rollers:
        markup.add(types.KeyboardButton(roller))
    bot.reply_to(message, "Choose your dice roller type:", reply_markup=markup)
    bot.register_next_step_handler(message, process_roller_choice)
 
def process_roller_choice(message):
    roller_types = {'Normal', 'Advantage', 'Disadvantage'}
    roller_choice = message.text
    if roller_choice in roller_types:
        username = message.from_user.username
        db.set_dice_roller(username, roller_choice.lower())
        bot.reply_to(message, f"Dice roller set to {roller_choice}.")
    else:
        bot.reply_to(message, "Invalid dice roller type. Please choose from Normal, Advantage, Disadvantage.")

@bot.message_handler(commands=['add_character'])
def add_character(message):
    bot.reply_to(message, "Please provide character details in the format: name class")
    bot.register_next_step_handler(message, process_character_step)

def process_character_step(message):
    try:
        name, class_ = message.text.split()
        username = message.from_user.username
        db.add_character(name, class_, username)
        bot.reply_to(message, f"Character {name} added!")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")

@bot.message_handler(commands=['set_modificator'])
def set_modificator(message):
    bot.reply_to(message, "Please provide modificator details in the format: character_name parameter value")
    bot.register_next_step_handler(message, process_modificator_step)

def process_modificator_step(message):
    try:
        name, parameter, value = message.text.split()
        value = int(value)
        db.set_modificator(name, parameter, value)
        bot.reply_to(message, f"Modificator {parameter} for character {name} set to {value}!")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")

@bot.message_handler(commands=['add_attack'])
def add_attack(message):
    bot.reply_to(message, "Please provide attack details in the format: character_name attack_name dice count modificator")
    bot.register_next_step_handler(message, process_attack_step)

def process_attack_step(message):
    try:
        name, attack_name, dice, count, modificator = message.text.split()
        dice = int(dice)
        count = int(count)
        username = message.from_user.username
        db.add_attack(name, attack_name, dice, count, modificator)
        bot.reply_to(message, f"Attack {attack_name} for character {name} added!")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")

@bot.message_handler(commands=['roll'])
def roll_dice(message):
    username = message.from_user.username
    roller_type = db.get_dice_roller(username)
 
    if roller_type == 'advantage':
        roller = AdvantageDiceRoller()
    elif roller_type == 'disadvantage':
        roller = DisadvantageDiceRoller()
    else:
        roller = DiceRoller()

    try:
        parts = message.text.split()
        dice = int(parts[1])
        count = int(parts[2])
        rolls = roller.get_roll(dice, count)
        bot.reply_to(message, f"Rolls: {rolls}")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")

@bot.message_handler(commands=['roll_character'])
def roll_dice_character(message):
    username = message.from_user.username
    roller_type = db.get_dice_roller(username)
 
    if roller_type == 'advantage':
        roller = AdvantageDiceRoller()
    elif roller_type == 'disadvantage':
        roller = DisadvantageDiceRoller()
    else:
        roller = DiceRoller()

    try:
        parts = message.text.split()
        character = db.get_character(parts[1])
        print('norm')
        parameter = parts[2]
        rolls = roller.get_roll_character(character, parameter)
        bot.reply_to(message, f"Rolls: {rolls}")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")

@bot.message_handler(commands=['roll_attack'])
def roll_dice_attack(message):
    username = message.from_user.username
    roller_type = db.get_dice_roller(username)
 
    if roller_type == 'advantage':
        roller = AdvantageDiceRoller()
    elif roller_type == 'disadvantage':
        roller = DisadvantageDiceRoller()
    else:
        roller = DiceRoller()

    try:
        parts = message.text.split()
        character = db.get_character(parts[1])
        attack = character.attacks_.get(parts[2])
        rolls = roller.get_roll_damage(character, attack)
        bot.reply_to(message, f"Rolls: {rolls}")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")


@bot.message_handler(commands=['list_characters'])
def list_characters(message):
    username = message.from_user.username
    characters = db.list_characters(username)
    if characters:
        response = "Characters:\n"
        for char in characters:
            response += f"Name: {char[0]}, Class: {char[1]}\n"
    else:
        response = "No characters found."

    bot.reply_to(message, response)

@bot.message_handler(commands=['list_attacks'])
def list_attacks(message):
    bot.reply_to(message, "Please provide the character name.")
    bot.register_next_step_handler(message, process_list_attacks_step)

def process_list_attacks_step(message):
    try:
        name = message.text
        username = message.from_user.username
        attacks = db.list_attacks(name, username)

        if attacks:
            response = f"Attacks for {name}:\n"
            for attack in attacks:
                response += f"Name: {attack[0]}, Dice: {attack[1]}, Count: {attack[2]}, Modificator: {attack[3]}\n"
        else:
            response = f"No attacks found for character {name} or no such character."

        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please make sure you provided the details in the correct format.")

@bot.inline_handler(lambda query: query.query.startswith('/'))
def query_text(inline_query):
    text = inline_query.query[1:]
    matches = [f"/{command}" for command in commands if command.startswith(text)]
    results = []
    for match in matches:
        results.append(types.InlineQueryResultArticle(
            id=match,
            title=match,
            input_message_content=types.InputTextMessageContent(message_text=match)
        ))
    bot.answer_inline_query(inline_query.id, results)

bot.polling()