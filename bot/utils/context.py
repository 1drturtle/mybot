from discord.ext import commands
import discord
import asyncio
from utils.functions import create_default_embed, try_delete


class CustomContext(commands.Context):
    @property
    def guild_id(self):
        return getattr(self.guild, 'id', None)

    @property
    def embed(self):
        return create_default_embed(self)

    async def prompt(self, title: str, description: str, timeout=30, sendable=None) -> str:
        """
        Prompts the Context author for a question, and returns the result. Returns None if they do not respond.
        :param str title: The title of the prompt
        :param str description: The description of the prompt
        :param int timeout:
        :param discord.Messagable sendable: Where to send the message. (Optional, defaults to context channel.)
        :return: The response, or None
        :rtype: str or None
        """
        embed = create_default_embed(self)
        embed.title = title or 'Question Prompt'

        if not description:
            raise Exception('Missing required argument Description on prompt.')
        embed.description = description

        if sendable:
            question = await sendable.send(embed=embed)
        else:
            question = await self.channel.send(embed=embed)

        def check(msg: discord.Message):
            return msg.author.id == self.author.id and msg.channel.id == self.channel.id

        try:
            result = await self.bot.wait_for('message', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            return None

        content = result.content
        await try_delete(question)
        await try_delete(result)

        return content or None
