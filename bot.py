import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def is_mod(interaction: discord.Interaction) -> bool:
    return any(role.name == "Discord Management Team" for role in interaction.user.roles)

@bot.event
async def on_ready():
    await tree.sync()

@tree.command(name="say", description="Send a message to a selected channel.")
@app_commands.check(is_mod)
@app_commands.describe(channel="Channel to send the message to", message="Message to send")
async def say_in_channel(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    await channel.send(message)
    await interaction.response.send_message(f"✅ Message sent to {channel.mention}", ephemeral=True)

@say_in_channel.error
async def say_in_channel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
        
@bot.command()
async def say(ctx, *, message: str):
    channel = discord.utils.get(ctx.guild.text_channels, name="📃┃meeting-notices")
    await channel.send(message)

def create_log_embed(title, description, color, author=None, channel=None, message_id=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    if author:
        embed.add_field(name="Message author", value=author.mention, inline=False)
    if channel:
        embed.add_field(name="Channel", value=channel.mention, inline=False)
    if message_id:
        embed.set_footer(text=f"ID: {message_id}")
    return embed

@bot.event
async def on_message_edit(before, after):
    log_channel = discord.utils.get(after.guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="✏️ Message Edited",
            description=f"**Before:** {before.content or '*Empty*'}\n**After:** {after.content or '*Empty*'}",
            color=discord.Color.orange(),
            author=after.author,
            channel=after.channel,
            message_id=after.id
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    log_channel = discord.utils.get(message.guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="🗑️ Message Deleted",
            description=message.content or "*Empty message*",
            color=discord.Color.red(),
            author=message.author,
            channel=message.channel,
            message_id=message.id
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    log_channel = discord.utils.get(after.guild.text_channels, name="logs")
    if log_channel and before.roles != after.roles:
        before_roles = ", ".join([r.name for r in before.roles if r.name != "@everyone"])
        after_roles = ", ".join([r.name for r in after.roles if r.name != "@everyone"])
        embed = create_log_embed(
            title="🛡️ Roles Updated",
            description=f"**Before:** {before_roles or 'None'}\n**After:** {after_roles or 'None'}",
            color=discord.Color.blue(),
            author=after
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    welcome_channel = member.guild.system_channel
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if welcome_channel:
        await welcome_channel.send(
            f"Welcome {member.mention} to **{member.guild.name}**! Please change your username to your name and grade. Contact an Admin if you need help."
        )
    if log_channel:
        embed = create_log_embed(
            title="✅ Member Joined",
            description=f"{member.mention} joined the server.",
            color=discord.Color.green(),
            author=member
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = discord.utils.get(member.guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="❌ Member Left or Kicked",
            description=f"{member} is no longer in the server.",
            color=discord.Color.red(),
            author=member
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="🔨 Member Banned",
            description=f"{user} was banned from the server.",
            color=discord.Color.dark_red(),
            author=user
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="♻️ Member Unbanned",
            description=f"{user} was unbanned.",
            color=discord.Color.teal(),
            author=user
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    log_channel = discord.utils.get(channel.guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="📁 Channel Created",
            description=f"{channel.mention} was created.",
            color=discord.Color.green(),
            channel=channel
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    log_channel = discord.utils.get(channel.guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="🗑️ Channel Deleted",
            description=f"{channel.name} was deleted.",
            color=discord.Color.red(),
            channel=channel
        )
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_update(before, after):
    log_channel = discord.utils.get(after.guild.text_channels, name="logs")
    if log_channel:
        changes = []
        if before.name != after.name:
            changes.append(f"✏️ Renamed: `{before.name}` → `{after.name}`")
        if changes:
            embed = create_log_embed(
                title="⚙️ Channel Updated",
                description="\n".join(changes),
                color=discord.Color.blurple(),
                channel=after
            )
            await log_channel.send(embed=embed)

@commands.has_permissions(manage_messages=True)
@bot.command()
async def clear(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("❗ You can only delete between 1 and 100 messages.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")
    if log_channel:
        embed = create_log_embed(
            title="🧹 Messages Cleared",
            description=f"{ctx.author.mention} deleted {len(deleted) - 1} messages in {ctx.channel.mention}.",
            color=discord.Color.orange(),
            author=ctx.author,
            channel=ctx.channel
        )
        await log_channel.send(embed=embed)

bot.run(token)
