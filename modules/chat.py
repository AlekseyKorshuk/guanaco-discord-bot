import discord
from discord.ext import commands

from chai_guanaco import chat as chai_chat
from chai_guanaco import metrics

import utils
import config


def attach_chat_module(bot):
    @bot.command(name="chat", description='Starts conversation with the bot, served by deployed submission.')
    async def chat(ctx: commands.Context, submission_id: str = None, bot_name: str = None):
        thread = await _create_initial_thread(ctx.channel)

        available_bots = utils.get_available_bots()
        available_models = _get_available_model()

        if not bot_name and not submission_id:
            bot_name = await _prompt_selection(thread, ctx.bot, available_bots,
                                               "Please select a bot by typing its number:")
            submission_id = await _prompt_selection(thread, ctx.bot, available_models,
                                                    'Now please select a model by typing its number:')
        if bot_name not in available_bots:
            return await thread.send("Invalid bot name provided!")
        if submission_id not in available_models:
            return await thread.send("Invalid model ID provided!")

        await _clean_up_thread(thread, bot_name, submission_id)
        bot_config = chai_chat.SubmissionChatbot._get_bot_config(bot_name)
        await thread.send(f"{bot_config.bot_label}: {bot_config.first_message}")

    @bot.event
    async def on_message(message: discord.Message):
        if message.channel.type != discord.ChannelType.public_thread:
            return await bot.process_commands(message)
        if message.channel.archived or message.channel.locked or message.author.id == bot.application_id:
            return
        await _process_conversation(message, bot)


async def _process_conversation(message, bot):
    bot_name, submission_id = utils.parse_bot_name_and_submission_id(message.channel.name)
    async with message.channel.typing():
        messages = await utils.get_messages(message.channel)
        bot_config = chai_chat.SubmissionChatbot._get_bot_config(bot_name)
        response = utils.get_response(messages, submission_id, bot_config, bot.application_id)
        await message.reply(f"{bot_config.bot_label}: {response}")


async def _create_initial_thread(channel):
    return await channel.create_thread(name="Initializing", type=discord.ChannelType.public_thread)


async def _prompt_selection(thread, bot, options, prompt_message):
    options_text = _get_options_text(options)
    await thread.send(prompt_message + "\n" + options_text)

    def check_thread(m):
        return m.channel == thread

    while True:
        choice_msg = await bot.wait_for('message', check=check_thread)
        if choice_msg.content.isdigit() and 0 < int(choice_msg.content) <= len(options):
            return options[int(choice_msg.content) - 1]
        await thread.send("Please write a number from the provided list!")


async def _clean_up_thread(thread, chosen_bot, chosen_model):
    new_thread_name = f"Chat with {chosen_bot} by {chosen_model}"
    await thread.edit(name=new_thread_name)
    async for message in thread.history(limit=None):
        if message.type == discord.MessageType.default:
            await message.delete()


def _get_options_text(options):
    options_text = "\n".join([f"{index + 1}. {option}" for index, option in enumerate(options)])
    return options_text


def _get_available_model():
    available_models = utils.get_available_models()
    leaderboard = metrics.cache(metrics.get_leaderboard, regenerate=False)(config.DEVELOPER_KEY)
    leaderboard = metrics._print_formatted_leaderboard(leaderboard, detailed=True)
    lb_submission_ids = leaderboard["submission_id"].tolist()

    def sort_key(model):
        try:
            return lb_submission_ids.index(model)
        except ValueError:
            return float('inf')

    available_models = sorted(available_models, key=sort_key)
    return available_models
