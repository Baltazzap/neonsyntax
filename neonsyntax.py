import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Загрузка токена из .env
load_dotenv()

# ==========================================
# ⚙️ НАСТРОЙКИ (ПРОПИШИ ID ЗДЕСЬ)
# ==========================================
BOT_TOKEN = os.getenv('DISCORD_TOKEN')  # Токен оставляем в .env для безопасности

# Вставь свои ID ниже внутри кавычек
GUILD_ID = 123456789012345678          # ID сервера
WELCOME_ROLE_ID = 987654321098765432   # ID роли для выдачи
WELCOME_CHANNEL_ID = 111111111111111   # ID канала для приветствия
# ==========================================

# Проверка токена
if not BOT_TOKEN:
    raise ValueError("⚠️ Ошибка: Токен не найден! Проверь файл .env")

# ==========================================
# НАСТРОЙКА БОТА
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# ✅ ИСПРАВЛЕНИЕ: help_command=None отключает встроенную команду help
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
tree = bot.tree

# ==========================================
# СИСТЕМА 1: АВТО ПРИВЕТСТВИЕ И АВТО РОЛЬ
# ==========================================

@bot.event
async def on_member_join(member):
    try:
        role = discord.utils.get(member.guild.roles, id=WELCOME_ROLE_ID)
        if role:
            await member.add_roles(role)
            print(f"✅ Роль выдана пользователю {member.name}")
    except Exception as e:
        print(f"❌ Ошибка при выдаче роли: {e}")

    try:
        channel = discord.utils.get(member.guild.channels, id=WELCOME_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=f"👋 Добро пожаловать, {member.name}!",
                description="Рады видеть тебя на нашем сервере услуг разработки.",
                color=discord.Color.blue()
            )
            embed.add_field(name="🤖 Чем мы занимаемся?", value="Мы создаем крутых ботов для Discord и Telegram под ключ.", inline=False)
            embed.set_footer(text="Напиши !help или /help для списка команд")
            await channel.send(embed=embed)
    except Exception as e:
        print(f"❌ Ошибка при отправке приветствия: {e}")

# ==========================================
# КОМАНДЫ
# ==========================================

@tree.command(name="start", description="Главное меню", guild=discord.Object(id=GUILD_ID))
async def slash_start(interaction: discord.Interaction):
    embed = discord.Embed(title="🚀 Разработка Ботов", color=discord.Color.green())
    embed.description = "Привет! Мы разрабатываем сложные системы, магазины и модерацию."
    await interaction.response.send_message(embed=embed)

@tree.command(name="price", description="Узнать стоимость", guild=discord.Object(id=GUILD_ID))
async def slash_price(interaction: discord.Interaction):
    embed = discord.Embed(title="💰 Прайс-лист", color=discord.Color.gold())
    embed.add_field(name="Простой бот", value="от 1000₽", inline=True)
    embed.add_field(name="Средний бот", value="от 3000₽", inline=True)
    embed.add_field(name="Сложный проект", value="от 10000₽", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="contact", description="Связаться", guild=discord.Object(id=GUILD_ID))
async def slash_contact(interaction: discord.Interaction):
    await interaction.response.send_message("📞 **Связь:**\nTelegram: @твой_ник\nDiscord: ТвойНик")

@tree.command(name="help", description="Список команд", guild=discord.Object(id=GUILD_ID))
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message("❓ **Команды:**\n`/start`, `/price`, `/contact`\n`!start`, `!price`, `!contact`")

# --- Префиксные команды (!) ---

@bot.command()
async def start(ctx): 
    await ctx.send("🚀 **Разработка Ботов**\nИспользуй /start для меню.")

@bot.command()
async def price(ctx): 
    await ctx.send("💰 **Прайс:**\nОт 1000₽ до 10000₽")

@bot.command()
async def contact(ctx): 
    await ctx.send("📞 **Связь:**\nTelegram: @твой_ник")

@bot.command()
async def help(ctx): 
    await ctx.send("❓ **Команды:**\n!start, !price, !contact")

# ==========================================
# ЗАПУСК
# ==========================================

@bot.event
async def on_ready():
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
    print(f'✅ Бот запущен: {bot.user}')

bot.run(BOT_TOKEN)
