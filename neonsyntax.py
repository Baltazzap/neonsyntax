import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from dotenv import load_dotenv
import os
import json

# Загрузка токена из .env
load_dotenv()

# ==========================================
# ⚙️ НАСТРОЙКИ (ПРОПИШИ ID ЗДЕСЬ)
# ==========================================
BOT_TOKEN = os.getenv('DISCORD_TOKEN')

# Вставь свои ID ниже
GUILD_ID = 1477952025034752070          # ID сервера
WELCOME_ROLE_ID = 987654321098765432   # ID роли для выдачи
WELCOME_CHANNEL_ID = 111111111111111   # ID канала для приветствия
TICKET_CATEGORY_ID = 1477964293122031717   # ID категории, где создаются тикеты
DEVELOPER_ROLE_ID = 1477952290148192338    # ID роли "Разработчик" (доступ к тикетам)
ADMIN_ROLE_ID = 1477952288076201984        # ID роли "Админ" (полный доступ)
TICKET_CHANNEL_ID = 1477956383520325754    # ID канала, куда отправлять панель тикетов
# ==========================================

if not BOT_TOKEN:
    raise ValueError("⚠️ Ошибка: Токен не найден! Проверь файл .env")

# ==========================================
# НАСТРОЙКА БОТА
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
tree = bot.tree

# Файл для хранения номеров тикетов
TICKET_FILE = "tickets.json"

def get_ticket_number():
    """Получает следующий номер тикета"""
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            number = data.get('last_ticket', 0) + 1
    else:
        number = 1
    save_ticket_number(number)
    return number

def save_ticket_number(number):
    """Сохраняет номер тикета"""
    with open(TICKET_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_ticket': number}, f)

# ==========================================
# КНОПКИ И VIEW ДЛЯ ТИКЕТОВ
# ==========================================

class TicketTypeSelect(View):
    """Выбор типа бота для тикета"""
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="📱 Telegram Бот", style=discord.ButtonStyle.blurple, custom_id="ticket_telegram")
    async def telegram_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Telegram")

    @discord.ui.button(label="💬 Discord Бот", style=discord.ButtonStyle.green, custom_id="ticket_discord")
    async def discord_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Discord")

    async def create_ticket(self, interaction: discord.Interaction, bot_type: str):
        # Проверка - нет ли уже открытого тикета у пользователя
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.name.startswith("заявка-") and channel.topic and str(self.author.id) in channel.topic:
                    await interaction.response.send_message(f"❌ У вас уже есть открытый тикет: {channel.mention}", ephemeral=True)
                    return

        ticket_number = get_ticket_number()
        category = discord.utils.get(interaction.guild.categories, id=TICKET_CATEGORY_ID)
        
        # Создаем канал
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(DEVELOPER_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        
        channel = await interaction.guild.create_text_channel(
            name=f"заявка-{ticket_number}",
            category=category,
            overwrites=overwrites,
            topic=f"Тикет от {self.author.id} | Тип: {bot_type}"
        )

        # Приветственное сообщение в тикете
        embed = discord.Embed(
            title=f"🎫 Тикет #{ticket_number}",
            description=f"Здравствуйте, {self.author.mention}!\n\nВаш тикет создан. Опишите вашу задачу подробнее.",
            color=discord.Color.blue()
        )
        embed.add_field(name="📌 Тип разработки", value=f"**{bot_type} Бот**", inline=False)
        embed.add_field(name="👤 Заказчик", value=f"{self.author.name}", inline=True)
        embed.add_field(name="🆔 ID пользователя", value=f"`{self.author.id}`", inline=True)
        embed.set_footer(text=f"Номер тикета: #{ticket_number}")

        # Кнопка закрытия (только для админа/разработчика)
        close_view = View()
        close_btn = Button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red, custom_id="close_ticket")
        close_btn.callback = self.close_ticket_callback
        close_view.add_item(close_btn)

        await channel.send(embed=embed, view=close_view)
        await channel.send(f"👋 {self.author.mention}, добро пожаловать в тикет!")

        await interaction.response.send_message(f"✅ Тикет создан: {channel.mention}", ephemeral=True)

    async def close_ticket_callback(self, interaction: discord.Interaction):
        # Проверка прав (только админ или разработчик)
        member = interaction.user
        role_ids = [ADMIN_ROLE_ID, DEVELOPER_ROLE_ID]
        if not any(role.id in role_ids for role in member.roles):
            await interaction.response.send_message("❌ У вас нет прав для закрытия тикета!", ephemeral=True)
            return
        
        confirm_view = View()
        confirm_btn = Button(label="✅ Подтвердить", style=discord.ButtonStyle.green, custom_id="confirm_close")
        cancel_btn = Button(label="❌ Отмена", style=discord.ButtonStyle.gray, custom_id="cancel_close")
        
        async def confirm_callback(interaction: discord.Interaction):
            await interaction.channel.delete()
        
        async def cancel_callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="❌ Закрытие тикета отменено.", view=None)
        
        confirm_btn.callback = confirm_callback
        cancel_btn.callback = cancel_callback
        confirm_view.add_item(confirm_btn)
        confirm_view.add_item(cancel_btn)
        
        await interaction.response.send_message("⚠️ Вы уверены, что хотите закрыть тикет?", view=confirm_view, ephemeral=True)


class TicketPanelView(View):
    """Панель создания тикета (кнопка в канале)"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Создать обращение", style=discord.ButtonStyle.green, custom_id="create_ticket_panel")
    async def create_ticket_btn(self, interaction: discord.Interaction, button: Button):
        view = TicketTypeSelect(interaction.user)
        await interaction.response.send_message("Выберите тип бота для разработки:", view=view, ephemeral=True)


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
    embed = discord.Embed(title="❓ Помощь", description="Доступные команды:", color=discord.Color.purple())
    embed.add_field(name="Слэш команды", value="/start - Главная\n/price - Цены\n/contact - Связь\n/help - Это меню\n/ticket - Панель тикетов", inline=False)
    embed.add_field(name="Префикс команды", value="!start - Главная\n!price - Цены\n!contact - Связь\n!help - Это меню\n!ticket - Панель тикетов", inline=False)
    await interaction.response.send_message(embed=embed)

# --- Команда для отправки панели тикетов (Только Админ) ---

@tree.command(name="ticket", description="Отправить панель создания тикетов (Только Админ)", guild=discord.Object(id=GUILD_ID))
async def slash_ticket(interaction: discord.Interaction):
    # Проверка прав админа
    member = interaction.user
    if not any(role.id == ADMIN_ROLE_ID for role in member.roles):
        await interaction.response.send_message("❌ У вас нет прав для использования этой команды!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📩 Создание обращения",
        description="**Добрый день!**\n\nЕсли вы хотите заказать разработку персонального бота, создайте обращение нажав кнопку ниже.",
        color=discord.Color.blue()
    )
    embed.add_field(name="💼 Наши услуги", value="• Discord Боты\n• Telegram Боты\n• Парсеры и Скрипты", inline=False)
    embed.set_footer(text="NeoSyntax Development")

    view = TicketPanelView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.command()
async def ticket(ctx):
    """Префиксная версия команды тикет"""
    if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
        await ctx.send("❌ У вас нет прав для использования этой команды!")
        return

    embed = discord.Embed(
        title="📩 Создание обращения",
        description="**Добрый день!**\n\nЕсли вы хотите заказать разработку персонального бота, создайте обращение нажав кнопку ниже.",
        color=discord.Color.blue()
    )
    embed.add_field(name="💼 Наши услуги", value="• Discord Боты\n• Telegram Боты\n• Парсеры и Скрипты", inline=False)
    embed.set_footer(text="NeoSyntax Development")

    view = TicketPanelView()
    await ctx.send(embed=embed, view=view)

@bot.command()
async def start(ctx): 
    await ctx.send("🚀 **Разработка Ботов**\nИспользуй /start для меню.")

@bot.command()
async def price(ctx): 
    embed = discord.Embed(title="💰 Прайс-лист", color=discord.Color.gold())
    embed.add_field(name="Простой бот", value="от 1000₽", inline=True)
    embed.add_field(name="Средний бот", value="от 3000₽", inline=True)
    embed.add_field(name="Сложный проект", value="от 10000₽", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def contact(ctx): 
    await ctx.send("📞 **Связь:**\nTelegram: @твой_ник\nDiscord: ТвойНик")

@bot.command()
async def help(ctx): 
    await ctx.send("❓ **Команды:**\n!start, !price, !contact, !ticket, !help")

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
    
    # Регистрируем персистентные view (кнопки работают после перезагрузки)
    bot.add_view(TicketPanelView())
    # Для кнопок внутри тикета нужно хранить их состояние отдельно или пересоздавать
    
    print(f'✅ Бот запущен: {bot.user}')
    print(f'🆔 ID Бота: {bot.user.id}')

bot.run(BOT_TOKEN)
