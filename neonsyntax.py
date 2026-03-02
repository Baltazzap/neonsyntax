import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

# ==========================================
# НАСТРОЙКИ (ЗАПОЛНИ ЭТО ПЕРЕД ЗАПУСКОМ)
# ==========================================
BOT_TOKEN = os.getenv('DISCORD_TOKEN')  # Вставь токен из Discord Developer Portal
GUILD_ID = 1477952025034752070        # ID твоего сервера (включи режим разработчика в Discord, нажми ПКМ на сервер -> Копировать ID)
WELCOME_ROLE_ID = 1477952294984224809 # ID роли, которую нужно выдавать (например, "Участник")
WELCOME_CHANNEL_ID = 1477955639937466531 # ID канала, куда писать приветствие (например, "general" или "chat")
# ==========================================

# Настройка интентов (разрешений)
intents = discord.Intents.default()
intents.message_content = True  # Нужно для работы команд с префиксом !
intents.members = True          # Нужно для выдачи ролей при входе

# Инициализация клиента
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Префикс для обычных команд
PREFIX = "!"

# ==========================================
# СИСТЕМА 1: АВТО ПРИВЕТСТВИЕ И АВТО РОЛЬ
# ==========================================

@client.event
async def on_member_join(member):
    """Срабатывает, когда кто-то заходит на сервер"""
    
    # 1. Выдача роли
    try:
        role = discord.utils.get(member.guild.roles, id=WELCOME_ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f"Роль выдана пользователю {member.name}")
        else:
            print(f"Роль с ID {WELCOME_ROLE_ID} не найдена!")
    except Exception as e:
        print(f"Ошибка при выдаче роли: {e}")

    # 2. Авто-приветствие
    try:
        channel = discord.utils.get(member.guild.channels, id=WELCOME_CHANNEL_ID)
        if channel:
            # Создаем красивое сообщение (Embed)
            embed = discord.Embed(
                title=f"👋 Добро пожаловать, {member.name}!",
                description="Рады видеть тебя на нашем сервере услуг разработки.",
                color=discord.Color.blue()
            )
            embed.add_field(name="🤖 Чем мы занимаемся?", value="Мы создаем крутых ботов для Discord и Telegram под ключ.", inline=False)
            embed.add_field(name="📜 Правила", value="Ознакомься с правилами в закрепленных сообщениях.", inline=False)
            embed.set_footer(text="Напиши !help или /help для списка команд")
            
            await channel.send(embed=embed)
        else:
            print(f"Канал с ID {WELCOME_CHANNEL_ID} не найден!")
    except Exception as e:
        print(f"Ошибка при отправке приветствия: {e}")

# ==========================================
# КОМАНДЫ (СЛЭШ И ПРЕФИКС)
# ==========================================

# --- Слэш команды (/) ---

@tree.command(name="start", description="Главное меню и информация об услугах", guild=discord.Object(id=GUILD_ID))
async def slash_start(interaction: discord.Interaction):
    embed = discord.Embed(title="🚀 Разработка Ботов Discord & Telegram", color=discord.Color.green())
    embed.description = "Привет! Я бот-портфолио. Мы разрабатываем сложные системы, магазины, модерацию и многое другое."
    embed.add_field(name="💼 Наши услуги", value="• Discord Боты (Python/JS)\n• Telegram Боты (Aiogram/Pyrogram)\n• Парсеры и Скрипты", inline=False)
    embed.set_thumbnail(url=interaction.client.user.avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(name="price", description="Узнать стоимость разработки", guild=discord.Object(id=GUILD_ID))
async def slash_price(interaction: discord.Interaction):
    embed = discord.Embed(title="💰 Прайс-лист", color=discord.Color.gold())
    embed.add_field(name="Простой бот", value="от 1000₽\n(Приветствия, простые команды)", inline=True)
    embed.add_field(name="Средний бот", value="от 3000₽\n(Экономика, тикеты, модерация)", inline=True)
    embed.add_field(name="Сложный проект", value="от 10000₽\n(Магазины, интеграции API, базы данных)", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="contact", description="Связаться с разработчиком", guild=discord.Object(id=GUILD_ID))
async def slash_contact(interaction: discord.Interaction):
    embed = discord.Embed(title="📞 Контакты", description="Для заказа напишите в ЛС:", color=discord.Color.blue())
    embed.add_field(name="Telegram", value="@твой_ник_в_телеграм", inline=False)
    embed.add_field(name="Discord", value="ТвойНик#0000", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="help", description="Список всех команд", guild=discord.Object(id=GUILD_ID))
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(title="❓ Помощь", description="Доступные команды:", color=discord.Color.purple())
    embed.add_field(name="Слэш команды", value="/start - Главная\n/price - Цены\n/contact - Связь\n/help - Это меню", inline=False)
    embed.add_field(name="Префикс команды", value="!start - Главная\n!price - Цены\n!contact - Связь\n!help - Это меню", inline=False)
    await interaction.response.send_message(embed=embed)

# --- Префиксные команды (!) ---

@client.command()
async def start(ctx):
    await ctx.send("🚀 **Разработка Ботов Discord & Telegram**\nМы создаем крутые проекты. Используй /start для красивого меню или пиши в ЛС разработчику.")

@client.command()
async def price(ctx):
    embed = discord.Embed(title="💰 Прайс-лист", color=discord.Color.gold())
    embed.add_field(name="Простой бот", value="от 1000₽", inline=True)
    embed.add_field(name="Средний бот", value="от 3000₽", inline=True)
    embed.add_field(name="Сложный проект", value="от 10000₽", inline=True)
    await ctx.send(embed=embed)

@client.command()
async def contact(ctx):
    await ctx.send("📞 **Связь:**\nTelegram: @твой_ник\nDiscord: ТвойНик#0000")

@client.command()
async def help(ctx):
    await ctx.send("❓ **Список команд:**\n`!start`, `!price`, `!contact`, `!help`\nТакже работают слэш команды: `/start`, `/price` и т.д.")

# ==========================================
# ЗАПУСК
# ==========================================

@client.event
async def on_ready():
    # Синхронизация слэш-команд с сервером
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Синхронизировано {len(synced)} слэш-команд для сервера {GUILD_ID}")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")

    print(f'Бот успешно запущен как {client.user}')
    print(f'ID Бота: {client.user.id}')

# Запуск бота
client.run(BOT_TOKEN)
