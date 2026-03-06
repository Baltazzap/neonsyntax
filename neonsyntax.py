import discord
from discord.ext import commands
from discord import Permissions
from discord.ui import Button, View
import os
from dotenv import load_dotenv
import random
import asyncio

# Загрузка переменных окружения из .env файла
load_dotenv()

# --- НАСТРОЙКИ ---
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("❌ Error: DISCORD_TOKEN not found in environment variables!")
    print("💡 Please create a .env file with DISCORD_TOKEN=your_token_here")
    exit(1)

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True

bot = commands.Bot(command_prefix='!', intents=INTENTS, help_command=None)

# --- ID КАНАЛОВ ---
CHANNEL_IDS = {
    "rules": "1479178350823211068",
    "roles": "1479178355701186695",
    "general": "1479178361535201513",
    "lfg-pve": "1479178383601434675"
}

# --- ID АВТО-РОЛИ ---
AUTO_ROLE_ID = 1479178344976089179

# --- ID РОЛЕЙ ДЛЯ САМОВЫДАЧИ ---
SELF_ASSIGNABLE_ROLES = {
    "PC": {"id": 1479178336755388448, "emoji": "🖥️", "label": "PC Gamer", "desc": "Play on PC (Steam/Ubisoft)"},
    "PlayStation": {"id": 1479178337732792632, "emoji": "🎮", "label": "PlayStation", "desc": "Play on PS4/PS5"},
    "Xbox": {"id": 1479178338819117207, "emoji": "🕹️", "label": "Xbox", "desc": "Play on Xbox One/Series"},
    "PvE-Hardcore": {"id": 1479178339884204032, "emoji": "⚔️", "label": "PvE Hardcore", "desc": "Raids, Heroic, Optimized builds"},
    "PvE-Casual": {"id": 1479178340941172737, "emoji": "🌿", "label": "PvE Casual", "desc": "Missions, Farming, relaxed gameplay"},
    "BattlePass-Grind": {"id": 1479178342069571787, "emoji": "🏆", "label": "BattlePass Grind", "desc": "Focus on Battle Pass progression"},
    "Ping-Events": {"id": 1479178342572884099, "emoji": "📢", "label": "Ping Events", "desc": "Get notified about clan events"},
    "Ping-LFG": {"id": 1479178343885836562, "emoji": "🔍", "label": "Ping LFG", "desc": "Get notified about group finding"}
}

# --- ЦВЕТА РОЛЕЙ ---
ROLE_COLORS = {
    "Leader": 0xFF6B35,
    "Officer": 0xFFD700,
    "Veteran": 0xC0C0C0,
    "Raid-Leader": 0xE74C3C,
    "PC": 0x3498DB,
    "PlayStation": 0x0070D1,
    "Xbox": 0x107C10,
    "PvE-Hardcore": 0x8E44AD,
    "PvE-Casual": 0x27AE60,
    "BattlePass-Grind": 0xF1C40F,
    "Ping-Events": 0xE91E63,
    "Ping-LFG": 0x1ABC9C,
    "New-Agent": 0x7F8C8D,
    "Muted": 0x2C3E50
}

# --- БАЗА ДАННЫХ ЭКЗОТИКОВ ---
EXOTICS_DB = [
    {"name": "Merciless & Ruthless", "type": "Rifle & Pistol", "talent": "The Show Must Go On", "location": "Invaded District Union Arena", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/0/02/Merciless.png"},
    {"name": "Chatterbox", "type": "SMG", "talent": "Unhinged", "location": "Invaded Bank Headquarters", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/9/9a/Chatterbox.png"},
    {"name": "Lady Death", "type": "SMG", "talent": "Obliterate", "location": "Invaded Tidal Basin", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/1/1a/Lady_Death.png"},
    {"name": "Pestilence", "type": "Assault Rifle", "talent": "Plague", "location": "Invaded Capitol Building", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/8/8a/Pestilence.png"},
    {"name": "Nemesis", "type": "Sniper Rifle", "talent": "Perfect Unwavering", "location": "Invaded Potomac Event Center", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/5/5a/Nemesis.png"},
    {"name": "Dodge City Gunslinger", "type": "Holster", "talent": "Fan the Hammer", "location": "Invaded Manning National Zoo", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/3/3a/Dodge_City.png"},
    {"name": "Heartbreaker", "type": "LMG", "talent": "Perfect Sledgehammer", "location": "Iron Horse Raid", "difficulty": "Raid", "image": "https://static.wikia.nocookie.net/thedivision/images/6/6a/Heartbreaker.png"},
    {"name": "Paradox", "type": "Assault Rifle", "talent": "Perfect Time Dilation", "location": "Manhunt Targets", "difficulty": "Heroic", "image": "https://static.wikia.nocookie.net/thedivision/images/7/7a/Paradox.png"}
]

# --- БАЗА ДАННЫХ МЕМОВ ---
MEME_URLS = [
    "https://i.imgur.com/sAnFJ4c.png",
    "https://i.imgur.com/DivisionMeme1.png",
    "https://i.imgur.com/DivisionMeme2.png"
]

# --- КОМПЛИМЕНТЫ ---
COMPLIMENTS = [
    "You're an amazing agent! 🧡",
    "Your gameplay is legendary! 🏆",
    "You make the team better! 🎯",
    "Your positivity is contagious! ✨",
    "You're a true Division veteran! 🎖️",
    "Your skills are unmatched! ⚔️",
    "You're the MVP of this clan! 🌟",
    "Your dedication inspires us all! 💪",
    "You're a fantastic teammate! 🤝",
    "Your builds are genius! 🧠"
]

# --- ЗАПРЕЩЁННЫЕ СЛОВА ---
FORBIDDEN_WORDS = [
    "scam", "hack", "cheat", "glitch", "exploit",
    "toxic", "hate", "spam", "nsfw"
]

# --- ВОПРОСЫ ДЛЯ ВИКТОРИНЫ ---
TRIVIA_QUESTIONS = [
    {"question": "What is the name of the AI system used by Division agents?", "options": ["ISAC", "JTF", "SHD", "BTSU"], "answer": 0},
    {"question": "Which faction controls the White House at the start of Division 2?", "options": ["Hyenas", "Outcasts", "True Sons", "Black Tusk"], "answer": 2},
    {"question": "What is the max Gear Score in Warlords of New York?", "options": ["450", "500", "515", "600"], "answer": 2},
    {"question": "Which exotic SMG has the 'Obliterate' talent?", "options": ["Chatterbox", "Lady Death", "Tommy Gun", "Vector"], "answer": 1},
    {"question": "What year was The Division 2 released?", "options": ["2017", "2018", "2019", "2020"], "answer": 2},
    {"question": "Which raid was added in Title Update 8?", "options": ["Dark Hours", "Iron Horse", "Summit", "Countdown"], "answer": 0},
    {"question": "What is the name of the Division's watch?", "options": ["Smart Watch", "SHD Watch", "Agent Watch", "Tactical Watch"], "answer": 1},
    {"question": "Which specialisation uses the Crossbow?", "options": ["Demolitionist", "Survivalist", "Gunner", "Technician"], "answer": 1}
]

# --- СИСТЕМА ОЧКОВ ВИКТОРИНЫ ---
trivia_scores = {}
active_trivia = None

# --- СТРУКТУРА КАНАЛОВ ---
CATEGORIES = {
    "🏠 WELCOME & INFO": [
        ("👋・welcome", "text"),
        ("📜・rules", "text"),
        ("📢・announcements", "text"),
        ("🎁・roles", "text"),
        ("🔗・useful-links", "text")
    ],
    "💬 GENERAL CHAT": [
        ("💬・general", "text"),
        ("🎮・gaming-chat", "text"),
        ("📸・screenshots", "text"),
        ("🤖・bot-commands", "text"),
        ("💡・suggestions", "text")
    ],
    "🎯 THE DIVISION 2: GAME HUB": [
        ("📰・td2-news", "text"),
        ("⚙️・builds-theory", "text"),
        ("🗺️・missions-help", "text"),
        ("👾・boss-strats", "text"),
        ("🛠️・tech-support", "text")
    ],
    "🔍 LFG / ACTIVITIES": [
        ("🔍・lfg-pve", "text"),
        ("🔥・lfg-raids", "text"),
        ("🏆・lfg-battlepass", "text"),
        ("🕐・scheduled-runs", "text"),
        ("🌍・lfg-global", "text")
    ],
    "🔊 VOICE CHANNELS": [
        ("🔊・Lobby", "voice"),
        ("🔊・Squad-1", "voice"),
        ("🔊・Squad-2", "voice"),
        ("🔊・Raid-Command", "voice"),
        ("🔊・AFK / Chill", "voice")
    ],
    "🛠️ STAFF & ADMIN": [
        ("🔐・staff-chat", "text"),
        ("📋・applications", "text"),
        ("🗑️・mod-logs", "text"),
        ("⚙️・server-setup", "text")
    ]
}

# ============================================
# ✅ КЛАСС ДЛЯ КНОПОК ЭКЗОТИКОВ (ИСПРАВЛЕНО)
# ============================================
class ExoticSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)  # ✅ No timeout for persistent view
    
    @discord.ui.button(label="🎲 Random Exotic", style=discord.ButtonStyle.blurple, emoji="🎲", custom_id="exotic_random")  # ✅ custom_id added
    async def random_exotic(self, interaction: discord.Interaction, button: Button):
        exotic = random.choice(EXOTICS_DB)
        embed = discord.Embed(title=f"🎲 Random Exotic: {exotic['name']}", description=f"**Type:** {exotic['type']}\n**Talent:** `{exotic['talent']}`", color=0xFFD700)
        embed.add_field(name="📍 Drop Location", value=exotic['location'], inline=False)
        embed.add_field(name="⚠️ Difficulty", value=exotic['difficulty'], inline=False)
        embed.set_thumbnail(url=exotic['image'])
        embed.set_footer(text="CoopFamily • Good luck farming!", icon_url="https://i.imgur.com/sAnFJ4c.png")
        await interaction.response.edit_message(embed=embed, view=ExoticSelectView())
    
    @discord.ui.button(label="📋 All Exotics", style=discord.ButtonStyle.gray, emoji="📋", custom_id="exotic_all")  # ✅ custom_id added
    async def all_exotics(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(title="📋 All Exotics List", description="Here are all available exotic weapons and gear", color=0xFFD700)
        for i, exotic in enumerate(EXOTICS_DB, 1):
            embed.add_field(name=f"{i}. {exotic['name']}", value=f"**Type:** {exotic['type']}\n**Location:** {exotic['location']}", inline=False)
        embed.set_footer(text="CoopFamily • Use !exotics <name> for details", icon_url="https://i.imgur.com/sAnFJ4c.png")
        await interaction.response.edit_message(embed=embed, view=ExoticSelectView())

# ============================================
# ✅ КЛАСС ДЛЯ КНОПОК РОЛЕЙ (ИСПРАВЛЕНО)
# ============================================
class RoleSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)  # ✅ No timeout for persistent view
        for role_key, role_data in SELF_ASSIGNABLE_ROLES.items():
            emoji = role_data["emoji"]
            style = discord.ButtonStyle.blurple if role_key in ["PC", "PlayStation", "Xbox"] else discord.ButtonStyle.green if role_key in ["Ping-Events", "Ping-LFG"] else discord.ButtonStyle.gray
            # ✅ custom_id added for each button
            self.add_item(RoleButton(role_key, role_data["id"], emoji, style, custom_id=f"role_{role_key}"))

class RoleButton(Button):
    def __init__(self, role_key, role_id, emoji, style, custom_id):
        super().__init__(style=style, label=role_key, emoji=emoji, custom_id=custom_id)  # ✅ custom_id passed
        self.role_key = role_key
        self.role_id = role_id
    
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed <@&{self.role_id}>!", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Added <@&{self.role_id}>!", ephemeral=True)

# ============================================
# ✅ КЛАСС ДЛЯ КНОПОК ВИКТОРИНЫ
# ============================================
class TriviaView(View):
    def __init__(self, correct_answer: int, question_data: dict):
        super().__init__(timeout=30)  # ⚠️ Has timeout, so NOT persistent (don't add to bot.add_view)
        self.correct_answer = correct_answer
        self.question_data = question_data
        self.answered = False
    
    @discord.ui.button(label="A", style=discord.ButtonStyle.blurple, custom_id="trivia_a")
    async def option_a(self, interaction: discord.Interaction, button: Button):
        await self.check_answer(interaction, 0)
    
    @discord.ui.button(label="B", style=discord.ButtonStyle.blurple, custom_id="trivia_b")
    async def option_b(self, interaction: discord.Interaction, button: Button):
        await self.check_answer(interaction, 1)
    
    @discord.ui.button(label="C", style=discord.ButtonStyle.blurple, custom_id="trivia_c")
    async def option_c(self, interaction: discord.Interaction, button: Button):
        await self.check_answer(interaction, 2)
    
    @discord.ui.button(label="D", style=discord.ButtonStyle.blurple, custom_id="trivia_d")
    async def option_d(self, interaction: discord.Interaction, button: Button):
        await self.check_answer(interaction, 3)
    
    async def check_answer(self, interaction: discord.Interaction, answer: int):
        if self.answered:
            await interaction.response.send_message("⏰ Already answered!", ephemeral=True)
            return
        
        self.answered = True
        user = interaction.user
        
        if answer == self.correct_answer:
            trivia_scores[user.id] = trivia_scores.get(user.id, 0) + 10
            await interaction.response.send_message(f"✅ **Correct!** +10 points, {user.name}!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ **Wrong!** The answer was {chr(65 + self.correct_answer)}.", ephemeral=True)
        
        for child in self.children:
            child.disabled = True
        await interaction.edit_original_response(view=self)

# --- СОБЫТИЯ ---
@bot.event
async def on_ready():
    print(f'✅ Bot Online: {bot.user.name}')
    print(f'🔗 Server ID: {bot.guilds[0].id if bot.guilds else "N/A"}')
    await bot.change_presence(activity=discord.Game(name="The Division 2 | !help"))
    # ✅ Register persistent views (only those with timeout=None and custom_id)
    bot.add_view(RoleSelectView())
    bot.add_view(ExoticSelectView())

@bot.event
async def on_member_join(member):
    try:
        auto_role = member.guild.get_role(AUTO_ROLE_ID)
        if auto_role:
            await member.add_roles(auto_role)
            try:
                await member.send(f"🧡 **Welcome to CoopFamily, {member.name}!**\n\n📋 **Next steps:**\n• Read rules in <#{CHANNEL_IDS['rules']}>\n• Get your roles in <#{CHANNEL_IDS['roles']}>\n• Introduce yourself in <#{CHANNEL_IDS['general']}>")
            except discord.Forbidden:
                pass
    except Exception as e:
        print(f"❌ Error assigning auto-role: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await auto_moderate(message)
    await bot.process_commands(message)

# --- АВТО-МОДЕРАЦИЯ ---
async def auto_moderate(message):
    if message.author.guild_permissions.administrator:
        return
    
    content = message.content
    
    # 1. Блокировка инвайтов Discord
    if "discord.gg/" in content.lower() or "discord.com/invite" in content.lower():
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, Discord invites are not allowed!", delete_after=5)
        return
    
    # 2. Блокировка спама ссылок (более 3 ссылок)
    link_count = content.count("http://") + content.count("https://")
    if link_count > 3:
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, Too many links!", delete_after=5)
        return
    
    # 3. Блокировка КАПСА (более 70% заглавных)
    if len(content) > 10:
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
        if caps_ratio > 0.7:
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, Please don't use all caps!", delete_after=5)
            return
    
    # 4. Блокировка запрещённых слов
    for word in FORBIDDEN_WORDS:
        if word in content.lower():
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, That word is not allowed!", delete_after=5)
            return

# --- КОМАНДЫ ---

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    guild = ctx.guild
    await ctx.send("🚀 **Starting CoopFamily Server Setup...**")
    created_roles = {}
    for role_name, color in ROLE_COLORS.items():
        try:
            role = await guild.create_role(name=role_name, color=discord.Color(color), reason="CoopFamily Setup")
            created_roles[role_name] = role
        except Exception as e:
            print(f"❌ Error creating role {role_name}: {e}")
    await ctx.send(f"🎨 **Created {len(created_roles)} roles.**")
    for cat_name, channels in CATEGORIES.items():
        try:
            category = await guild.create_category_channel(cat_name)
            if "STAFF" in cat_name:
                await category.set_permissions(guild.default_role, view_channel=False)
            for ch_name, ch_type in channels:
                if ch_type == "text":
                    await guild.create_text_channel(ch_name, category=category)
                elif ch_type == "voice":
                    await guild.create_voice_channel(ch_name, category=category)
        except Exception as e:
            print(f"❌ Error in category {cat_name}: {e}")
    await ctx.send("✅ **Server Setup Complete!**")

@bot.command(name='welcome')
@commands.has_permissions(manage_messages=True)
async def send_welcome(ctx):
    embed = discord.Embed(title="🧡 Welcome to CoopFamily", description='"United We Stand, Divided We Fall" — Our motto in Washington.', color=0xFF6B35)
    embed.add_field(name="🎯 What to Expect?", value="• 🤝 Friendly PvE Community\n• 🔍 24/7 LFG for Missions & Farming\n• 📚 Guides, Builds & Newbie Help\n• 🏆 Joint Battlepass & Exotic Farming\n• 🎙️ Active Voice Chats", inline=False)
    embed.add_field(name="📋 First Steps:", value=f"1️⃣ Read rules in <#{CHANNEL_IDS['rules']}>\n2️⃣ Pick your platform in <#{CHANNEL_IDS['roles']}>\n3️⃣ Introduce yourself in <#{CHANNEL_IDS['general']}>\n4️⃣ Find a group in <#{CHANNEL_IDS['lfg-pve']}>", inline=False)
    embed.set_footer(text="CoopFamily • SHD Network Active", icon_url="https://i.imgur.com/sAnFJ4c.png")
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command(name='rules')
@commands.has_permissions(manage_messages=True)
async def send_rules(ctx):
    embed = discord.Embed(title="📜 CoopFamily Server Rules", description='"With great power comes great responsibility"', color=0xFF6B35)
    embed.add_field(name="🛡️ General Conduct", value="1️⃣ **Be Respectful**\n2️⃣ **No Toxicity**\n3️⃣ **English Only**\n4️⃣ **No Spam**\n5️⃣ **No NSFW**", inline=False)
    embed.add_field(name="🎮 Division 2 Rules", value="6️⃣ **PvE Focus**\n7️⃣ **No Cheating**\n8️⃣ **Share Loot**\n9️⃣ **Use Mic for Raids**\n🔟 **Help New Agents**", inline=False)
    embed.set_footer(text="CoopFamily • By joining, you agree", icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed)

@bot.command(name='roles')
@commands.has_permissions(manage_messages=True)
async def send_roles(ctx):
    embed = discord.Embed(title="🎁 Select Your Roles", description="Click buttons to get roles!", color=0x3498DB)
    for key in ["PC", "PlayStation", "Xbox"]:
        role_data = SELF_ASSIGNABLE_ROLES[key]
        embed.add_field(name="🎮 Platforms", value=f"{role_data['emoji']} <@&{role_data['id']}>", inline=False)
        break
    embed.set_footer(text="CoopFamily • Self-assign roles", icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed, view=RoleSelectView())

@bot.command(name='exotics')
@commands.has_permissions(manage_messages=True)
async def send_exotics(ctx, *, exotic_name: str = None):
    if exotic_name:
        found = next((e for e in EXOTICS_DB if exotic_name.lower() in e['name'].lower()), None)
        if found:
            embed = discord.Embed(title=f"🎯 Exotic: {found['name']}", description=f"**Type:** {found['type']}\n**Talent:** `{found['talent']}`", color=0xFFD700)
            embed.add_field(name="📍 Location", value=found['location'], inline=False)
            embed.set_thumbnail(url=found['image'])
            await ctx.send(embed=embed, view=ExoticSelectView())
        else:
            await ctx.send(f"❌ Exotic not found!")
    else:
        embed = discord.Embed(title="🎯 Exotic Weapons & Gear", color=0xFFD700)
        for i, exotic in enumerate(random.sample(EXOTICS_DB, 5), 1):
            embed.add_field(name=f"{i}. {exotic['name']}", value=f"**Type:** {exotic['type']}", inline=False)
        await ctx.send(embed=embed, view=ExoticSelectView())

@bot.command(name='meme')
async def send_meme(ctx):
    meme_url = random.choice(MEME_URLS)
    embed = discord.Embed(title="🎭 Random Division Meme", color=0xE91E63)
    embed.set_image(url=meme_url)
    embed.set_footer(text="CoopFamily • Stay positive!", icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed)

@bot.command(name='compliment')
async def send_compliment(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    compliment = random.choice(COMPLIMENTS)
    embed = discord.Embed(title="💝 Compliment!", description=f"{member.mention}, {compliment}", color=0xE91E63)
    embed.set_footer(text="CoopFamily • Spread positivity!", icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed)

@bot.command(name='trivia')
async def start_trivia(ctx):
    global active_trivia
    
    if active_trivia:
        await ctx.send("⏰ A trivia question is already active!")
        return
    
    question_data = random.choice(TRIVIA_QUESTIONS)
    active_trivia = question_data
    
    embed = discord.Embed(
        title="🧠 Division 2 Trivia!",
        description=f"**{question_data['question']}**\n\n"
                    f"🅰️ {question_data['options'][0]}\n"
                    f"🅱️ {question_data['options'][1]}\n"
                    f"🅾️ {question_data['options'][2]}\n"
                    f"🇩️ {question_data['options'][3]}",
        color=0x9B59B6
    )
    embed.add_field(name="⏱️ Time Limit", value="30 seconds", inline=False)
    embed.add_field(name="🏆 Prize", value="10 points per correct answer", inline=False)
    embed.set_footer(text="CoopFamily Trivia • Use buttons to answer!", icon_url="https://i.imgur.com/sAnFJ4c.png")
    
    await ctx.send(embed=embed, view=TriviaView(question_data['answer'], question_data))
    
    await asyncio.sleep(30)
    active_trivia = None

@bot.command(name='trivia-leaderboard')
async def trivia_leaderboard(ctx):
    if not trivia_scores:
        await ctx.send("📊 No trivia scores yet! Start with `!trivia`")
        return
    
    sorted_scores = sorted(trivia_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 Trivia Leaderboard", description="Top 10 trivia champions!", color=0xFFD700)
    
    for i, (user_id, score) in enumerate(sorted_scores, 1):
        user = await bot.fetch_user(user_id)
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        embed.add_field(name=f"{medal} {user.name}", value=f"**{score} points**", inline=False)
    
    embed.set_footer(text="CoopFamily Trivia • Keep playing!", icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="🤖 CoopFamily Bot Commands", description="Here are all available commands!", color=0x3498DB)
    embed.add_field(name="🎮 The Division 2", value="`!exotics` — Exotic info\n`!exotics <name>` — Search exotic\n`!meme` — Random meme\n`!trivia` — Start trivia\n`!trivia-leaderboard` — Show scores", inline=False)
    embed.add_field(name="💝 Community", value="`!compliment @user` — Give compliment", inline=False)
    embed.add_field(name="🏓 Utilities", value="`!help` — Show this menu\n`!ping` — Check latency", inline=False)
    embed.set_footer(text="CoopFamily Bot v1.8", icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Bot latency: **{latency}ms**", color=0x2ECC71)
    embed.set_footer(icon_url="https://i.imgur.com/sAnFJ4c.png")
    await ctx.send(embed=embed)

# --- ОБРАБОТКА ОШИБОК ---
@setup_server.error
async def setup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Administrator permissions required!")

@send_welcome.error
@send_rules.error
@send_roles.error
@send_exotics.error
async def perm_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Manage Messages permissions required!")

# --- ЗАПУСК ---
if __name__ == "__main__":
    try:
        print("🚀 Starting CoopFamily Bot v1.8...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid token!")
    except Exception as e:
        print(f"❌ Error: {e}")
