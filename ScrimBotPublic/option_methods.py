import discord
from discord.ext import commands, tasks
import random

class Pick_One:
    def __init__(self, name, choices : list):
        self.name = name
        self.choices = choices

class Side:
    def __init__(self, name, choices : list):
        self.name = name
        self.choices = choices