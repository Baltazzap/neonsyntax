# ============================================
# 🌆 NEONSYNTAX BOT - Discord Moderation Bot
# ============================================
# Version: 2.0.0
# Author: NeonSyntax Team
# ============================================

import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput
from dotenv import load_dotenv
import asyncio
import datetime
import json
import os
import logging
from typing import Optional
from pathlib import Path

# ============================================
# 🔷 ЗАГРУЗКА КОНФИГУРАЦИИ 🔷
# ============================================

load_dotenv()

# Токен и основные настройки
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('1477952025034752070', 0))
BOT_PREFIX = os.getenv('@NeonSyntax | DevStudio#8987', '!')
BOT_OWNER_ID = int(os.getenv('314805583788244993', 0))

# ID каналов
WELCOME_CHANNEL_ID = int(os.getenv('1477955639937466531', 0))
LOG_CHANNEL_ID = int(os.getenv('1477964505546883184', 0))
TICKET_CHANNEL_ID = int(os.getenv('1477956383520325754', 0))
STAFF_APP_CHANNEL_ID = int(os.getenv('1477964570344685670', 0))
STATS_CHANNEL_ID = int(os.getenv('1477964455555104768', 0))

# ID ролей
AUTO_ROLE_ID = int(os.getenv('1477952294984224809', 0))
MUTE_ROLE_ID = int(os.getenv('1477952295869349888', 0))
STAFF_ROLE_ID = int(os.getenv('1477952291439902791', 0))
ADMIN_ROLE_ID = int(os.getenv('1477952288076201984', 0))

# Настройки анти-спама
ANTI_SPAM_SETTINGS = {
    'messages_count': int(os.getenv('ANTI_SPAM_MESSAGES_COUNT', 5)),
    'time_window': int(os.getenv('ANTI_SPAM_TIME_WINDOW', 10)),
    'capslock_percent': int(os.getenv('ANTI_SPAM_CAPS_PERCENT', 70)),
    'duplicate_messages': int(os.getenv('ANTI_SPAM_DUPLICATE_MESSAGES', 3))
}

# Цвета embed
EMBED_COLORS = {
    'main': int(os.getenv('EMBED_COLOR_MAIN', 'FF00FF'), 16),
    'success': int(os.getenv('EMBED_COLOR_SUCCESS', '43b581'), 16),
    'error': int(os.getenv('EMBED_COLOR_ERROR', 'ed4245'), 16),
    'warning': int(os.getenv('EMBED_COLOR_WARNING', 'faa61a'), 16)
}

# ============================================
# 🔷 НАСТРОЙКА ЛОГИРОВАНИЯ 🔷
# ============================================

# Создание директорий
Path('data').mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
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
    command_prefix=BOT_PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# ============================================
# 🔷 БАЗА ДАННЫХ (JSON) 🔷
# ============================================

DATA_FILE = 'data/bot_data.json'

def load_data():
    """Загрузка данных из JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'tickets': [],
        'staff_apps': [],
        'mutes': [],
        'warnings': [],
        'stats': {}
    }

def save_data(data):
    """Сохранение данных в JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

# ============================================
# 🔷 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ 🔷
# ============================================

def get_log_channel(guild):
    """Получение канала логирования"""
    return guild.get_channel(LOG_CHANNEL_ID)

async def log_action(guild, action, user, target=None, reason=None):
    """Логирование действий администрации"""
    log_channel = get_log_channel(guild)
    if not log_channel:
        logger.warning(f"Канал логирования не найден для {guild.name}")
        return
    
    embed = discord.Embed(
        title=f"🔨 {action}",
        color=EMBED_COLORS['error'],
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="👤 Модератор", value=f"{user.mention} ({user.id})", inline=True)
    if target:
        embed.add_field(name="🎯 Цель", value=f"{target.mention} ({target.id})", inline=True)
    if reason:
        embed.add_field(name="📝 Причина", value=reason, inline=False)
    embed.set_footer(text=f"ID: {user.id}")
    
    try:
        await log_channel.send(embed=embed)
        logger.info(f"Действие залогировано: {action} by {user}")
    except Exception as e:
        logger.error(f"Ошибка логирования: {e}")

# ============================================
# 🔷 СОБЫТИЯ БОТА 🔷
# ============================================

@bot.event
async def on_ready():
    """Запуск бота"""
    logger.info(f'✅ {bot.user} успешно запущен!')
    logger.info(f'📊 Серверов: {len(bot.guilds)}')
    logger.info(f'👥 Пользователей: {len(bot.users)}')
    
    # Запуск фоновых задач
    update_stats.start()
    check_mutes.start()
    
    # Установка статуса
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{BOT_PREFIX}help | NeonSyntax"
        )
    )
    
    logger.info('🎯 Бот готов к работе!')

@bot.event
async def on_member_join(member):
    """Авто-приветствие и авто-роль"""
    try:
        # Авто-роль
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            await member.add_roles(role)
            logger.info(f"Авто-роль выдана: {member}")
        
        # Авто-приветствие
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="👋 Добро пожаловать!",
                description=f"{member.mention}, добро пожаловать на сервер **{member.guild.name}**!",
                color=EMBED_COLORS['success'],
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="📅 Дата регистрации", value=member.created_at.strftime('%d.%m.%Y'), inline=True)
            embed.add_field(name="🎯 Участников", value=member.guild.member_count, inline=True)
            embed.set_footer(text=f"ID: {member.id}")
            
            await channel.send(embed=embed)
            logger.info(f"Приветствие отправлено: {member}")
    except Exception as e:
        logger.error(f"Ошибка при приветствии: {e}")

@bot.event
async def on_message(message):
    """Обработка сообщений (анти-спам)"""
    if message.author == bot.user:
        return
    
    # Проверка на спам
    await check_spam(message)
    
    # Обработка команд
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для этой команды!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Укажите все необходимые аргументы!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Пользователь не найден!")
    else:
        logger.error(f"Ошибка команды: {error}")
        await ctx.send(f"❌ Произошла ошибка: {error}")

# ============================================
# 🔷 АНТИ-СПАМ СИСТЕМА 🔷
# ============================================

message_cache = {}

async def check_spam(message):
    """Проверка на спам, флуд, капс"""
    if not message.guild or message.author.guild_permissions.administrator:
        return
    
    author_id = message.author.id
    current_time = datetime.datetime.now()
    
    if author_id not in message_cache:
        message_cache[author_id] = {
            'messages': [],
            'last_message': None
        }
    
    cache = message_cache[author_id]
    cache['messages'].append({
        'content': message.content,
        'time': current_time
    })
    
    # Очистка старых сообщений
    cache['messages'] = [
        msg for msg in cache['messages']
        if (current_time - msg['time']).total_seconds() < ANTI_SPAM_SETTINGS['time_window']
    ]
    
    # Проверка на флуд
    if len(cache['messages']) >= ANTI_SPAM_SETTINGS['messages_count']:
        await handle_spam(message, "Флуд")
        return
    
    # Проверка на капс
    if len(message.content) > 10:
        caps_percent = sum(1 for c in message.content if c.isupper()) / len(message.content) * 100
        if caps_percent > ANTI_SPAM_SETTINGS['capslock_percent']:
            await handle_spam(message, "Капслок")
            return
    
    # Проверка на дубликаты
    recent_messages = [msg['content'] for msg in cache['messages'][-3:]]
    if recent_messages.count(message.content) >= ANTI_SPAM_SETTINGS['duplicate_messages']:
        await handle_spam(message, "Спам")
        return

async def handle_spam(message, reason):
    """Обнаружение спама"""
    try:
        await message.delete()
        await message.author.send(f"⚠️ Ваше сообщение было удалено: **{reason}**")
        
        log_channel = get_log_channel(message.guild)
        if log_channel:
            embed = discord.Embed(
                title="⚠️ Анти-спам",
                description=f"Сообщение удалено: {reason}",
                color=EMBED_COLORS['warning'],
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="👤 Пользователь", value=message.author.mention, inline=True)
            embed.add_field(name="📝 Канал", value=message.channel.mention, inline=True)
            await log_channel.send(embed=embed)
        
        logger.warning(f"Спам обнаружен: {message.author} - {reason}")
    except Exception as e:
        logger.error(f"Ошибка обработки спама: {e}")

# ============================================
# 🔷 ФОНОВЫЕ ЗАДАЧИ 🔷
# ============================================

@tasks.loop(minutes=5)
async def update_stats():
    """Обновление статистики сервера"""
    for guild in bot.guilds:
        channel = guild.get_channel(STATS_CHANNEL_ID)
        if channel:
            try:
                async for msg in channel.history(limit=10):
                    if msg.author == bot.user:
                        await msg.delete()
                
                online_count = sum(1 for member in guild.members if member.status != discord.Status.offline)
                
                embed = discord.Embed(
                    title="📊 Статистика Сервера",
                    color=EMBED_COLORS['main'],
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="👥 Всего участников", value=guild.member_count, inline=True)
                embed.add_field(name="🟢 Онлайн", value=online_count, inline=True)
                embed.add_field(name="📝 Каналов", value=len(guild.channels), inline=True)
                embed.add_field(name="🎭 Ролей", value=len(guild.roles), inline=True)
                embed.add_field(name="🤖 Ботов", value=sum(1 for m in guild.members if m.bot), inline=True)
                embed.add_field(name="🏓 Пинг бота", value=f"{round(bot.latency * 1000)}ms", inline=True)
                embed.set_footer(text=f"Сервер: {guild.name}")
                
                await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Ошибка обновления статистики: {e}")

@tasks.loop(minutes=1)
async def check_mutes():
    """Проверка истечения мутов"""
    data = load_data()
    current_time = datetime.datetime.now()
    
    for mute in data['mutes'][:]:
        end_time = datetime.datetime.fromisoformat(mute['end_time'])
        if current_time >= end_time:
            guild = bot.get_guild(mute['guild_id'])
            if guild:
                member = guild.get_member(mute['user_id'])
                if member:
                    mute_role = guild.get_role(MUTE_ROLE_ID)
                    if mute_role:
                        await member.remove_roles(mute_role)
                        await log_action(guild, "🔓 Мут истёк", bot.user, member, "Время мута истекло")
            
            data['mutes'].remove(mute)
            save_data(data)

# ============================================
# 🔷 КОМАНДЫ АДМИНИСТРИРОВАНИЯ 🔷
# ============================================

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_command(ctx, member: discord.Member, *, reason: str = "Не указана"):
    """Бан пользователя"""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} забанен. Причина: {reason}")
        await log_action(ctx.guild, "🔨 Бан", ctx.author, member, reason)
        logger.info(f"Бан: {member} by {ctx.author}")
    except Exception as e:
        logger.error(f"Ошибка бана: {e}")
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_command(ctx, member: discord.Member, *, reason: str = "Не указана"):
    """Кик пользователя"""
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} кикнут. Причина: {reason}")
        await log_action(ctx.guild, "👢 Кик", ctx.author, member, reason)
        logger.info(f"Кик: {member} by {ctx.author}")
    except Exception as e:
        logger.error(f"Ошибка кика: {e}")
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command(name='mute')
@commands.has_permissions(moderate_members=True)
async def mute_command(ctx, member: discord.Member, minutes: int, *, reason: str = "Не указана"):
    """Мут пользователя на время"""
    try:
        mute_role = ctx.guild.get_role(MUTE_ROLE_ID)
        if not mute_role:
            await ctx.send("❌ Роль мута не найдена!")
            return
        
        await member.add_roles(mute_role, reason=reason)
        
        data = load_data()
        data['mutes'].append({
            'user_id': member.id,
            'guild_id': ctx.guild.id,
            'end_time': (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).isoformat(),
            'reason': reason,
            'moderator': ctx.author.id
        })
        save_data(data)
        
        await ctx.send(f"🔇 {member.mention} замьючен на {minutes} минут. Причина: {reason}")
        await log_action(ctx.guild, "🔇 Мут", ctx.author, member, f"{reason} ({minutes} мин)")
        logger.info(f"Мут: {member} на {minutes} мин by {ctx.author}")
    except Exception as e:
        logger.error(f"Ошибка мута: {e}")
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command(name='unmute')
@commands.has_permissions(moderate_members=True)
async def unmute_command(ctx, member: discord.Member, *, reason: str = "Не указана"):
    """Снять мут"""
    try:
        mute_role = ctx.guild.get_role(MUTE_ROLE_ID)
        if mute_role in member.roles:
            await member.remove_roles(mute_role, reason=reason)
            
            data = load_data()
            data['mutes'] = [m for m in data['mutes'] if m['user_id'] != member.id]
            save_data(data)
            
            await ctx.send(f"🔊 {member.mention} размьючен. Причина: {reason}")
            await log_action(ctx.guild, "🔊 Размут", ctx.author, member, reason)
            logger.info(f"Размут: {member} by {ctx.author}")
        else:
            await ctx.send("❌ Пользователь не в муте!")
    except Exception as e:
        logger.error(f"Ошибка размута: {e}")
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command(name='warn')
@commands.has_permissions(moderate_members=True)
async def warn_command(ctx, member: discord.Member, *, reason: str = "Не указана"):
    """Выдать предупреждение"""
    try:
        data = load_data()
        data['warnings'].append({
            'user_id': member.id,
            'guild_id': ctx.guild.id,
            'reason': reason,
            'moderator': ctx.author.id,
            'time': datetime.datetime.now().isoformat()
        })
        save_data(data)
        
        await ctx.send(f"⚠️ {member.mention} получил предупреждение. Причина: {reason}")
        await log_action(ctx.guild, "⚠️ Предупреждение", ctx.author, member, reason)
        logger.info(f"Предупреждение: {member} by {ctx.author}")
    except Exception as e:
        logger.error(f"Ошибка предупреждения: {e}")
        await ctx.send(f"❌ Ошибка: {e}")

# ============================================
# 🔷 КОМАНДЫ ПОМОЩИ И ИНФО 🔷
# ============================================

@bot.command(name='help')
async def help_command(ctx):
    """Справка по командам"""
    embed = discord.Embed(
        title="📚 Помощь | NeonSyntax Bot",
        description="Список всех доступных команд:",
        color=EMBED_COLORS['main'],
        timestamp=datetime.datetime.utcnow()
    )
    
    embed.add_field(
        name="🔨 Администрирование",
        value=f"`{BOT_PREFIX}ban` - Бан пользователя\n`{BOT_PREFIX}kick` - Кик пользователя\n`{BOT_PREFIX}mute` - Мут на время\n`{BOT_PREFIX}unmute` - Снять мут\n`{BOT_PREFIX}warn` - Предупреждение",
        inline=False
    )
    
    embed.add_field(
        name="🎫 Тикеты",
        value=f"`{BOT_PREFIX}tickets` - Панель тикетов\n`{BOT_PREFIX}staffapp` - Заявка на staff",
        inline=False
    )
    
    embed.add_field(
        name="📬 Сообщения",
        value=f"`{BOT_PREFIX}sendpanel` - Панель отправки сообщений",
        inline=False
    )
    
    embed.add_field(
        name="📊 Инфо",
        value=f"`{BOT_PREFIX}help` - Эта справка\n`{BOT_PREFIX}ping` - Пинг бота\n`{BOT_PREFIX}serverinfo` - Инфо о сервере",
        inline=False
    )
    
    embed.set_footer(text=f"Запрос от: {ctx.author}")
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Проверка пинга"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Пинг Бота",
        description=f"**{latency}ms**",
        color=EMBED_COLORS['success'],
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="NeonSyntax Bot")
    await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo_command(ctx):
    """Информация о сервере"""
    guild = ctx.guild
    online_count = sum(1 for member in guild.members if member.status != discord.Status.offline)
    
    embed = discord.Embed(
        title=f"📊 Информация о сервере",
        description=f"**{guild.name}**",
        color=EMBED_COLORS['main'],
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👥 Участников", value=guild.member_count, inline=True)
    embed.add_field(name="🟢 Онлайн", value=online_count, inline=True)
    embed.add_field(name="📝 Каналов", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Ролей", value=len(guild.roles), inline=True)
    embed.add_field(name="👑 Владелец", value=guild.owner.mention if guild.owner else "Неизвестно", inline=True)
    embed.add_field(name="📅 Создан", value=guild.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    embed.set_footer(text=f"ID: {guild.id}")
    
    await ctx.send(embed=embed)

# ============================================
# 🔷 ЗАПУСК БОТА 🔷
# ============================================

if __name__ == "__main__":
    try:
        logger.info("🚀 Запуск бота...")
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"❌ Ошибка запуска: {e}")