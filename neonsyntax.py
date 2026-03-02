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
    PURPLE = 0x8A2BE2
    BLUE = 0x00BFFF
    GREEN = 0x00FF7F
    RED = 0xFF1493
    GOLD = 0xFFD700
    CYAN = 0x00FFFF
    WHITE = 0xFFFFFF
    DARK = 0x0D0D0D

# ==========================================
# ⚙️ НАСТРОЙКИ
# ==========================================
BOT_TOKEN = os.getenv('DISCORD_TOKEN')

GUILD_ID = 1477952025034752070
WELCOME_ROLE_ID = 1477952294984224809
WELCOME_CHANNEL_ID = 1477955639937466531
TICKET_CATEGORY_ID = 1477997491659214968
DEVELOPER_ROLE_ID = 1477952290148192338
ADMIN_ROLE_ID = 1477952288076201984

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

TICKET_FILE = "tickets.json"

def get_ticket_number():
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            number = data.get('last_ticket', 0) + 1
    else:
        number = 1
    save_ticket_number(number)
    return number

def save_ticket_number(number):
    with open(TICKET_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_ticket': number}, f)

# ==========================================
# 🎨 ШАБЛОНЫ EMBED
# ==========================================

def create_welcome_embed(member):
    embed = discord.Embed(
        title=f"👋 Добро пожаловать, {member.name}!",
        description="**Рады видеть тебя в NeoSyntax Community!**\n\nЗдесь ты можешь заказать разработку бота или получить поддержку.",
        color=NeonColors.BLUE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🤖 **Наши услуги**", value="• **Discord Боты** — модерация, экономика, магазины\n• **Telegram Боты** — рассылки, магазины, интеграции\n• **Парсеры** — сбор данных с сайтов\n• **Скрипты** — автоматизация задач", inline=False)
    embed.add_field(name="🚀 **Быстрый старт**", value="`/start` — Главная информация\n`/price` — Прайс-лист\n`/ticket` — Создать обращение", inline=False)
    embed.set_footer(text=f"ID: {member.id} • NeoSyntax © {datetime.now().year}")
    return embed

def create_ticket_embed(ticket_number, bot_type, author):
    embed = discord.Embed(
        title=f"🎫 Тикет #{ticket_number}",
        description=f"**Здравствуйте, {author.mention}!**\n\nВаше обращение создано. Опишите задачу подробно — мы приступим к работе в ближайшее время.",
        color=NeonColors.CYAN,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📌 **Тип разработки**", value=f"**{bot_type} Бот**", inline=True)
    embed.add_field(name="👤 **Заказчик**", value=f"{author.name}", inline=True)
    embed.add_field(name="🆔 **ID пользователя**", value=f"`{author.id}`", inline=True)
    embed.add_field(name="📅 **Дата создания**", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=False)
    embed.set_footer(text=f"NeoSyntax Support • #{ticket_number}")
    return embed

def create_ticket_panel_embed():
    embed = discord.Embed(
        title="📩 **Создание обращения**",
        description="**Добрый день!**\n\nЕсли вы хотите заказать разработку персонального бота, нажмите кнопку ниже для создания обращения.\n\n⏱ **Время ответа:** 1-24 часа",
        color=NeonColors.PURPLE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="💼 **Наши специализации**", value="• **Discord** — боты для серверов, модерация, экономика\n• **Telegram** — боты для бизнеса, рассылки, магазины\n• **Web** — парсеры, API, автоматизация", inline=False)
    embed.add_field(name="⭐ **Почему мы?**", value="✅ Опыт работы 3+ года\n✅ Поддержка после запуска\n✅ Прозрачные цены\n✅ Соблюдение дедлайнов", inline=False)
    embed.set_footer(text="NeoSyntax Development • Все права защищены")
    return embed

def create_price_embed():
    embed = discord.Embed(
        title="💰 **Прайс-лист**",
        description="**Актуальные цены на разработку**\n\n⚠️ *Итоговая стоимость зависит от сложности проекта*",
        color=NeonColors.GOLD,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🥉 **Старт**", value="**от 1,500₽**\n• Простые команды\n• Приветствия\n• Базовая модерация\n• Срок: 3-5 дней", inline=True)
    embed.add_field(name="🥈 **Бизнес**", value="**от 5,000₽**\n• Экономика сервера\n• Система тикетов\n• Интеграции API\n• Срок: 7-14 дней", inline=True)
    embed.add_field(name="🥇 **Премиум**", value="**от 15,000₽**\n• Магазины с оплатой\n• Сложные системы\n• База данных\n• Срок: 14-30 дней", inline=True)
    embed.add_field(name="📞 **Связь**", value="Telegram: `@твой_ник`\nDiscord: `ТвойНик#0000`\nEmail: `info@neonsyntax.ru`", inline=False)
    embed.set_footer(text="💳 Возможна рассрочка • Предоплата 50%")
    return embed

def create_start_embed():
    embed = discord.Embed(
        title="🚀 **NeoSyntax Development**",
        description="**Профессиональная разработка ботов и автоматизация**\n\nМы создаём цифровые решения для вашего бизнеса с 2021 года.",
        color=NeonColors.PURPLE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📊 **Наши проекты**", value="• **50+** успешных проектов\n• **30+** довольных клиентов\n• **98%** положительных отзывов", inline=True)
    embed.add_field(name="🌍 **География**", value="• Россия\n• СНГ\n• Европа\n• США", inline=True)
    embed.add_field(name="⚡ **Технологии**", value="• Python 3.11+\n• Discord.py 2.0+\n• Aiogram 3.x\n• Node.js", inline=True)
    embed.set_footer(text="NeoSyntax © 2024 • Все права защищены")
    return embed

def create_contact_embed():
    embed = discord.Embed(
        title="📞 **Контакты**",
        description="**Свяжитесь с нами для заказа или консультации**",
        color=NeonColors.BLUE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="💬 **Telegram**", value="`@твой_ник`", inline=True)
    embed.add_field(name="🎮 **Discord**", value="`ТвойНик#0000`", inline=True)
    embed.add_field(name="📧 **Email**", value="`info@neonsyntax.ru`", inline=True)
    embed.add_field(name="🌐 **Сайт**", value="`neonsyntax.ru`", inline=True)
    embed.add_field(name="⏰ **Время работы**", value="**Пн-Пт:** 10:00 - 20:00 МСК\n**Сб-Вс:** 12:00 - 18:00 МСК", inline=False)
    embed.set_footer(text="💡 Отвечаем в течение 24 часов")
    return embed

# ==========================================
# 🔘 КНОПКИ И VIEW (ИСПРАВЛЕНО)
# ==========================================

class CloseTicketView(View):
    """Кнопка закрытия тикета с проверкой прав"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red, custom_id="close_ticket_btn", emoji="🔒")
    async def close_ticket_btn(self, interaction: discord.Interaction, button: Button):
        # Проверка прав (Админ или Разработчик)
        member = interaction.user
        role_ids = [ADMIN_ROLE_ID, DEVELOPER_ROLE_ID]
        if not any(role.id in role_ids for role in member.roles):
            embed = discord.Embed(
                title="❌ **Нет доступа**",
                description="У вас нет прав для закрытия этого тикета!",
                color=NeonColors.RED,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Меню подтверждения
        confirm_view = View()
        confirm_btn = Button(label="✅ Подтвердить", style=discord.ButtonStyle.green, custom_id="confirm_close", emoji="✅")
        cancel_btn = Button(label="❌ Отмена", style=discord.ButtonStyle.gray, custom_id="cancel_close", emoji="❌")
        
        async def confirm_callback(interaction: discord.Interaction):
            await interaction.channel.delete()
        
        async def cancel_callback(interaction: discord.Interaction):
            embed = discord.Embed(
                title="❌ **Отменено**",
                description="Закрытие тикета отменено.",
                color=NeonColors.RED,
                timestamp=datetime.utcnow()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        confirm_btn.callback = confirm_callback
        cancel_btn.callback = cancel_callback
        confirm_view.add_item(confirm_btn)
        confirm_view.add_item(cancel_btn)
        
        embed = discord.Embed(
            title="⚠️ **Подтверждение**",
            description="Вы уверены, что хотите закрыть этот тикет?\n\nЭто действие **нельзя отменить**.",
            color=NeonColors.GOLD,
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)

class TicketTypeSelect(View):
    """Выбор типа бота для тикета"""
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="📱 Telegram Бот", style=discord.ButtonStyle.green, custom_id="ticket_telegram", emoji="📱")
    async def telegram_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Telegram")

    @discord.ui.button(label="💬 Discord Бот", style=discord.ButtonStyle.blurple, custom_id="ticket_discord", emoji="💬")
    async def discord_btn(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "Discord")

    async def create_ticket(self, interaction: discord.Interaction, bot_type: str):
        # Проверка на дубликат тикета
        for channel in interaction.guild.channels:
            if isinstance(channel, discord.TextChannel):
                if channel.name.startswith("заявка-") and channel.topic and str(self.author.id) in channel.topic:
                    embed = discord.Embed(
                        title="❌ **Тикет уже существует**",
                        description=f"У вас уже есть открытый тикет: {channel.mention}",
                        color=NeonColors.RED,
                        timestamp=datetime.utcnow()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

        ticket_number = get_ticket_number()
        category = discord.utils.get(interaction.guild.categories, id=TICKET_CATEGORY_ID)
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            self.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            interaction.guild.get_role(DEVELOPER_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, manage_channels=True),
        }
        
        channel = await interaction.guild.create_text_channel(
            name=f"заявка-{ticket_number}",
            category=category,
            overwrites=overwrites,
            topic=f"Тикет от {self.author.id} | Тип: {bot_type} | Статус: Открыт"
        )

        embed = create_ticket_embed(ticket_number, bot_type, self.author)
        
        # ✅ ИСПРАВЛЕНИЕ: Используем отдельный класс View для кнопки закрытия
        close_view = CloseTicketView()

        await channel.send(embed=embed, view=close_view)
        await channel.send(f"👋 {self.author.mention}, **добро пожаловать в тикет!**")

        success_embed = discord.Embed(
            title="✅ **Тикет создан**",
            description=f"Ваше обращение успешно создано!\n\nКанал: {channel.mention}",
            color=NeonColors.GREEN,
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=success_embed, ephemeral=True)


class TicketPanelView(View):
    """Панель создания тикета"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Создать обращение", style=discord.ButtonStyle.green, custom_id="create_ticket_panel", emoji="📩")
    async def create_ticket_btn(self, interaction: discord.Interaction, button: Button):
        view = TicketTypeSelect(interaction.user)
        embed = discord.Embed(
            title="🎯 **Выберите тип разработки**",
            description="Укажите, какой тип бота вы хотите заказать:",
            color=NeonColors.PURPLE,
            timestamp=datetime.utcnow()
        )
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

@tree.command(name="start", description="🏠 Главная информация", guild=discord.Object(id=GUILD_ID))
async def slash_start(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_start_embed())

@tree.command(name="price", description="💰 Прайс-лист", guild=discord.Object(id=GUILD_ID))
async def slash_price(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_price_embed())

@tree.command(name="contact", description="📞 Контакты", guild=discord.Object(id=GUILD_ID))
async def slash_contact(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_contact_embed())

@tree.command(name="help", description="❓ Помощь", guild=discord.Object(id=GUILD_ID))
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(title="❓ **Помощь**", description="**Список команд**", color=NeonColors.PURPLE, timestamp=datetime.utcnow())
    embed.add_field(name="🔹 **Слэш**", value="`/start`, `/price`, `/contact`, `/ticket`, `/help`", inline=False)
    embed.add_field(name="🔸 **Префикс**", value="`!start`, `!price`, `!contact`, `!ticket`, `!help`", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ticket", description="📩 Панель тикетов (Админ)", guild=discord.Object(id=GUILD_ID))
async def slash_ticket(interaction: discord.Interaction):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_message(embed=create_ticket_panel_embed(), view=TicketPanelView())

@bot.command()
async def ticket(ctx):
    if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    await ctx.send(embed=create_ticket_panel_embed(), view=TicketPanelView())

@bot.command()
async def start(ctx): await ctx.send(embed=create_start_embed())
@bot.command()
async def price(ctx): await ctx.send(embed=create_price_embed())
@bot.command()
async def contact(ctx): await ctx.send(embed=create_contact_embed())
@bot.command()
async def help(ctx): await ctx.send(embed=discord.Embed(title="❓ **Помощь**", color=NeonColors.PURPLE, description="`!start`, `!price`, `!ticket`"))

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
    bot.add_view(CloseTicketView())  # ✅ Регистрируем кнопку закрытия
    
    print(f'✅ Бот запущен: {bot.user}')
    print(f'🎨 NeoSyntax Style: Активирован')

bot.run(BOT_TOKEN)
