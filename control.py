import os
import json
import asyncio
import subprocess

import discord
from discord.ext import commands


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

FIFO_PATH = "/run/teamspeak-ts-timer/control"

# Discord role allowed to control the TeamSpeak bots/timer
CONTROL_ROLE_ID = int(os.getenv("CONTROL_ROLE_ID", "0"))

# User allowed to control the bot through Direct Messages
DM_CONTROL_USER_ID = int(os.getenv("DM_CONTROL_USER_ID", "0"))

TS_BOTS = json.loads(os.getenv("TS_BOT_CONTAINERS", "[]"))


# ============================================================
# DISCORD BOT
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=";",
    intents=intents
)


# ============================================================
# PERMISSIONS
# Administrator OR CONTROL_ROLE_ID
# ============================================================

def can_control():
    async def predicate(ctx):

        # Direct Messages:
        # only the configured owner can control the timer
        if ctx.guild is None:
            return ctx.author.id == DM_CONTROL_USER_ID

        # Discord administrators always have access
        if ctx.author.guild_permissions.administrator:
            return True

        # Allow members with the control role
        return any(
            role.id == CONTROL_ROLE_ID
            for role in ctx.author.roles
        )

    return commands.check(predicate)


# ============================================================
# TIMER CONTROL
# ============================================================

def send_timer_command(command):
    if not os.path.exists(FIFO_PATH):
        return False

    try:
        fd = os.open(
            FIFO_PATH,
            os.O_WRONLY | os.O_NONBLOCK
        )

        with os.fdopen(fd, "w") as fifo:
            fifo.write(command + "\n")
            fifo.flush()

        return True

    except OSError:
        return False


# ============================================================
# TEAMSPEAK DOCKER CONTROL
# ============================================================

def docker_start_bots():
    result = subprocess.run(
        ["docker", "start", *TS_BOTS],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def docker_stop_bots():
    result = subprocess.run(
        ["docker", "stop", *TS_BOTS],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def get_running_bots():
    result = subprocess.run(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return []

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() in TS_BOTS
    ]


# ============================================================
# READY EVENT
# ============================================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("TeamSpeak TS Control ready.")


# ============================================================
# ;bots
# Start all configured TeamSpeak bots
# ============================================================

@bot.command()
@can_control()
async def bots(ctx):
    await ctx.reply(
        "🔄 Starting TeamSpeak bots..."
    )

    success = await asyncio.to_thread(
        docker_start_bots
    )

    if success:
        await ctx.reply(
            "🎧 TeamSpeak bots STARTED"
        )
    else:
        await ctx.reply(
            "❌ Failed to start TeamSpeak bots."
        )


# ============================================================
# ;start
# Start Jungle Timer ONLY
# ============================================================

@bot.command()
@can_control()
async def start(ctx):

    if send_timer_command("start"):
        await ctx.reply(
            "⏱️ Timer STARTED"
        )
    else:
        await ctx.reply(
            "❌ Timer service is offline."
        )


# ============================================================
# ;stop
# Stop Jungle Timer ONLY
# TeamSpeak bots stay online
# ============================================================

@bot.command()
@can_control()
async def stop(ctx):

    if send_timer_command("stop"):
        await ctx.reply(
            "🛑 Timer STOPPED"
        )
    else:
        await ctx.reply(
            "❌ Timer service is offline."
        )


# ============================================================
# ;off
# Stop Jungle Timer + shut down all 6 TeamSpeak bots
# ============================================================

@bot.command()
@can_control()
async def off(ctx):

    timer_stopped = send_timer_command("stop")

    success = await asyncio.to_thread(
        docker_stop_bots
    )

    if success:

        if timer_stopped:
            await ctx.reply(
                "🛑 Timer STOPPED\n"
                "💤 TeamSpeak bots OFFLINE"
            )

        else:
            await ctx.reply(
                "⚠️ Timer service was offline\n"
                "💤 TeamSpeak bots OFFLINE"
            )

    else:
        await ctx.reply(
            "❌ Failed to stop TeamSpeak bots."
        )


# ============================================================
# ;status
# Show timer service reachability + TS bot count
# ============================================================

@bot.command()
@can_control()
async def status(ctx):

    running = await asyncio.to_thread(
        get_running_bots
    )

    timer_online = send_timer_command("status")

    await ctx.reply(
        f"📡 Timer service: "
        f"{'ONLINE' if timer_online else 'OFFLINE'}\n"
        f"🎧 TeamSpeak bots: "
        f"{len(running)}/{len(TS_BOTS)} ONLINE"
    )


# ============================================================
# ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        (
            commands.MissingPermissions,
            commands.CheckFailure
        )
    ):
        await ctx.reply(
            "❌ You don't have permission to control the timer."
        )

    elif isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    else:
        print(
            f"Command error: "
            f"{type(error).__name__}: {error}"
        )

        await ctx.reply(
            f"❌ Error: `{error}`"
        )


# ============================================================
# START BOT
# ============================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing"
    )

bot.run(TOKEN)
