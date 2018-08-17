import discord
from discord.ext import commands
import collections, random, signal, re
import traceback, sys, asyncio

# Importing commands from ./botfunctions
from botfunctions import *

bot = commands.Bot(command_prefix='!')

# Cogs starting with cmd contains only one command,
# cogs starting with cmds has multiple commands sharing some common trait.
load_cogs = [ 'cogs.cmds_owner',    # Owner-only commands
              'cogs.cmds_mod',      # Mod-only commands.
              'cogs.cmds_links',    # !dummies, !readme, !source
              'cogs.cmd_mrfreeze',  # !mrfreeze
              'cogs.cmd_quote',     # !quote
              'cogs.cmd_rules',     # !rules
              'cogs.help_temp' ]    # !temp, DM instructions for automatic temp conversion.

# We don't use this.
bot.remove_command("help")

# Here's where the actual loading of the cogs go.
if __name__ == '__main__':
    for cog in load_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load extension {cog}.', file=sys.stderr)
            traceback.print_exc()

# This will be printed in the console once the
# bot has been connected to discord.
@bot.event
async def on_ready():
    print ('We have logged in as {0.user}'.format(bot))
    print ('User name: ' + str(bot.user.name))
    print ('User ID: ' + str(bot.user.id))
    print ('-----------')

    # Creating dict of all pins in channels in the guilds.
    global pinsDict
    pinsDict = None
    pinsDict = await pinlists.create_dict(bot.guilds)

    # Set activity to "Listening to your commands"
    await bot.change_presence(status=None, activity=
        discord.Activity(name='your commands...', type=discord.ActivityType.listening))

    # Greetings message for all the servers now that all is setup.
    for i in bot.guilds:
        try:
            bot_trash = discord.utils.get(i.channels, name='bot-trash')
            await bot_trash.send(':wave: ' + native.mrfreeze())
        except:
            print ('ERROR: No channel bot-trash in ' + i.name + '. Can\'t greet them.')

# Certain events, namely temp, depends on checking for temperature statements in
# all messages sent to the chat. If a command is detected before that the command
# will run instead.
@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    # the trailing space let's us match temperatures at the end of the message.
    tempstatement = re.search('(( -)?\d+[,.]?(\d+)?) ?(?:°?d(eg)?(egrees)?|°?c(elcius)?(elsius)?(ivilized( units)?)?(ivilised( units)?)?(u)?|' +
                              '°?f(ahrenheit)?(reedom( units)?)?(u)?|°?k(elvin)?|°?r(ankine)?)[^\w]',
                              ' ' + message.content.lower() + ' ')

    if message.author == bot.user:
        pass # never do anything the bot says.

    elif ctx.valid: # this is a command, we should invoke it.
        await bot.invoke(ctx)

    elif tempstatement != None:
        await temp.convert(ctx, tempstatement)

# Message when people leave.
@bot.event
async def on_member_remove(member):
    mod_channel = discord.utils.get(member.guild.channels, name='mod-discussion')
    member_name = str(member.name + '#' + str(member.discriminator))
    embed = discord.Embed(color=0x00dee9)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field( name='A member has left the server! :sob:',
                     value=('**%s#%s** is a trechorous smud who\'s turned their back on %s.' %
                     (member.name, str(member.discriminator), member.guild.name)) )
    await mod_channel.send(embed=embed)

# Command errors
@bot.event
async def on_command_error(ctx, error):
    get_command = re.compile('!\w+')
    command = get_command.match(ctx.message.content).group()
    if isinstance(error, commands.CheckFailure):
        print(native.get_author(ctx) + 'tried to invoke command !' + str(ctx.command) + ' which resulted in a check failure.')
    else:
        print(error)

# A message was pinned.
@bot.event
async def on_guild_channel_pins_update(channel, last_pin):
    global pinsDict

    # Unfortunately we have to cast an empty return
    # if the dict isn't finished yet.
    if pinsDict == None:
        print ('The PinsDict isn\'t finished yet!')
        return

    # The channel might be new, if so we need to create an entry for it.
    try:
        pinsDict[channel.guild.id][channel.id]
    except KeyError:
        pinsDict[channel.guild.id][channel.id] = 0

    # For comparisson between the two. These numbers will be
    # used to determine whether a pin was added or removed.
    channel_pins = await channel.pins()
    old_pins = pinsDict[channel.guild.id][channel.id]
    new_pins = len(channel_pins)

    # Was a new pin added?
    # If a pin was added when the bot was starting up, this won't work.
    # But it will work the next time as the pinsDict is updated.
    was_added = False
    if new_pins > old_pins:
        was_added = True

    # Updating the list of pins.
    pinsDict[channel.guild.id][channel.id] = new_pins

    if was_added:
        message = channel_pins[0]
        pinned_message = discord.Embed(description = message.content, color=0x00dee9)
        pinned_message.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        await channel.send('The following message was just pinned:\n', embed=pinned_message)

### Program ends here
# Client.run with the bots token
# Place your token in a file called 'token'
# Put the file in the same directory as the bot.
try:
    token = open('token', 'r').read().strip()
    bot.run(token, bot=True, reconnect=True)
except:
    print ('\nERROR: BOT TOKEN MISSING\n' +
           'Please put your bot\'s token in a separate text file called \'token\'.\n' +
           'This file should be located in the same directory as the bot files.\n')
    sys.exit(0)

# Graceful exit
def signal_handler(sig, frame):
        print('\n\nYou pressed Ctrl+C!\nI will now do like the tree, and get out of here.')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.pause()
