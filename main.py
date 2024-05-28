# THIS USES PYCORD, NOT DISCORD.PY

import discord
from discord.ext import commands
from discord.ui import Button, View
import requests

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("ready")

# function to get question

def get_trivia(type1):
    if type1 == "Multiple":
        type1 = "&type=multiple"
    elif type1 == "True or False":
        type1 = "&type=boolean"
    else:
        type1 = ""
    response = requests.get(f"https://opentdb.com/api.php?amount=1{type1}")
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]
    return None

# classes to add buttons

class TriviaBoolean(View):
    def __init__(self, correct_answer, command_user_id):
        super().__init__(timeout=30)
        self.correct_answer = correct_answer
        self.command_user_id = command_user_id
        self.result = None
        
    async def stopbutton(self, interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="True", style=discord.ButtonStyle.green)
    async def true_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id == self.command_user_id:
            if self.correct_answer.lower() == 'true':
                await interaction.response.send_message("That's the correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message("Sadly, it's incorrect.", ephemeral=True)
            self.result = True
            await self.stopbutton(interaction)
        else:
            await interaction.response.send_message("This command was sent from another user, so you cannot play.", ephemeral=True)
            
    @discord.ui.button(label="False", style=discord.ButtonStyle.red)
    async def false_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id == self.command_user_id:
            if self.correct_answer.lower() == 'false':
                await interaction.response.send_message("That's the correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message("Sadly, it's incorrect.", ephemeral=True)
            self.result = True
            await self.stopbutton(interaction)
        else:
            await interaction.response.send_message("This command was sent from another user, so you cannot play.", ephemeral=True)
            
class TriviaMultiple(View):
    def __init__(self, correct_answer, command_user_id, answers):
        super().__init__(timeout=30)
        self.correct_answer = correct_answer
        self.command_user_id = command_user_id
        self.answers = answers
        self.result = None
        self.create_buttons()
        
    async def stopbutton(self, interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        
    async def handle_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.command_user_id:
            if button.label == self.correct_answer:
                await interaction.response.send_message("That's the correct answer!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Sadly, it's incorrect. The correct answer was {self.correct_answer}.", ephemeral=True)
            self.result = True
            await self.stopbutton(interaction)
        else:
            await interaction.response.send_message("This command was sent from another user, so you cannot play.", ephemeral=True)
            
    def create_buttons(self):
        for answer in self.answers:
            button = discord.ui.Button(label=answer, style=discord.ButtonStyle.blurple)
            button.callback = lambda interaction, button=button: self.handle_button_click(interaction, button)
            self.add_item(button)

# the command itself

@bot.slash_command(name="trivia", description="Answer a True or False question.")
async def trivia(ctx, question_type: discord.Option(str, "Choose the trivia type", choices=["Multiple", "True or False", "Random"])):
    data = get_trivia(question_type)
    if not data:
        await ctx.respond("Failed to fetch trivia question. Please try again.")
        return
    
    questiontype = data['type']
    question = html.unescape(data['question'])
    correct_answer = data['correct_answer']
    difficulty = data['difficulty']
    category = data['category']
    
    if questiontype == "boolean":
        view = TriviaBoolean(correct_answer, ctx.author.id)
    else:
        incorrect_answers = data['incorrect_answers']
        answers = incorrect_answers + [correct_answer]
        random.shuffle(answers)
        view = TriviaMultiple(correct_answer, ctx.author.id, answers)
        
    embed = discord.Embed(title="Trivia", description=f"## {question}\nDifficulty: {difficulty}\nCategory: {category}", colour=0x2b2d31)
    await ctx.respond(embed=embed, view=view)

bot.run("token")
