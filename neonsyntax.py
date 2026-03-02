# ============================================
# 🌆 NEONSYNTAX BOT - Discord Moderation Bot
# ============================================
# Version: 3.0.1
# Author: NeonSyntax Team
# Description: Полный код бота со всеми функциями
# ============================================

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput
from dotenv import load_dotenv
import asyncio
import datetime
import json
import os
import logging
from pathlib import Path
from typing import Optional

# ============================================
# 🔷 ПРОВЕРКА КОНФИГУРАЦИИ 🔷
# ============================================

print("🔍 Проверка конфигурации...")
print(f"DISCORD_TOKEN: {'✅' if DISCORD_TOKEN and len(DISCORD_TOKEN) > 50 else '❌'}")
print(f"GUILD_ID: {'✅' if GUILD_ID > 0 else '❌'} ({GUILD_ID})")
print(f"OWNER_ID: {'✅' if OWNER_ID > 0 else '❌'} ({OWNER_ID})")
print(f"WELCOME_CHANNEL: {'✅' if WELCOME_CHANNEL > 0 else '❌'}")
print(f"LOG_CHANNEL: {'✅' if LOG_CHANNEL > 0 else '❌'}")
print(f"AUTO_ROLE: {'✅' if AUTO_ROLE > 0 else '❌'}")
print(f"MUTE_ROLE: {'✅' if MUTE_ROLE > 0 else '❌'}")

if not TOKEN or len(TOKEN) < 50:
    print("❌ ОШИБКА: Неверный токен бота!")
    exit(1)

if GUILD_ID == 0:
    print("❌ ОШИБКА: GUILD_ID не настроен!")
    exit(1)

# ============================================
# 🔷 ЗАГРУЗКА КОНФИГУРАЦИИ 🔷
# ============================================

load_dotenv()

# Основные настройки
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('1477952025034752070', 0))
OWNER_ID = int(os.getenv('314805583788244993', 0))
PREFIX = os.getenv('BOT_PREFIX', '/')

# ID каналов
WELCOME_CHANNEL = int(os.getenv('1477955639937466531', 0))
LOG_CHANNEL = int(os.getenv('1477964505546883184', 0))
TICKET_CHANNEL = int(os.getenv('1477956383520325754', 0))
STAFF_APP_CHANNEL = int(os.getenv('1477964570344685670', 0))
STATS_CHANNEL = int(os.getenv('1477964455555104768', 0))

# ID ролей
AUTO_ROLE = int(os.getenv('1477952294984224809', 0))
MUTE_ROLE = int(os.getenv('1477952295869349888', 0))
STAFF_ROLE = int(os.getenv('1477952291439902791', 0))
ADMIN_ROLE = int(os.getenv('1477952288076201984', 0))

# Настройки анти-спама
ANTI_SPAM_ENABLED = os.getenv('ANTI_SPAM_ENABLED', 'True').lower() == 'true'
ANTI_SPAM_MESSAGES = int(os.getenv('ANTI_SPAM_MESSAGES_COUNT', 5))
ANTI_SPAM_TIME = int(os.getenv('ANTI_SPAM_TIME_WINDOW', 10))
ANTI_SPAM_CAPS = int(os.getenv('ANTI_SPAM_CAPS_PERCENT', 70))

# Цвета
COLOR_MAIN = int(os.getenv('EMBED_COLOR_MAIN', 'FF00FF'), 16)
COLOR_SUCCESS = int(os.getenv('EMBED_COLOR_SUCCESS', '43b581'), 16)
COLOR_ERROR = int(os.getenv('EMBED_COLOR_ERROR', 'ed4245'), 16)
COLOR_WARNING = int(os.getenv('EMBED_COLOR_WARNING', 'faa61a'), 16)

# Пути
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / 'bot_data.json'

# ============================================
# 🔷 НАСТРОЙКА ЛОГИРОВАНИЯ 🔷
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('NeonSyntaxBot')

# ============================================
# 🔷 ИНИЦИАЛИЗАЦИЯ БОТА 🔷
# ============================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# ============================================
# 🔷 БАЗА ДАННЫХ 🔷
# ============================================

def load_data():
    """Загрузка данных из JSON"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'tickets': [],
        'staff_apps': [],
        'mutes': [],
        'warnings': []
    }

def save_data(data):
    """Сохранение данных в JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

# ============================================
# 🔷 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ 🔷
# ============================================

def get_log_channel(guild):
    return guild.get_channel(LOG_CHANNEL)

async def log_action(guild, action, user, target=None, reason=None):
    """Логирование действий"""
    channel = get_log_channel(guild)
    if not channel:
        return
    
    embed = discord.Embed(
        title=f"🔨 {action}",
        color=COLOR_ERROR,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="👤 Модератор", value=f"{user.mention} ({user.id})", inline=True)
    if target:
        embed.add_field(name="🎯 Цель", value=f"{target.mention} ({target.id})", inline=True)
    if reason:
        embed.add_field(name="📝 Причина", value=reason, inline=False)
    embed.set_footer(text=f"ID: {user.id}")
    
    try:
        await channel.send(embed=embed)
    except:
        pass

# ============================================
# 🔷 СОБЫТИЯ БОТА 🔷
# ============================================

@bot.event
async def on_ready():
    logger.info(f'✅ {bot.user} успешно запущен!')
    
    # Глобальная синхронизация (работает на всех серверах)
    try:
        synced = await bot.tree.sync()  # Без guild=
        logger.info(f"🔄 Синхронизировано {len(synced)} команд (глобально)")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

@bot.event
async def on_member_join(member):
    """Авто-приветствие и роль"""
    try:
        role = member.guild.get_role(AUTO_ROLE)
        if role:
            await member.add_roles(role)
        
        channel = member.guild.get_channel(WELCOME_CHANNEL)
        if channel:
            embed = discord.Embed(
                title="👋 Добро пожаловать!",
                description=f"{member.mention}, добро пожаловать на **{member.guild.name}**!",
                color=COLOR_SUCCESS,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="📅 Регистрация", value=member.created_at.strftime('%d.%m.%Y'), inline=True)
            embed.add_field(name="🎯 Участников", value=member.guild.member_count, inline=True)
            await channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Ошибка приветствия: {e}")

@bot.event
async def on_message(message):
    """Анти-спам"""
    if message.author == bot.user:
        return
    
    if ANTI_SPAM_ENABLED and message.guild:
        await check_spam(message)
    
    await bot.process_commands(message)

# ============================================
# 🔷 АНТИ-СПАМ 🔷
# ============================================

message_cache = {}

async def check_spam(message):
    if message.author.guild_permissions.administrator:
        return
    
    author_id = message.author.id
    now = datetime.datetime.now()
    
    if author_id not in message_cache:
        message_cache[author_id] = []
    
    message_cache[author_id].append({'time': now, 'content': message.content})
    message_cache[author_id] = [
        m for m in message_cache[author_id]
        if (now - m['time']).total_seconds() < ANTI_SPAM_TIME
    ]
    
    if len(message_cache[author_id]) >= ANTI_SPAM_MESSAGES:
        await handle_spam(message, "Флуд")
        return
    
    if len(message.content) > 10:
        caps = sum(1 for c in message.content if c.isupper()) / len(message.content) * 100
        if caps > ANTI_SPAM_CAPS:
            await handle_spam(message, "Капс")

async def handle_spam(message, reason):
    try:
        await message.delete()
        channel = get_log_channel(message.guild)
        if channel:
            embed = discord.Embed(
                title="⚠️ Анти-спам",
                description=f"Удалено: {reason}",
                color=COLOR_WARNING,
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="👤 Пользователь", value=message.author.mention)
            await channel.send(embed=embed)
    except:
        pass

# ============================================
# 🔷 СЛЭШ КОМАНДЫ - МОДЕРАЦИЯ 🔷
# ============================================

@bot.tree.command(name='ban', description='Забанить пользователя')
@app_commands.describe(user='Пользователь', reason='Причина')
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    try:
        await user.ban(reason=reason)
        await interaction.response.send_message(f"✅ {user.mention} забанен. Причина: {reason}", ephemeral=True)
        await log_action(interaction.guild, "Бан", interaction.user, user, reason)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

@bot.tree.command(name='kick', description='Кикнуть пользователя')
@app_commands.describe(user='Пользователь', reason='Причина')
@app_commands.default_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"✅ {user.mention} кикнут. Причина: {reason}", ephemeral=True)
        await log_action(interaction.guild, "Кик", interaction.user, user, reason)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

@bot.tree.command(name='mute', description='Замьютить на время')
@app_commands.describe(user='Пользователь', minutes='Минуты', reason='Причина')
@app_commands.default_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "Не указана"):
    try:
        role = interaction.guild.get_role(MUTE_ROLE)
        if not role:
            await interaction.response.send_message("❌ Роль мута не найдена!", ephemeral=True)
            return
        
        await user.add_roles(role, reason=reason)
        
        data = load_data()
        data['mutes'].append({
            'user_id': user.id,
            'guild_id': interaction.guild.id,
            'end_time': (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).isoformat(),
            'reason': reason
        })
        save_data(data)
        
        await interaction.response.send_message(f"🔇 {user.mention} замьючен на {minutes} мин", ephemeral=True)
        await log_action(interaction.guild, "Мут", interaction.user, user, f"{reason} ({minutes} мин)")
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

@bot.tree.command(name='unmute', description='Снять мут')
@app_commands.describe(user='Пользователь', reason='Причина')
@app_commands.default_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    try:
        role = interaction.guild.get_role(MUTE_ROLE)
        if role in user.roles:
            await user.remove_roles(role, reason=reason)
            data = load_data()
            data['mutes'] = [m for m in data['mutes'] if m['user_id'] != user.id]
            save_data(data)
            await interaction.response.send_message(f"🔊 {user.mention} размьючен", ephemeral=True)
            await log_action(interaction.guild, "Размут", interaction.user, user, reason)
        else:
            await interaction.response.send_message("❌ Не в муте!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

@bot.tree.command(name='warn', description='Предупреждение')
@app_commands.describe(user='Пользователь', reason='Причина')
@app_commands.default_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    try:
        data = load_data()
        data['warnings'].append({
            'user_id': user.id,
            'reason': reason,
            'moderator': interaction.user.id,
            'time': datetime.datetime.now().isoformat()
        })
        save_data(data)
        await interaction.response.send_message(f"⚠️ {user.mention} получил предупреждение", ephemeral=True)
        await log_action(interaction.guild, "Предупреждение", interaction.user, user, reason)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

@bot.tree.command(name='warnings', description='Предупреждения пользователя')
@app_commands.describe(user='Пользователь')
@app_commands.default_permissions(moderate_members=True)
async def warnings(interaction: discord.Interaction, user: discord.Member):
    try:
        data = load_data()
        user_warnings = [w for w in data['warnings'] if w['user_id'] == user.id]
        
        if not user_warnings:
            await interaction.response.send_message(f"✅ Нет предупреждений", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"⚠️ Предупреждения: {user.display_name}",
            color=COLOR_WARNING,
            timestamp=datetime.datetime.utcnow()
        )
        
        for i, w in enumerate(user_warnings[-5:], 1):
            embed.add_field(
                name=f"#{i}",
                value=f"Причина: {w['reason']}\nМодератор: <@{w['moderator']}>",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)

# ============================================
# 🔷 СЛЭШ КОМАНДЫ - УТИЛИТЫ 🔷
# ============================================

@bot.tree.command(name='ping', description='Пинг бота')
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Пинг",
        description=f"**{latency}ms**",
        color=COLOR_SUCCESS,
        timestamp=datetime.datetime.utcnow()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='serverinfo', description='Инфо о сервере')
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    
    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=COLOR_MAIN,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👥 Участников", value=guild.member_count, inline=True)
    embed.add_field(name="🟢 Онлайн", value=online, inline=True)
    embed.add_field(name="📝 Каналов", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Ролей", value=len(guild.roles), inline=True)
    embed.add_field(name="👑 Владелец", value=guild.owner.mention if guild.owner else "N/A", inline=True)
    embed.add_field(name="📅 Создан", value=guild.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='userinfo', description='Инфо о пользователе')
@app_commands.describe(user='Пользователь')
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    if not user:
        user = interaction.user
    
    embed = discord.Embed(
        title=f"👤 {user.display_name}",
        color=COLOR_MAIN,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="🆔 ID", value=user.id, inline=True)
    embed.add_field(name="📅 Аккаунт", value=user.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name="📌 На сервере", value=user.joined_at.strftime('%d.%m.%Y') if user.joined_at else "N/A", inline=True)
    embed.add_field(name="🎭 Ролей", value=len(user.roles), inline=True)
    embed.add_field(name="🤖 Бот", value="Да" if user.bot else "Нет", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='help', description='Справка')
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Помощь | NeonSyntax Bot",
        description="Все команды бота:",
        color=COLOR_MAIN,
        timestamp=datetime.datetime.utcnow()
    )
    
    embed.add_field(
        name="🔨 Модерация",
        value="/ban, /kick, /mute, /unmute, /warn, /warnings",
        inline=False
    )
    embed.add_field(
        name="🎫 Тикеты",
        value="/tickets, /close-ticket",
        inline=False
    )
    embed.add_field(
        name="👥 Staff",
        value="/staffapp, /stafflist",
        inline=False
    )
    embed.add_field(
        name="📬 Сообщения",
        value="/embed, /send-panel",
        inline=False
    )
    embed.add_field(
        name="📊 Утилиты",
        value="/ping, /serverinfo, /userinfo, /help",
        inline=False
    )
    
    embed.set_footer(text="NeonSyntax Bot v3.0.1")
    await interaction.response.send_message(embed=embed)

# ============================================
# 🔷 ТИКЕТЫ 🔷
# ============================================

class TicketModal(Modal):
    def __init__(self, ticket_type: str):
        super().__init__(title=f"Тикет: {ticket_type}")
        self.ticket_type = ticket_type
        self.description = TextInput(
            label="Описание",
            placeholder="Опишите проблему...",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.description)
    
    async def on_submit(self, interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, name="🎫 Тикеты")
        if not category:
            category = await interaction.guild.create_category_channel(name="🎫 Тикеты")
        
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{self.ticket_type.lower()[:10]}-{interaction.user.name}",
            category=category
        )
        
        await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        
        embed = discord.Embed(
            title=f"🎫 Тикет: {self.ticket_type}",
            description=f"Создан: {interaction.user.mention}",
            color=COLOR_MAIN,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="📝 Описание", value=self.description.value[:1000], inline=False)
        
        view = View()
        view.add_item(Button(label="🔒 Закрыть", style=discord.ButtonStyle.danger, custom_id="close_ticket"))
        
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Тикет: {channel.mention}", ephemeral=True)

class TicketPanel(View):
    @discord.ui.button(label="📝 Заказ", style=discord.ButtonStyle.success, custom_id="ticket_order")
    async def order(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TicketModal("Заказ"))
    
    @discord.ui.button(label="🐛 Баг", style=discord.ButtonStyle.danger, custom_id="ticket_bug")
    async def bug(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TicketModal("Баг"))
    
    @discord.ui.button(label="💬 Поддержка", style=discord.ButtonStyle.primary, custom_id="ticket_support")
    async def support(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(TicketModal("Поддержка"))

@bot.tree.command(name='tickets', description='Панель тикетов')
@app_commands.default_permissions(administrator=True)
async def tickets_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Система Тикетов",
        description="Выберите тип обращения:",
        color=COLOR_MAIN,
        timestamp=datetime.datetime.utcnow()
    )
    await interaction.response.send_message(embed=embed, view=TicketPanel())

@bot.tree.command(name='close-ticket', description='Закрыть тикет')
@app_commands.default_permissions(administrator=True)
async def close_ticket(interaction: discord.Interaction):
    if not interaction.channel.name.startswith('ticket-'):
        await interaction.response.send_message("❌ Не в тикете!", ephemeral=True)
        return
    
    await interaction.response.send_message("🔒 Тикет закрывается через 5 секунд...")
    await asyncio.sleep(5)
    await interaction.channel.delete()

# ============================================
# 🔷 ЗАЯВКИ НА STAFF 🔷
# ============================================

class StaffAppModal(Modal):
    def __init__(self):
        super().__init__(title="Заявка на Staff")
        self.username = TextInput(label="Discord Username", placeholder="username#0000", required=True)
        self.age = TextInput(label="Возраст", placeholder="18", required=True)
        self.exp = TextInput(label="Опыт", placeholder="Опишите опыт...", required=True, style=discord.TextStyle.paragraph)
        self.reason = TextInput(label="Почему вы?", placeholder="Расскажите о себе...", required=True, style=discord.TextStyle.paragraph)
        
        for item in [self.username, self.age, self.exp, self.reason]:
            self.add_item(item)
    
    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        data['staff_apps'].append({
            'user_id': interaction.user.id,
            'username': self.username.value,
            'age': self.age.value,
            'exp': self.exp.value,
            'reason': self.reason.value,
            'time': datetime.datetime.now().isoformat(),
            'status': 'На рассмотрении'
        })
        save_data(data)
        
        embed = discord.Embed(
            title="📋 Новая заявка на Staff",
            color=COLOR_SUCCESS,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 Пользователь", value=interaction.user.mention, inline=True)
        embed.add_field(name="📛 Username", value=self.username.value, inline=True)
        embed.add_field(name="🎂 Возраст", value=self.age.value, inline=True)
        embed.add_field(name="💼 Опыт", value=self.exp.value[:500], inline=False)
        embed.add_field(name="💭 Причина", value=self.reason.value[:500], inline=False)
        
        channel = interaction.guild.get_channel(STAFF_APP_CHANNEL)
        if channel:
            view = View()
            view.add_item(Button(label="✅ Принять", style=discord.ButtonStyle.success, custom_id="accept_staff"))
            view.add_item(Button(label="❌ Отклонить", style=discord.ButtonStyle.danger, custom_id="reject_staff"))
            await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message("✅ Заявка отправлена!", ephemeral=True)

class StaffAppView(View):
    @discord.ui.button(label="📝 Подать заявку", style=discord.ButtonStyle.success, custom_id="staff_app")
    async def app_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(StaffAppModal())

@bot.tree.command(name='staffapp', description='Заявка на стафф')
async def staff_app(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎯 Заявки на Staff",
        description="Хотите стать модератором?\nНажмите кнопку ниже!",
        color=COLOR_SUCCESS,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="📋 Требования", value="• Возраст 16+\n• Опыт модерации\n• Активность", inline=False)
    await interaction.response.send_message(embed=embed, view=StaffAppView())

@bot.tree.command(name='stafflist', description='Список стаффа')
async def staff_list(interaction: discord.Interaction):
    staff_role = interaction.guild.get_role(STAFF_ROLE)
    if not staff_role:
        await interaction.response.send_message("❌ Роль стаффа не найдена!", ephemeral=True)
        return
    
    members = staff_role.members
    embed = discord.Embed(
        title="👥 Команда Staff",
        description=f"Всего: {len(members)}",
        color=COLOR_SUCCESS,
        timestamp=datetime.datetime.utcnow()
    )
    
    for member in members[:10]:
        embed.add_field(name=member.display_name, value=member.mention, inline=True)
    
    if len(members) > 10:
        embed.set_footer(text=f"... и ещё {len(members) - 10}")
    
    await interaction.response.send_message(embed=embed)

# ============================================
# 🔷 EMBED СООБЩЕНИЯ 🔷
# ============================================

class EmbedModal(Modal):
    def __init__(self):
        super().__init__(title="Создать Embed")
        self.title = TextInput(label="Заголовок", required=True)
        self.desc = TextInput(label="Описание", required=False, style=discord.TextStyle.paragraph)
        self.color = TextInput(label="Цвет (HEX)", placeholder="#FF00FF", required=False)
        
        for item in [self.title, self.desc, self.color]:
            self.add_item(item)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            color = int(self.color.value.replace('#', ''), 16) if self.color.value else COLOR_MAIN
        except:
            color = COLOR_MAIN
        
        embed = discord.Embed(
            title=self.title.value,
            description=self.desc.value if self.desc.value else None,
            color=color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"Создано: {interaction.user}")
        
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed отправлен!", ephemeral=True)

class EmbedView(View):
    @discord.ui.button(label="📄 Embed", style=discord.ButtonStyle.primary, custom_id="embed_msg")
    async def embed_btn(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(EmbedModal())
    
    @discord.ui.button(label="💬 Текст", style=discord.ButtonStyle.success, custom_id="text_msg")
    async def text_btn(self, interaction: discord.Interaction, button: Button):
        class TextModal(Modal):
            def __init__(self):
                super().__init__(title="Текст")
                self.msg = TextInput(label="Сообщение", required=True, style=discord.TextStyle.paragraph)
                self.add_item(self.msg)
            
            async def on_submit(self, i: discord.Interaction):
                await i.channel.send(self.msg.value)
                await i.response.send_message("✅ Отправлено!", ephemeral=True)
        
        await interaction.response.send_modal(TextModal())

@bot.tree.command(name='send-panel', description='Панель сообщений')
@app_commands.default_permissions(administrator=True)
async def send_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📬 Панель отправки",
        description="Выберите тип:",
        color=COLOR_MAIN,
        timestamp=datetime.datetime.utcnow()
    )
    await interaction.response.send_message(embed=embed, view=EmbedView())

@bot.tree.command(name='embed', description='Быстрый embed')
@app_commands.describe(title='Заголовок', description='Описание', color='Цвет HEX')
@app_commands.default_permissions(administrator=True)
async def embed_cmd(interaction: discord.Interaction, title: str, description: str = None, color: str = "#FF00FF"):
    try:
        color_int = int(color.replace('#', ''), 16)
    except:
        color_int = COLOR_MAIN
    
    embed = discord.Embed(title=title, description=description, color=color_int, timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=f"By {interaction.user}")
    
    await interaction.response.send_message(embed=embed)

# ============================================
# 🔷 ФОНОВЫЕ ЗАДАЧИ 🔷
# ============================================

@tasks.loop(minutes=5)
async def update_stats():
    for guild in bot.guilds:
        channel = guild.get_channel(STATS_CHANNEL)
        if channel:
            try:
                async for msg in channel.history(limit=10):
                    if msg.author == bot.user:
                        await msg.delete()
                
                online = sum(1 for m in guild.members if m.status != discord.Status.offline)
                
                embed = discord.Embed(
                    title="📊 Статистика",
                    color=COLOR_MAIN,
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="👥 Всего", value=guild.member_count, inline=True)
                embed.add_field(name="🟢 Онлайн", value=online, inline=True)
                embed.add_field(name="📝 Каналов", value=len(guild.channels), inline=True)
                embed.add_field(name="🏓 Пинг", value=f"{round(bot.latency * 1000)}ms", inline=True)
                
                await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Статистика: {e}")

@tasks.loop(minutes=1)
async def check_mutes():
    data = load_data()
    now = datetime.datetime.now()
    
    for mute in data['mutes'][:]:
        end = datetime.datetime.fromisoformat(mute['end_time'])
        if now >= end:
            guild = bot.get_guild(mute['guild_id'])
            if guild:
                member = guild.get_member(mute['user_id'])
                if member:
                    role = guild.get_role(MUTE_ROLE)
                    if role:
                        await member.remove_roles(role)
                        await log_action(guild, "Мут истёк", bot.user, member)
            
            data['mutes'].remove(mute)
            save_data(data)

# ============================================
# 🔷 ЗАПУСК 🔷
# ============================================

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        logger.info("🚀 Запуск NeonSyntax Bot...")
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"❌ Ошибка: {e}")
