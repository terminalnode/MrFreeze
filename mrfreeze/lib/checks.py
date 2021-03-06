"""Various checks that can be added to commands."""

from typing import Union

import discord
from discord import Member
from discord.ext.commands import CommandError
from discord.ext.commands import Context


class MuteCheckFailure(CommandError):
    """Empty CheckFailure class for when the bot is muted in a server."""

    pass


async def is_owner_or_mod(ctx: Context) -> bool:
    """
    Check if author is bot owner and/or administrator in the server.

    The purpose of this check is to give the bot owner limited permissions
    to test various commands in the production environment. It should be
    limited to things that does not affect other members.

    Call with:
    @commands.check(checks.is_owner_or_mod)
    """
    is_mod = ctx.author.guild_permissions.administrator
    is_owner = await ctx.bot.is_owner(ctx.author)
    return is_mod or is_owner


async def is_owner(ctx: Context) -> bool:
    """
    Check if author is the bot owner.

    Call with:
    @commands.check(checks.is_owner)
    """
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        msg = f"{ctx.author.mention} You're not the boss of me! "
        msg += "<@!154516898434908160> Help I'm being opressed!!"
        await ctx.send(msg)
    return is_owner


async def is_owner_silent(ctx: Context) -> bool:
    """
    Check if author is the bot owner; silent version.

    Call with:
    @commands.check(checks.is_owner_silent)
    """
    return await ctx.bot.is_owner(ctx.author)


async def is_mod(caller: Union[Context, Member]) -> bool:
    """
    Check if the author is a mod.

    This check can be used with both context and member objects.
    Output varies depending on which object is used. For context
    objects the check will send a response to the user. For a
    member object the function simply returns True or False.

    Call with:
    @commands.check(checks.is_mod)
    """
    member_call = isinstance(caller, discord.member.Member)

    if member_call:
        mod_status = caller.guild_permissions.administrator

    else:
        mod_status = caller.author.guild_permissions.administrator

        # caller is a context object
        if caller.guild is None:
            await caller.send("Don't you try to sneak into my DMs and mod me!")
            return False

        if not mod_status:
            msg = f"{caller.author.mention} Only mods are allowed to use that command."
            await caller.send(msg)

    return mod_status


async def is_mod_silent(caller: Union[Context, Member]) -> bool:
    """
    Check if the author is a mod.

    This check will never return a message and as such is also
    suitable for uses other than as a function decorator. It works
    both with Member objects and context objects.

    Call with:
    @commands.check(checks.is_mod_silent)
    """
    if caller.guild is None:
        return False

    elif isinstance(caller, Member):
        return caller.guild_permissions.administrator

    else:
        return caller.author.guild_permissions.administrator


async def always_allow(ctx: Context) -> bool:
    """
    Return True, always. Used for debugging.

    Call with:
    @commands.check(checks.always_deny)
    """
    return True


async def always_deny(ctx: Context) -> bool:
    """
    Return False, always. Used for debugging.

    Call with:
    @commands.check(checks.always_deny)
    """
    return False
