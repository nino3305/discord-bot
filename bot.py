import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta


# =========================
# 兩隻 BOT 使用的 Token 與頻道
# =========================
TOKEN1 = os.getenv("DISCORD_TOKEN_1")  # Bot 1
TOKEN2 = os.getenv("DISCORD_TOKEN_2")  # Bot 2

TARGET_CHANNEL_ID = 1010848964981051424   # 統一用同一個文字頻道通知


# =========================
# Bot 1：語音進出 + 冷卻
# =========================
intents1 = discord.Intents.default()
intents1.message_content = True
intents1.voice_states = True
bot1 = commands.Bot(command_prefix="!", intents=intents1)

# 冷卻時間（例如 60 秒內不重複通知）
VOICE_COOLDOWN = timedelta(hours=2)

# 記錄每個人最後一次通知時間
last_voice_notify = {}   # key = (guild_id, user_id)


@bot1.event
async def on_ready():
    print(f"✅ Bot1 已登入：{bot1.user}")
    await bot1.change_presence(activity=discord.CustomActivity(name="(･ω<)☆"))


@bot1.event
async def on_voice_state_update(member, before, after):
    channel = bot1.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        return
    
    now = datetime.utcnow()
    key = (member.guild.id, member.id)

    # ========== 加入語音 ==========
    if before.channel is None and after.channel is not None:
        last_time = last_voice_notify.get(key)

        # 冷卻判定
        if last_time and now - last_time < VOICE_COOLDOWN:
            return
        
        last_voice_notify[key] = now   # 更新時間
        await channel.send(f":white_check_mark: <{member.display_name}> 加入了語音頻道 {after.channel.name}♭")

    # ========== 離開語音 ==========
    elif before.channel is not None and after.channel is None:
        last_time = last_voice_notify.get(key)

        # 冷卻判定
        if last_time and now - last_time < VOICE_COOLDOWN:
            return
        
        last_voice_notify[key] = now
        await channel.send(f":x: <{member.display_name}> 離開了語音頻道 {before.channel.name}♪")


# =========================
# Bot 2：暱稱修改 (Slash 指令)
# =========================
intents2 = discord.Intents.default()
intents2.members = True
intents2.message_content = True
bot2 = commands.Bot(command_prefix="?", intents=intents2)


@bot2.event
async def on_ready():
    print(f"✅ Bot2 已登入：{bot2.user}")
    await bot2.change_presence(activity=discord.CustomActivity(name="正在書寫 如我所書"))
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
            f"👤 {interaction.user.mention} 已將 {user.mention} 的暱稱由 `{old_nick}` 改成 `{new_nick}`"
        )
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ 我沒有權限更改這個成員的暱稱。")
    except discord.HTTPException:
        await interaction.response.send_message("⚠️ 更改暱稱失敗，請再試一次。")


# =========================
# 主程式：讓兩隻 bot 同時跑
# =========================
async def main():
    await asyncio.gather(
        bot1.start(TOKEN1),
        bot2.start(TOKEN2),
    )

asyncio.run(main())


