import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Загрузка токена из .env
load_dotenv()

# ==========================================
# 🎨 НЕОНОВАЯ ПАЛИТРА
# ==========================================
class NeonColors:
    PURPLE = 0x8A2BE2      # Основной бренд
    BLUE = 0x00BFFF        # Информация
    GREEN = 0x00FF7F       # Успех / Telegram
    RED = 0xFF1493         # Ошибки / Закрытие
    GOLD = 0xFFD700        # Прайс
    CYAN = 0x00FFFF        # Тикеты заказов
    ORANGE = 0xFFA500      # Стафф тикеты
    WHITE = 0xFFFFFF
    DARK = 0x0D0D0D

# ==========================================
# ⚙️ НАСТРОЙКИ (ОБНОВЛЕНО)
# ==========================================
BOT_TOKEN = os.getenv('DISCORD_TOKEN')

# ID сервера и ролей
GUILD_ID = 1477952025034752070
WELCOME_ROLE_ID = 1477952294984224809
WELCOME_CHANNEL_ID = 1477955639937466531

# Тикеты заказов (клиенты)
TICKET_CATEGORY_ID = 1477997491659214968
DEVELOPER_ROLE_ID = 1477952290148192338
ADMIN_ROLE_ID = 1477952288076201984

# Тикеты стаффа (заявки) ✅ ОБНОВЛЕНО
STAFF_TICKET_CATEGORY_ID = 1478003822352662600
SUPPORT_ROLE_ID = 1477952291439902791
MODERATOR_ROLE_ID = 1477952291439902791

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

# Файлы для хранения номеров тикетов
TICKET_FILE = "tickets.json"
STAFF_TICKET_FILE = "staff_tickets.json"

def get_ticket_number(file=TICKET_FILE):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            number = data.get('last_ticket', 0) + 1
    else:
        number = 1
    save_ticket_number(number, file)
    return number

def save_ticket_number(number, file=TICKET_FILE):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump({'last_ticket': number}, f)

# ==========================================
# 🎨 ШАБЛОНЫ EMBED
# ==========================================

def create_welcome_embed(member):
    embed = discord.Embed(
        title=f"👋 Добро пожаловать, {member.name}!",
        description="**Рады видеть тебя в NeonSyntax | DevStudio!**",
        color=NeonColors.BLUE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🤖 **Наши услуги**", value="• **Discord Боты** — модерация, экономика, магазины\n• **Telegram Боты** — рассылки, магазины, интеграции\n• **Парсеры** — сбор данных с сайтов", inline=False)
    embed.add_field(name="🚀 **Быстрый старт**", value="`/start` — Главная\n`/price` — Прайс\n`/ticket` — Заказ\n`/staff` — Заявка в стафф", inline=False)
    embed.set_footer(text=f"ID: {member.id} • NeonSyntax | DevStudio © {datetime.now().year}")
    return embed

def create_ticket_embed(ticket_number, bot_type, author):
    embed = discord.Embed(
        title=f"🎫 Тикет заказа #{ticket_number}",
        description=f"**Здравствуйте, {author.mention}!**\n\nВаше обращение создано. Опишите задачу подробно.",
        color=NeonColors.CYAN,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📌 **Тип разработки**", value=f"**{bot_type} Бот**", inline=True)
    embed.add_field(name="👤 **Заказчик**", value=f"{author.name}", inline=True)
    embed.add_field(name="🆔 **ID**", value=f"`{author.id}`", inline=True)
    embed.set_footer(text=f"NeonSyntax | DevStudio • #{ticket_number}")
    return embed

def create_staff_ticket_embed(ticket_number, position, author):
    embed = discord.Embed(
        title=f"📋 Заявка в стафф #{ticket_number}",
        description=f"**Здравствуйте, {author.mention}!**\n\nВаша заявка на позицию создана. Ожидайте рассмотрения.",
        color=NeonColors.ORANGE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📌 **Позиция**", value=f"**{position}**", inline=True)
    embed.add_field(name="👤 **Заявитель**", value=f"{author.name}", inline=True)
    embed.add_field(name="🆔 **ID**", value=f"`{author.id}`", inline=True)
    embed.add_field(name="📅 **Дата подачи**", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=False)
    embed.set_footer(text=f"NeonSyntax | DevStudio • #{ticket_number}")
    return embed

def create_ticket_panel_embed():
    embed = discord.Embed(
        title="📩 **Создание обращения (Заказ)**",
        description="**Добрый день!**\n\nЕсли вы хотите заказать разработку персонального бота, нажмите кнопку ниже.\n\n⏱ **Время ответа:** 1-24 часа",
        color=NeonColors.PURPLE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="💼 **Специализации**", value="• **Discord** — боты для серверов\n• **Telegram** — боты для бизнеса\n• **Web** — парсеры, API", inline=False)
    embed.set_footer(text="NeonSyntax | DevStudio • Заказ услуг")
    return embed

def create_staff_panel_embed():
    embed = discord.Embed(
        title="🛡️ **Заявка в команду NeonSyntax | DevStudio**",
        description="**Хочешь стать частью нашей команды?**\n\nНажми кнопку ниже, чтобы подать заявку на одну из доступных позиций.\n\n⏱ **Время рассмотрения:** 1-7 дней",
        color=NeonColors.ORANGE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📌 **Открытые вакансии**", value="• **🎧 Поддержка** — помощь пользователям\n• **🔨 Модератор** — модерация сервера\n• **💻 Разработчик** — создание ботов", inline=False)
    embed.add_field(name="⭐ **Требования**", value="✅ Активность в Discord\n✅ Опыт работы (для разработчика)\n✅ Грамотная речь\n✅ Возраст 16+", inline=False)
    embed.set_footer(text="NeonSyntax | DevStudio • Набор в стафф")
    return embed

def create_price_embed():
    embed = discord.Embed(
        title="💰 **Прайс-лист**",
        description="**Актуальные цены на разработку**\n\n⚠️ *Точную цену рассчитаю после обсуждения ТЗ*",
        color=NeonColors.GOLD,
        timestamp=datetime.utcnow()
    )
    embed.add_field(
        name="🥉 **Простые боты**", 
        value="**от 5,000₽**\n• Простые команды\n• Приветствия\n• Базовая модерация\n• Срок: 3-7 дней", 
        inline=True
    )
    embed.add_field(
        name="🥈 **Средней сложности**", 
        value="**от 15,000₽**\n• Экономика сервера\n• Система тикетов\n• Интеграции API\n• Срок: 7-14 дней", 
        inline=True
    )
    embed.add_field(
        name="🥇 **Сложные проекты**", 
        value="**от 30,000₽**\n• Магазины с оплатой\n• Сложные системы\n• База данных\n• Срок: 14-30 дней", 
        inline=True
    )
    embed.add_field(
        name="📞 **Связь**", 
        value="Telegram: `@твой_ник`\nDiscord: `ТвойНик#0000`\nEmail: `info@neonsyntax.ru`", 
        inline=False
    )
    embed.set_footer(text="💳 Предоплата 50% • Рассрочка возможна")
    return embed

def create_start_embed():
    embed = discord.Embed(
        title="🚀 **NeonSyntax | DevStudio**",
        description="**Профессиональная разработка ботов и автоматизация**\n\nМы создаём цифровые решения для вашего бизнеса с 2021 года.",
        color=NeonColors.PURPLE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📊 **Проекты**", value="• **50+** успешных\n• **30+** клиентов\n• **98%** отзывов", inline=True)
    embed.add_field(name="⚡ **Технологии**", value="• Python 3.11+\n• Discord.py 2.0+\n• Aiogram 3.x", inline=True)
    embed.set_footer(text="NeonSyntax | DevStudio © 2024")
    return embed

def create_contact_embed():
    embed = discord.Embed(
        title="📞 **Контакты**",
        description="**Свяжитесь с нами**",
        color=NeonColors.BLUE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="💬 **Telegram**", value="`@твой_ник`", inline=True)
    embed.add_field(name="🎮 **Discord**", value="`ТвойНик#0000`", inline=True)
    embed.add_field(name="📧 **Email**", value="`info@neonsyntax.ru`", inline=True)
    embed.set_footer(text="💡 Отвечаем в течение 24 часов")
    return embed

# ==========================================
# 🔘 КНОПКИ И VIEW
# ==========================================

class CloseTicketView(View):
    """Кнопка закрытия тикета"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket_btn(self, interaction: discord.Interaction, button: Button):
        member = interaction.user
        role_ids = [ADMIN_ROLE_ID, DEVELOPER_ROLE_ID, SUPPORT_ROLE_ID, MODERATOR_ROLE_ID]
        if not any(role.id in role_ids for role in member.roles):
            embed = discord.Embed(title="❌ **Нет доступа**", description="У вас нет прав!", color=NeonColors.RED, timestamp=datetime.utcnow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        confirm_view = View()
        confirm_btn = Button(label="✅ Подтвердить", style=discord.ButtonStyle.green, custom_id="confirm_close", emoji="✅")
        cancel_btn = Button(label="❌ Отмена", style=discord.ButtonStyle.gray, custom_id="cancel_close", emoji="❌")
        
        async def confirm_callback(interaction: discord.Interaction):
            await interaction.channel.delete()
        
        async def cancel_callback(interaction: discord.Interaction):
            embed = discord.Embed(title="❌ **Отменено**", description="Закрытие отменено.", color=NeonColors.RED, timestamp=datetime.utcnow())
            await interaction.response.edit_message(embed=embed, view=None)
        
        confirm_btn.callback = confirm_callback
        cancel_btn.callback = cancel_callback
        confirm_view.add_item(confirm_btn)
        confirm_view.add_item(cancel_btn)
        
        embed = discord.Embed(title="⚠️ **Подтверждение**", description="Закрыть тикет?", color=NeonColors.GOLD, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)


class TicketTypeSelect(View):
    """Выбор типа заказа"""
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="📱 Telegram Бот", style=discord.ButtonStyle.green, custom_id="ticket_telegram", emoji="📱")
    async def telegram_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Telegram", TICKET_CATEGORY_ID, TICKET_FILE)

    @discord.ui.button(label="💬 Discord Бот", style=discord.ButtonStyle.blurple, custom_id="ticket_discord", emoji="💬")
    async def discord_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Discord", TICKET_CATEGORY_ID, TICKET_FILE)

    async def create_ticket(self, interaction: discord.Interaction, bot_type: str, category_id: int, ticket_file: str):
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.name.startswith("заявка-") and channel.topic and str(self.author.id) in channel.topic:
                    embed = discord.Embed(title="❌ **Тикет уже существует**", description=f"{channel.mention}", color=NeonColors.RED, timestamp=datetime.utcnow())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

        ticket_number = get_ticket_number(ticket_file)
        category = discord.utils.get(interaction.guild.categories, id=category_id)
        
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

        embed = create_ticket_embed(ticket_number, bot_type, self.author)
        close_view = CloseTicketView()

        await channel.send(embed=embed, view=close_view)
        await channel.send(f"👋 {self.author.mention}, **добро пожаловать!**")

        success_embed = discord.Embed(title="✅ **Тикет создан**", description=f"{channel.mention}", color=NeonColors.GREEN, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=success_embed, ephemeral=True)


class StaffPositionSelect(View):
    """Выбор позиции в стафф"""
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="🎧 Поддержка", style=discord.ButtonStyle.green, custom_id="staff_support", emoji="🎧")
    async def support_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_staff_ticket(interaction, "Поддержка")

    @discord.ui.button(label="🔨 Модератор", style=discord.ButtonStyle.blurple, custom_id="staff_moderator", emoji="🔨")
    async def moderator_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_staff_ticket(interaction, "Модератор")

    @discord.ui.button(label="💻 Разработчик", style=discord.ButtonStyle.red, custom_id="staff_developer", emoji="💻")
    async def developer_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_staff_ticket(interaction, "Разработчик")

    async def create_staff_ticket(self, interaction: discord.Interaction, position: str):
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.name.startswith("стафф-") and channel.topic and str(self.author.id) in channel.topic:
                    embed = discord.Embed(title="❌ **Заявка уже существует**", description=f"{channel.mention}", color=NeonColors.RED, timestamp=datetime.utcnow())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

        ticket_number = get_ticket_number(STAFF_TICKET_FILE)
        category = discord.utils.get(interaction.guild.categories, id=STAFF_TICKET_CATEGORY_ID)
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(MODERATOR_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        
        channel = await interaction.guild.create_text_channel(
            name=f"стафф-{ticket_number}",
            category=category,
            overwrites=overwrites,
            topic=f"Заявка от {self.author.id} | Позиция: {position}"
        )

        embed = create_staff_ticket_embed(ticket_number, position, self.author)
        close_view = CloseTicketView()

        await channel.send(embed=embed, view=close_view)
        await channel.send(f"👋 {self.author.mention}, **спасибо за заявку!**\n\nОпишите свой опыт и почему вы хотите к нам.")

        success_embed = discord.Embed(title="✅ **Заявка подана**", description=f"{channel.mention}\nПозиция: **{position}**", color=NeonColors.GREEN, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=success_embed, ephemeral=True)


class TicketPanelView(View):
    """Панель заказов"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Создать заказ", style=discord.ButtonStyle.green, custom_id="create_ticket_panel", emoji="📩")
    async def create_ticket_btn(self, interaction: discord.Interaction, button: Button):
        view = TicketTypeSelect(interaction.user)
        embed = discord.Embed(title="🎯 **Тип разработки**", description="Выберите тип бота:", color=NeonColors.PURPLE, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class StaffPanelView(View):
    """Панель заявок в стафф"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛡️ Подать заявку", style=discord.ButtonStyle.red, custom_id="create_staff_panel", emoji="🛡️")
    async def create_staff_btn(self, interaction: discord.Interaction, button: Button):
        view = StaffPositionSelect(interaction.user)
        embed = discord.Embed(title="🎯 **Выберите позицию**", description="На какую позицию вы подаёте?", color=NeonColors.ORANGE, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ==========================================
# 🎉 СОБЫТИЯ
# ==========================================

@bot.event
async def on_member_join(member):
    try:
        role = discord.utils.get(member.guild.roles, id=WELCOME_ROLE_ID)
        if role:
            await member.add_roles(role)
    except Exception as e:
        print(f"❌ Ошибка роли: {e}")

    try:
        channel = discord.utils.get(member.guild.channels, id=WELCOME_CHANNEL_ID)
        if channel:
            embed = create_welcome_embed(member)
            await channel.send(embed=embed)
    except Exception as e:
        print(f"❌ Ошибка приветствия: {e}")

# ==========================================
# 💬 КОМАНДЫ
# ==========================================

@tree.command(name="start", description="🏠 Главная", guild=discord.Object(id=GUILD_ID))
async def slash_start(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_start_embed())

@tree.command(name="price", description="💰 Прайс", guild=discord.Object(id=GUILD_ID))
async def slash_price(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_price_embed())

@tree.command(name="contact", description="📞 Контакты", guild=discord.Object(id=GUILD_ID))
async def slash_contact(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_contact_embed())

@tree.command(name="help", description="❓ Помощь", guild=discord.Object(id=GUILD_ID))
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(title="❓ **Помощь**", description="**Команды**", color=NeonColors.PURPLE, timestamp=datetime.utcnow())
    embed.add_field(name="🔹 **Заказы**", value="`/ticket` — Панель заказов\n`/start` — Главная\n`/price` — Прайс", inline=True)
    embed.add_field(name="🔸 **Стафф**", value="`/staff` — Панель заявок\n`/help` — Это меню", inline=True)
    embed.add_field(name="🔹 **Общее**", value="`/contact` — Контакты\n`!команда` — Префикс", inline=True)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ticket", description="📩 Панель заказов (Админ)", guild=discord.Object(id=GUILD_ID))
async def slash_ticket(interaction: discord.Interaction):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_message(embed=create_ticket_panel_embed(), view=TicketPanelView())

@tree.command(name="staff", description="🛡️ Панель заявок в стафф (Админ)", guild=discord.Object(id=GUILD_ID))
async def slash_staff(interaction: discord.Interaction):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_message(embed=create_staff_panel_embed(), view=StaffPanelView())

@bot.command()
async def ticket(ctx):
    if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    await ctx.send(embed=create_ticket_panel_embed(), view=TicketPanelView())

@bot.command()
async def staff(ctx):
    if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    await ctx.send(embed=create_staff_panel_embed(), view=StaffPanelView())

@bot.command()
async def start(ctx): await ctx.send(embed=create_start_embed())
@bot.command()
async def price(ctx): await ctx.send(embed=create_price_embed())
@bot.command()
async def contact(ctx): await ctx.send(embed=create_contact_embed())
@bot.command()
async def help(ctx): await ctx.send(embed=discord.Embed(title="❓ **Помощь**", color=NeonColors.PURPLE, description="`/ticket`, `/staff`, `/start`, `/price`"))

# ==========================================
# 🚀 ЗАПУСК
# ==========================================

@bot.event
async def on_ready():
    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
    
    bot.add_view(TicketPanelView())
    bot.add_view(StaffPanelView())
    bot.add_view(CloseTicketView())
    
    print(f'✅ Бот запущен: {bot.user}')
    print(f'🎨 NeonSyntax | DevStudio: Активирован')
    print(f'📩 Система заказов: Готова')
    print(f'🛡️ Система стаффа: Готова')

bot.run(BOT_TOKEN)
