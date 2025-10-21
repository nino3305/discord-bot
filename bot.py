import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# 環境變數裡放兩隻 bot 的 token
TOKEN1 = os.getenv("DISCORD_TOKEN_1")
TOKEN2 = os.getenv("DISCORD_TOKEN_2")

# 各自的通知頻道
TARGET_CHANNEL_ID_1 = 1010848964981051424
TARGET_CHANNEL_ID_2 = 1010848964981051424

# ===== Bot 1：語音進出通知 =====
intents1 = discord.Intents.default()
intents1.message_content = True
intents1.voice_states = True
bot1 = commands.Bot(command_prefix="!", intents=intents1)

@bot1.event
async def on_ready():
    print(f"✅ Bot1 已登入：{bot1.user}")
    activity = discord.Game(name="原神")
    await bot1.change_presence(status=discord.Status.online, activity=activity)

@bot1.event
async def on_voice_state_update(member, before, after):
    channel = bot1.get_channel(TARGET_CHANNEL_ID_1)
    if not channel:
        return
    if before.channel is None and after.channel is not None:
        await channel.send(f":white_check_mark: <{member.display_name}> 加入了語音頻道 {after.channel.name}")


# ===== Bot 2：暱稱修改 + 語音進出 =====
intents2 = discord.Intents.default()
intents2.members = True
intents2.message_content = True
intents2.voice_states = True
bot2 = commands.Bot(command_prefix="?", intents=intents2)

@bot2.event
async def on_ready():
    print(f"✅ Bot2 已登入：{bot2.user}")
    try:
        synced = await bot2.tree.sync()
        print(f"📌 已同步 {len(synced)} 個斜線指令 (Bot2)")
    except Exception as e:
        print(f"❌ Bot2 同步失敗: {e}")

@bot2.tree.command(name="nick", description="修改某個成員的暱稱")
@app_commands.describe(user="要改暱稱的成員", new_nick="新的暱稱")
async def nick(interaction: discord.Interaction, user: discord.Member, new_nick: str):
    try:
        old_nick = user.nick if user.nick else user.name
        await user.edit(nick=new_nick)
        await interaction.response.send_message(
            f"✅ 已將 {user.name} 的暱稱由 `{old_nick}` 改成 `{new_nick}`"
        )
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ 我沒有權限更改這個成員的暱稱。")
    except discord.HTTPException:
        await interaction.response.send_message("⚠️ 更改暱稱失敗，請再試一次。")

@bot2.event
async def on_voice_state_update(member, before, after):
    channel = bot2.get_channel(TARGET_CHANNEL_ID_2)
    if not channel:
        return
    if before.channel is not None and after.channel is None:
        await channel.send(f":x: <{member.display_name}> 離開了語音頻道 {before.channel.name}")


# ===== 主程式，兩隻 bot 一起跑 =====
async def main():
    await asyncio.gather(
        bot1.start(TOKEN1),
        bot2.start(TOKEN2),
    )

asyncio.run(main())

