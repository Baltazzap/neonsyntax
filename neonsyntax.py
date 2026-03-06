import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import asyncio

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
    ORANGE = 0xFFA500
    YELLOW = 0xFFFF00
    GRAY = 0x808080
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
STAFF_TICKET_CATEGORY_ID = 1478003822352662600
SUPPORT_ROLE_ID = 1477952291439902791
MODERATOR_ROLE_ID = 1477952291439902791
MUTE_ROLE_ID = 1477952295869349888
LOGS_CHANNEL_ID = 1477964505546883184

OWNER_ID = 1477952025034752070

# ID каналов
CHANNEL_RULES = 1477955006203428919
CHANNEL_ORDER = 1477956383520325754
CHANNEL_PRICE = 1477955733864710255
CHANNEL_EXTRA = 1477955856279801969
CHANNEL_PAYMENT = 1477955908536635514
CHANNEL_GUARANTEE = 1477956108978098246

# Настройки анти-модерации
ANTI_SPAM_MESSAGES = 5
ANTI_SPAM_SECONDS = 5
ANTI_CAPS_PERCENT = 70
MUTE_DURATION_MINUTES = 10

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

# Файлы
TICKET_FILE = "tickets.json"
STAFF_TICKET_FILE = "staff_tickets.json"
WARNINGS_FILE = "warnings.json"
VIOLATIONS_FILE = "violations.json"

# Хранилище нарушений в памяти
violations = {}

# ==========================================
# 💾 РАБОТА С ФАЙЛАМИ
# ==========================================

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

def get_warnings():
    if os.path.exists(WARNINGS_FILE):
        with open(WARNINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_warnings(data):
    with open(WARNINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_warning(user_id, moderator, reason):
    data = get_warnings()
    if str(user_id) not in   # ✅ ИСПРАВЛЕНО: добавлено "data"
        data[str(user_id)] = []
    data[str(user_id)].append({
        'moderator': moderator,
        'reason': reason,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_warnings(data)
    return len(data[str(user_id)])

def get_user_warnings(user_id):
    data = get_warnings()
    return data.get(str(user_id), [])

def clear_warnings(user_id):
    data = get_warnings()
    if str(user_id) in   # ✅ ИСПРАВЛЕНО: добавлено "data"
        del data[str(user_id)]
        save_warnings(data)

def get_violations():
    global violations
    if os.path.exists(VIOLATIONS_FILE):
        with open(VIOLATIONS_FILE, 'r', encoding='utf-8') as f:
            violations = json.load(f)
    return violations

def save_violations():
    global violations
    with open(VIOLATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(violations, f, ensure_ascii=False, indent=2)

def add_violation(user_id, violation_type):
    global violations
    get_violations()
    now = datetime.now().timestamp()
    
    if str(user_id) not in violations:  # ✅ ИСПРАВЛЕНО: добавлено "violations"
        violations[str(user_id)] = []
    
    violations[str(user_id)].append({
        'type': violation_type,
        'time': now
    })
    
    violations[str(user_id)] = [v for v in violations[str(user_id)] if now - v['time'] < 3600]
    
    save_violations()
    return len(violations[str(user_id)])

def get_violation_count(user_id):
    global violations
    get_violations()
    now = datetime.now().timestamp()
    
    if str(user_id) not in violations:  # ✅ ИСПРАВЛЕНО: добавлено "violations"
        return 0
    
    recent = [v for v in violations[str(user_id)] if now - v['time'] < 3600]
    return len(recent)

# ==========================================
# 📋 ЛОГИРОВАНИЕ
# ==========================================

async def log_action(guild, action_type, moderator, target, reason=None, duration=None):
    channel = discord.utils.get(guild.channels, id=LOGS_CHANNEL_ID)
    if not channel:
        return
    
    color_map = {
        'ban': NeonColors.RED,
        'kick': NeonColors.ORANGE,
        'mute': NeonColors.GRAY,
        'unmute': NeonColors.GREEN,
        'warn': NeonColors.YELLOW,
        'clear_warn': NeonColors.BLUE,
        'embed': NeonColors.PURPLE,
        'auto_mute': NeonColors.RED,
        'anti_spam': NeonColors.YELLOW,
        'anti_caps': NeonColors.YELLOW
    }
    
    emoji_map = {
        'ban': '🔨',
        'kick': '👢',
        'mute': '🔇',
        'unmute': '🔊',
        'warn': '⚠️',
        'clear_warn': '✅',
        'embed': '📝',
        'auto_mute': '🤖',
        'anti_spam': '📢',
        'anti_caps': '🔠'
    }
    
    embed = discord.Embed(
        title=f"{emoji_map.get(action_type, '📝')} {action_type.upper()}",
        color=color_map.get(action_type, NeonColors.PURPLE),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="👤 **Модератор**", value=f"{moderator.mention} (`{moderator.id}`)", inline=True)
    if target:
        embed.add_field(name="🎯 **Пользователь**", value=f"{target.mention} (`{target.id}`)", inline=True)
    if duration:
        embed.add_field(name="⏱ **Длительность**", value=duration, inline=True)
    if reason:
        embed.add_field(name="📄 **Причина**", value=f"```{reason}```", inline=False)
    
    embed.set_footer(text=f"NeonSyntax | DevStudio • Лог действий")
    
    await channel.send(embed=embed)

# ==========================================
# 🛡️ АНТИ-МОДЕРАЦИЯ
# ==========================================

async def check_anti_spam(message):
    if message.author.bot:
        return False
    
    if any(role.id in [ADMIN_ROLE_ID, MODERATOR_ROLE_ID] for role in message.author.roles):
        return False
    
    user_messages = [m for m in message.channel.history(limit=ANTI_SPAM_MESSAGES + 1) 
                     if m.author == message.author and (datetime.utcnow() - m.created_at).total_seconds() < ANTI_SPAM_SECONDS]
    
    return len(user_messages) >= ANTI_SPAM_MESSAGES

async def check_anti_caps(message):
    if message.author.bot or len(message.content) < 10:
        return False
    
    if any(role.id in [ADMIN_ROLE_ID, MODERATOR_ROLE_ID] for role in message.author.roles):
        return False
    
    letters = [c for c in message.content if c.isalpha()]
    if not letters:
        return False
    
    caps = [c for c in letters if c.isupper()]
    caps_percent = (len(caps) / len(letters)) * 100
    
    return caps_percent >= ANTI_CAPS_PERCENT

async def handle_violation(message, violation_type):
    user = message.author
    count = add_violation(user.id, violation_type)
    
    try:
        await message.delete()
    except:
        pass
    
    if count == 1:
        embed = discord.Embed(
            title="⚠️ **ПРЕДУПРЕЖДЕНИЕ**",
            description=f"{user.mention}, вы нарушили правила сервера!\n\n**Нарушение:** `{violation_type}`\n\nПожалуйста, соблюдайте правила. При следующем нарушении вы получите **мут на 10 минут**.",
            color=NeonColors.YELLOW,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="NeonSyntax | DevStudio • Автомодерация")
        
        await message.channel.send(embed=embed, delete_after=30)
        
        await log_action(message.guild, violation_type, message.guild.me, user, f"Предупреждение #{count}")
        
    elif count >= 2:
        mute_role = discord.utils.get(message.guild.roles, id=MUTE_ROLE_ID)
        
        if mute_role:
            try:
                await user.add_roles(mute_role, reason=f"Авто-мут: {violation_type}")
                
                embed = discord.Embed(
                    title="🔇 **АВТОМАТИЧЕСКИЙ МУТ**",
                    description=f"{user.mention} получил мут на **{MUTE_DURATION_MINUTES} минут**.\n\n**Причина:** `{violation_type}` (повторное нарушение)",
                    color=NeonColors.RED,
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text="NeonSyntax | DevStudio • Автомодерация")
                
                await message.channel.send(embed=embed)
                
                await log_action(message.guild, 'auto_mute', message.guild.me, user, f"{violation_type} (повторное нарушение)", f"{MUTE_DURATION_MINUTES} мин.")
                
                await asyncio.sleep(MUTE_DURATION_MINUTES * 60)
                
                if mute_role in user.roles:
                    await user.remove_roles(mute_role, reason="Авто-мут истёк")
                    
                    unmute_embed = discord.Embed(
                        title="🔊 **МУТ СНЯТ**",
                        description=f"{user.mention}, ваш мут истёк. Пожалуйста, соблюдайте правила сервера.",
                        color=NeonColors.GREEN,
                        timestamp=datetime.utcnow()
                    )
                    await message.channel.send(embed=unmute_embed)
                    
                    await log_action(message.guild, 'unmute', message.guild.me, user, "Авто-мут истёк")
                
            except Exception as e:
                print(f"❌ Ошибка при выдаче мута: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if await check_anti_spam(message):
        await handle_violation(message, 'anti_spam')
        return
    
    if await check_anti_caps(message):
        await handle_violation(message, 'anti_caps')
        return
    
    await bot.process_commands(message)

# ==========================================
# 🎨 ШАБЛОНЫ EMBED
# ==========================================

def create_welcome_embed(member):
    embed = discord.Embed(
        title=f"👋 Добро пожаловать, {member.name}!",
        description="**Рады видеть тебя в NeonSyntax | DevStudio!**\n\nМы занимаемся профессиональной разработкой ботов для Discord и Telegram.",
        color=NeonColors.BLUE,
        timestamp=datetime.utcnow()
    )
    
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    else:
        embed.set_thumbnail(url=member.default_avatar.url)
    
    embed.add_field(
        name="🤖 **Наши услуги**", 
        value="• **Discord Боты** — модерация, экономика, магазины, тикеты\n• **Telegram Боты** — рассылки, магазины, интеграции, оплата", 
        inline=False
    )
    
    embed.add_field(
        name="📌 **Ознакомься с каналами**", 
        value=f"<#{CHANNEL_RULES}> — Правила сервера\n<#{CHANNEL_ORDER}> — Заказать услугу\n<#{CHANNEL_PRICE}> — Основной прайс-лист\n<#{CHANNEL_EXTRA}> — Дополнительные услуги\n<#{CHANNEL_PAYMENT}> — Условия оплаты\n<#{CHANNEL_GUARANTEE}> — Гарантии работы", 
        inline=False
    )
    
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
    embed.add_field(name="💼 **Специализации**", value="• **Discord** — боты для серверов\n• **Telegram** — боты для бизнеса", inline=False)
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
    embed.add_field(name="🥉 **Простые боты**", value="**от 5,000₽**\n• Простые команды\n• Приветствия\n• Базовая модерация\n• Срок: 3-7 дней", inline=True)
    embed.add_field(name="🥈 **Средней сложности**", value="**от 15,000₽**\n• Экономика сервера\n• Система тикетов\n• Интеграции API\n• Срок: 7-14 дней", inline=True)
    embed.add_field(name="🥇 **Сложные проекты**", value="**от 30,000₽**\n• Магазины с оплатой\n• Сложные системы\n• База данных\n• Срок: 14-30 дней", inline=True)
    embed.add_field(name="📞 **Связь**", value="Telegram: `@твой_ник`\nDiscord: `ТвойНик#0000`\nEmail: `info@neonsyntax.ru`", inline=False)
    embed.set_footer(text="💳 Предоплата 50% • Рассрочка возможна")
    return embed

def create_start_embed():
    embed = discord.Embed(
        title="🚀 **NeonSyntax | DevStudio**",
        description="**Профессиональная разработка ботов и автоматизация**\n\nМы создаём цифровые решения для вашего бизнеса с 2026 года.",
        color=NeonColors.PURPLE,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📊 **Проекты**", value="• **50+** успешных\n• **30+** клиентов\n• **98%** отзывов", inline=True)
    embed.add_field(name="⚡ **Технологии**", value="• Python 3.11+\n• Discord.py 2.0+\n• Aiogram 3.x", inline=True)
    embed.set_footer(text="NeonSyntax | DevStudio © 2026")
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
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Создать заказ", style=discord.ButtonStyle.green, custom_id="create_ticket_panel", emoji="📩")
    async def create_ticket_btn(self, interaction: discord.Interaction, button: Button):
        view = TicketTypeSelect(interaction.user)
        embed = discord.Embed(title="🎯 **Тип разработки**", description="Выберите тип бота:", color=NeonColors.PURPLE, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class StaffPanelView(View):
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
    embed.add_field(name="🔹 **Модерация**", value="`/ban` — Бан\n`/kick` — Кик\n`/mute` — Мут\n`/warn` — Предупреждение", inline=True)
    embed.add_field(name="🔸 **Владелец**", value="`/embed` — Кастомный Embed", inline=True)
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

# ==========================================
# 🔨 МОДЕРАЦИЯ
# ==========================================

def check_moderator(member):
    return any(role.id in [ADMIN_ROLE_ID, MODERATOR_ROLE_ID] for role in member.roles)

@tree.command(name="ban", description="🔨 Забанить пользователя", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для бана", reason="Причина бана")
async def slash_ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    if not check_moderator(interaction.user):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Модераторов и Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user == interaction.user:
        embed = discord.Embed(title="❌ **Ошибка**", description="Нельзя забанить себя!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user.top_role.position >= interaction.user.top_role.position:
        embed = discord.Embed(title="❌ **Ошибка**", description="Нельзя банить пользователя с ролью выше!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        await user.ban(reason=reason)
        embed = discord.Embed(title="✅ **Пользователь забанен**", description=f"{user.mention} забанен.", color=NeonColors.GREEN, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed)
        await log_action(interaction.guild, 'ban', interaction.user, user, reason)
    except Exception as e:
        embed = discord.Embed(title="❌ **Ошибка**", description=f"Не удалось забанить: {e}", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="kick", description="👢 Кикнуть пользователя", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для кика", reason="Причина кика")
async def slash_kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    if not check_moderator(interaction.user):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Модераторов и Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user == interaction.user:
        embed = discord.Embed(title="❌ **Ошибка**", description="Нельзя кикнуть себя!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user.top_role.position >= interaction.user.top_role.position:
        embed = discord.Embed(title="❌ **Ошибка**", description="Нельзя кикнуть пользователя с ролью выше!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        await user.kick(reason=reason)
        embed = discord.Embed(title="✅ **Пользователь кикнут**", description=f"{user.mention} кикнут.", color=NeonColors.GREEN, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed)
        await log_action(interaction.guild, 'kick', interaction.user, user, reason)
    except Exception as e:
        embed = discord.Embed(title="❌ **Ошибка**", description=f"Не удалось кикнуть: {e}", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="mute", description="🔇 Выдать мут пользователю", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для мута", duration="Длительность (минуты)", reason="Причина мута")
async def slash_mute(interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "Не указана"):
    if not check_moderator(interaction.user):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Модераторов и Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    mute_role = discord.utils.get(interaction.guild.roles, id=MUTE_ROLE_ID)
    if not mute_role:
        embed = discord.Embed(title="❌ **Ошибка**", description="Роль мута не найдена!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if mute_role in user.roles:
        embed = discord.Embed(title="❌ **Ошибка**", description="Пользователь уже замьючен!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        await user.add_roles(mute_role, reason=reason)
        embed = discord.Embed(title="✅ **Пользователь замьючен**", description=f"{user.mention} получил мут на {duration} мин.", color=NeonColors.GREEN, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed)
        await log_action(interaction.guild, 'mute', interaction.user, user, reason, f"{duration} мин.")
        
        await asyncio.sleep(duration * 60)
        if mute_role in user.roles:
            await user.remove_roles(mute_role, reason="Мут истёк")
            await log_action(interaction.guild, 'unmute', interaction.guild.me, user, "Мут истёк")
    except Exception as e:
        embed = discord.Embed(title="❌ **Ошибка**", description=f"Не удалось выдать мут: {e}", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="unmute", description="🔊 Снять мут с пользователя", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для снятия мута")
async def slash_unmute(interaction: discord.Interaction, user: discord.Member):
    if not check_moderator(interaction.user):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Модераторов и Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    mute_role = discord.utils.get(interaction.guild.roles, id=MUTE_ROLE_ID)
    if not mute_role:
        embed = discord.Embed(title="❌ **Ошибка**", description="Роль мута не найдена!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if mute_role not in user.roles:
        embed = discord.Embed(title="❌ **Ошибка**", description="Пользователь не имеет мута!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        await user.remove_roles(mute_role)
        embed = discord.Embed(title="✅ **Мут снят**", description=f"{user.mention} теперь может говорить.", color=NeonColors.GREEN, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed)
        await log_action(interaction.guild, 'unmute', interaction.user, user, "По команде модератора")
    except Exception as e:
        embed = discord.Embed(title="❌ **Ошибка**", description=f"Не удалось снять мут: {e}", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="warn", description="⚠️ Выдать предупреждение", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для предупреждения", reason="Причина предупреждения")
async def slash_warn(interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
    if not check_moderator(interaction.user):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Модераторов и Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    warn_count = add_warning(user.id, interaction.user.name, reason)
    
    embed = discord.Embed(title="✅ **Предупреждение выдано**", description=f"{user.mention} получил предупреждение.", color=NeonColors.YELLOW, timestamp=datetime.utcnow())
    embed.add_field(name="📊 **Всего предупреждений**", value=f"**{warn_count}**", inline=True)
    await interaction.response.send_message(embed=embed)
    await log_action(interaction.guild, 'warn', interaction.user, user, reason)

@tree.command(name="warnings", description="📋 Показать предупреждения пользователя", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для проверки")
async def slash_warnings(interaction: discord.Interaction, user: discord.Member):
    warnings = get_user_warnings(user.id)
    
    if not warnings:
        embed = discord.Embed(title="📋 **Предупреждения**", description=f"У {user.mention} нет предупреждений.", color=NeonColors.BLUE, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(title="📋 **Предупреждения**", description=f"У {user.mention} **{len(warnings)}** предупреждений.", color=NeonColors.YELLOW, timestamp=datetime.utcnow())
    
    for i, warn in enumerate(warnings, 1):
        embed.add_field(name=f"⚠️ **Предупреждение #{i}**", value=f"**Модератор:** {warn['moderator']}\n**Причина:** {warn['reason']}\n**Дата:** {warn['date']}", inline=False)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="clearwarnings", description="✅ Очистить предупреждения пользователя", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Пользователь для очистки")
async def slash_clearwarnings(interaction: discord.Interaction, user: discord.Member):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Админов!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    clear_warnings(user.id)
    embed = discord.Embed(title="✅ **Предупреждения очищены**", description=f"У {user.mention} удалены все предупреждения.", color=NeonColors.GREEN, timestamp=datetime.utcnow())
    await interaction.response.send_message(embed=embed)
    await log_action(interaction.guild, 'clear_warn', interaction.user, user, "Очистка предупреждений")

# ==========================================
# 👑 СИСТЕМА EMBED ДЛЯ ВЛАДЕЛЬЦА
# ==========================================

class EmbedModal(Modal, title="📝 Создание Embed"):
    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    title_input = TextInput(
        label="Заголовок",
        placeholder="Введите заголовок embed",
        required=False,
        max_length=256
    )
    
    description_input = TextInput(
        label="Описание",
        placeholder="Введите описание embed",
        required=False,
        style=discord.TextStyle.long,
        max_length=4000
    )
    
    color_input = TextInput(
        label="Цвет (HEX)",
        placeholder="#8A2BE2 или 8A2BE2",
        required=False,
        max_length=7
    )
    
    footer_input = TextInput(
        label="Текст футера",
        placeholder="Текст внизу embed",
        required=False,
        max_length=2048
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(timestamp=datetime.utcnow())
            
            if self.title_input.value:
                embed.title = self.title_input.value
            
            if self.description_input.value:
                embed.description = self.description_input.value
            
            if self.color_input.value:
                color = self.color_input.value.replace('#', '')
                embed.color = int(color, 16)
            else:
                embed.color = NeonColors.PURPLE
            
            if self.footer_input.value:
                embed.set_footer(text=self.footer_input.value)
            
            await self.channel.send(embed=embed)
            await log_action(interaction.guild, 'embed', interaction.user, None, f"Embed отправлен в {self.channel.mention}")
            
            embed_success = discord.Embed(
                title="✅ **Embed отправлен**",
                description="Ваш кастомный embed успешно отправлен в канал.",
                color=NeonColors.GREEN,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed_success, ephemeral=True)
            
        except Exception as e:
            embed_error = discord.Embed(
                title="❌ **Ошибка**",
                description=f"Не удалось отправить embed: {e}",
                color=NeonColors.RED,
                timestamp=datetime.utcnow()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

@tree.command(name="embed", description="📝 Создать кастомный embed (Только Владелец)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(channel="Канал для отправки embed")
async def slash_embed(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Владельца бота!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    modal = EmbedModal(channel)
    await interaction.response.send_modal(modal)

@bot.command()
async def embed(ctx, channel: discord.TextChannel = None):
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(title="❌ **Нет доступа**", description="Только для Владельца бота!", color=NeonColors.RED, timestamp=datetime.utcnow())
        await ctx.send(embed=embed)
        return
    
    if channel is None:
        channel = ctx.channel
    
    embed = discord.Embed(
        title="❌ **Только слэш команда**",
        description="Используйте `/embed` для создания кастомного embed.",
        color=NeonColors.RED,
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command()
async def ban(ctx, user: discord.Member, *, reason="Не указана"):
    if not check_moderator(ctx.author):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    try:
        await user.ban(reason=reason)
        await ctx.send(embed=discord.Embed(title="✅ **Забанен**", description=f"{user.mention}", color=NeonColors.GREEN))
        await log_action(ctx.guild, 'ban', ctx.author, user, reason)
    except Exception as e:
        await ctx.send(embed=discord.Embed(title="❌ **Ошибка**", description=str(e), color=NeonColors.RED))

@bot.command()
async def kick(ctx, user: discord.Member, *, reason="Не указана"):
    if not check_moderator(ctx.author):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    try:
        await user.kick(reason=reason)
        await ctx.send(embed=discord.Embed(title="✅ **Кикнут**", description=f"{user.mention}", color=NeonColors.GREEN))
        await log_action(ctx.guild, 'kick', ctx.author, user, reason)
    except Exception as e:
        await ctx.send(embed=discord.Embed(title="❌ **Ошибка**", description=str(e), color=NeonColors.RED))

@bot.command()
async def mute(ctx, user: discord.Member, duration: int, *, reason="Не указана"):
    if not check_moderator(ctx.author):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    mute_role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if mute_role:
        await user.add_roles(mute_role)
        await ctx.send(embed=discord.Embed(title="✅ **Замьючен**", description=f"{user.mention} на {duration} мин.", color=NeonColors.GREEN))
        await log_action(ctx.guild, 'mute', ctx.author, user, reason, f"{duration} мин.")

@bot.command()
async def unmute(ctx, user: discord.Member):
    if not check_moderator(ctx.author):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    mute_role = discord.utils.get(ctx.guild.roles, id=MUTE_ROLE_ID)
    if mute_role:
        await user.remove_roles(mute_role)
        await ctx.send(embed=discord.Embed(title="✅ **Мут снят**", description=f"{user.mention}", color=NeonColors.GREEN))
        await log_action(ctx.guild, 'unmute', ctx.author, user, "По команде")

@bot.command()
async def warn(ctx, user: discord.Member, *, reason="Не указана"):
    if not check_moderator(ctx.author):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    warn_count = add_warning(user.id, ctx.author.name, reason)
    await ctx.send(embed=discord.Embed(title="✅ **Предупреждение**", description=f"{user.mention} ({warn_count} всего)", color=NeonColors.YELLOW))
    await log_action(ctx.guild, 'warn', ctx.author, user, reason)

@bot.command()
async def warnings(ctx, user: discord.Member):
    warnings = get_user_warnings(user.id)
    if not warnings:
        await ctx.send(embed=discord.Embed(title="📋 **Предупреждения**", description=f"У {user.mention} нет предупреждений.", color=NeonColors.BLUE))
        return
    embed = discord.Embed(title="📋 **Предупреждения**", description=f"У {user.mention} **{len(warnings)}** предупреждений.", color=NeonColors.YELLOW)
    for i, warn in enumerate(warnings, 1):
        embed.add_field(name=f"⚠️ #{i}", value=f"{warn['moderator']}: {warn['reason']}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def clearwarnings(ctx, user: discord.Member):
    if not any(role.id == ADMIN_ROLE_ID for role in ctx.author.roles):
        await ctx.send(embed=discord.Embed(title="❌ **Нет доступа**", color=NeonColors.RED))
        return
    clear_warnings(user.id)
    await ctx.send(embed=discord.Embed(title="✅ **Очищено**", description=f"У {user.mention} удалены все предупреждения.", color=NeonColors.GREEN))
    await log_action(ctx.guild, 'clear_warn', ctx.author, user, "Очистка")

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
async def start(ctx): 
    await ctx.send(embed=create_start_embed())

@bot.command()
async def price(ctx): 
    await ctx.send(embed=create_price_embed())

@bot.command()
async def contact(ctx): 
    await ctx.send(embed=create_contact_embed())

@bot.command()
async def help(ctx): 
    embed = discord.Embed(title="❓ **Помощь**", description="**Команды бота**", color=NeonColors.PURPLE, timestamp=datetime.utcnow())
    embed.add_field(name="🔹 **Инфо**", value="`!start` — Главная\n`!price` — Прайс\n`!contact` — Контакты", inline=True)
    embed.add_field(name="🔸 **Тикеты**", value="`!ticket` — Панель заказов\n`!staff` — Панель заявок", inline=True)
    embed.add_field(name="🔹 **Модерация**", value="`!ban` — Бан\n`!kick` — Кик\n`!mute` — Мут\n`!warn` — Предупреждение", inline=True)
    embed.add_field(name="🔸 **Владелец**", value="`/embed` — Кастомный Embed", inline=True)
    embed.set_footer(text="NeonSyntax | DevStudio © 2026")
    await ctx.send(embed=embed)

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
    
    get_violations()
    
    status = discord.Activity(
        type=discord.ActivityType.watching,
        name="!start /start | !help /help"
    )
    await bot.change_presence(activity=status)
    
    print(f'✅ Бот запущен: {bot.user}')
    print(f'🆔 ID Бота: {bot.user.id}')
    print(f'🎨 NeonSyntax | DevStudio © 2026')
    print(f'📩 Система заказов: Готова')
    print(f'🛡️ Система стаффа: Готова')
    print(f'🔨 Система модерации: Готова')
    print(f'📋 Система логов: Готова')
    print(f'👑 Система embed: Готова')
    print(f'🤖 Авто-модерация: Активирована')
    print(f'🎧 Статус: Слушает !start /start | !help /help')

bot.run(BOT_TOKEN)
