from discord import Intents, ext, Member

import config
import utils


def attach_core_module(bot):
    @bot.command(name="sync")
    async def sync(ctx: ext.commands.Context):
        await ctx.message.delete()
        await bot.tree.sync(guild=ctx.guild)

    @bot.command(name="info")
    async def info(ctx: ext.commands.Context):
        await ctx.reply(
            "You can chat with any currently deployed model and a bot from the list in this channel.\n"
            "Here are some commands you need to know:\n"
            "1. `/chat` — Starts conversation with the bot, served by deployed submission.\n"
            "2. `/info` — Prints this message.\n"
            "Enjoy ❤️"
        )

    @bot.event
    async def on_member_join(member: Member):
        developer_key = utils.get_existing_key(member.name)
        if not developer_key:
            developer_key = utils.create_new_key(user=member.name, max_submissions=2)
        await member.send(
            f"Welcome to the Chai LLM Competition, {member.name} 🔥💰🚀\n\n"
            "To submit solutions you need a developer key, here is yours:\n"
            f"🔑 `{developer_key}` 🔑\n\n"
            f"[Here is a Python Package](https://pypi.org/project/chai-guanaco/) that will help you deploy your "
            f"models to real users for evaluations.\n\n "
            f"P.S. Ask Tom (Team Chai) in Discord anything, he is kinda like a robot so never sleeps 🤖\n\n"
            f"Meanwhile, [introduce yourself](https://discord.com/channels/1104020730678612001/1104028332753957025) "
            f"and checkout our [leaderboard](https://discord.com/channels/1104020730678612001/1134163974296961195) "
            f"and [write-up channels](https://discord.com/channels/1104020730678612001/1112835255439740939) 🧠 🏆 "
        )


def create_bot():
    bot = ext.commands.Bot(command_prefix='/', intents=Intents.all(), aplication_id=config.APPLICATION_ID)
    return bot
