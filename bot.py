import discord
from discord.ext import commands
from botutils import *
import sqlite3

def init():
    global TOKEN, client, conn, c, img_link
    config = open('config.txt', 'r')
    data = config.read().strip().split('\n')
    for i in range(len(data)):
        data[i] = data[i].split(': ')

    TOKEN, img_link, db_dir, prefix = [data[i][1] for i in range(len(data))]
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()

    client = commands.Bot(command_prefix=prefix)
    client.remove_command('help')

    config.close()

init()

# Constant declarations
NAME, EN_NAME, JP_NAME, SEX, ROLE, DECKS, USER = [i for i in range(7)]  # Table indexes
TABLE_NAME, FULL_GEN, GEN_COLOUR = [i for i in range(3)]    # gen_attributes indexes
L_GEN, L_ROLE, L_SHOW_TAKEN = [i+1 for i in range(3)] # list arg indexes
BREAKLINE, TAB = '\n', '\t'
gen_attributes = {
    'dm': ('dm', 'Duel Monsters', discord.Colour(0x9742c9)),
    'gx': ('gx', 'GX', discord.Colour(0xcc240e)),
    '5ds': ('fiveds', "5D's", discord.Colour(0xbc681a)),
    'zexal': ('zexal', 'ZeXal', discord.Colour(0xffcf53)),
    'arcv': ('arcv', 'Arc-V', discord.Colour(0x69c42d)),
    'vrains': ('vrains', 'VRAINS', discord.Colour(0x3b7be2))
}


async def create_role(author, role_name, role_colour):
    role = await client.create_role(author.server, name=role_name, colour=role_colour)
    return role

def get_character_info(character):
    for gen in gen_attributes:
        table = gen_attributes[gen][TABLE_NAME]
        c.execute('SELECT * FROM {} WHERE name="{}"'.format(table, character[0].upper()+character[1:]))
        row = c.fetchall()
        if len(row) > 0:
            return table, row[0]

    return None, []

def get_user_character(user):
    for gen in gen_attributes:
        table = gen_attributes[gen][TABLE_NAME]
        c.execute('SELECT * FROM {} WHERE user="{}"'.format(table, user))
        row = c.fetchall()
        if len(row) > 0:
            return row[0][NAME]

    return None


@client.command(pass_context=True)
async def char(ctx, *args):
    def char_help():
        command = '>>char '
        message = bold('Usage:') + BREAKLINE
        message += bold(command + 'list (generation) [main | villain | side | all] [all]') + BREAKLINE
        message += bold(command + 'take (character)') + BREAKLINE
        message += bold(command + 'status (character)') + BREAKLINE
        message += bold(command + 'leave') + BREAKLINE
        message += 'For more information see ' + bold('>>help')
        return message


    async def char_list(): #########################################################
        def list_help():
            message = 'Usage: ' + markdown('>>char list (dm | gx | 5ds | zexal | arcv | vrains) [main | villain | side | all] [all]')
            return message

        def error_wrong_gen():
            message = "{} is not a valid parameter. correct parameters:".format(args[1]) + BREAKLINE
            for gen in gen_attributes:
                message += gen + ' '
            return message

        try:
            if args[L_GEN] not in gen_attributes:
                await client.say(error_wrong_gen())
                return
        except IndexError:
            await client.say(list_help())
            return


        condition = 'SELECT name FROM {}'.format(gen_attributes[args[L_GEN]][TABLE_NAME])
        if L_ROLE not in range(len(args)):
            condition += ' WHERE (role="main" OR role="villain")'
        elif args[L_ROLE] in ['main', 'villain', 'side'] and not args[L_ROLE] == 'all':
            condition += ' WHERE role="{}"'.format(args[L_ROLE])

        if L_SHOW_TAKEN not in range(len(args)):
            if L_ROLE in range(len(args)) and args[L_ROLE] == 'all':
                condition += ' WHERE'
            else:
                condition += ' AND'
            condition += ' user="Nobody"'

        c.execute(condition)

        message = ''
        for name in c.fetchall():
            message += markdown(name[0]) + BREAKLINE

        await client.say(bold('Use >>char take (name) to become one of these characters!'), embed=get_embed('Yu-Gi-Oh! ' + gen_attributes[args[L_GEN]][FULL_GEN] + ' characters', message, gen_attributes[args[L_GEN]][GEN_COLOUR]))


    async def char_take(): #########################################################
        def take_help():
            message = 'Usage: ' + markdown('>>char take (character)')
            return message

        async def give_role(author, gen):
            role = discord.utils.get(author.server.roles, name=gen_attributes[gen][FULL_GEN])
            if role is None:
                role = await create_role(author, gen_attributes[gen][FULL_GEN], gen_attributes[gen][GEN_COLOUR])

            await client.add_roles(author, role)

        try:
            args[1]
        except IndexError:
            await client.say(take_help())
            return

        character = args[1][0].upper() + args[1][1:]
        author = ctx.message.author
        table, row = get_character_info(character)

        if len(row) == 0:
            await client.say("Couldn't find any duelist named {}.".format(character))
            return

        if get_user_character(str(author)) is not None:
            await client.say("You already have character! Use `>>char leave` to leave your current one so you can get another!")

        elif row[USER] == "Nobody":
            c.execute('UPDATE {} SET user="{}" WHERE user="Nobody" AND name="{}"'.format(table, str(author), character))
            conn.commit()
            congrats = 'You are now {}!'.format(character)
            await client.say(embed=get_embed('', congrats, discord.Colour.blue()))
            await give_role(author, table)
            await client.change_nickname(author, character)

        else:
            await client.say('{} is already taken.'.format(character))


    async def char_leave():	########################################################
        author = ctx.message.author
        character = get_user_character(author)

        if not character == None:
            table, row = get_character_info(character)
            c.execute('UPDATE {} SET user="Nobody" WHERE user="{}"'.format(table, author))
            conn.commit()
            await client.say(embed=get_embed('', "You aren't {} anymore!".format(row[0]), discord.Colour.blue()))
            role = discord.utils.get(author.server.roles, name=gen_attributes[table][FULL_GEN])
            await client.remove_roles(author, role)
            await client.change_nickname(author, '')

        else:
            await client.say("You don't have a character!")


    async def char_status(): #######################################################
        def format_decks():
            decks = row[DECKS].split('/')
            message = ''
            for d in decks:
                message += d + BREAKLINE

            return message

        table, row = get_character_info(args[0])
        for key in gen_attributes:
            if table in gen_attributes[key]:
                break

        message = bold('Full EN name: ') + row[EN_NAME] + BREAKLINE
        message += bold('Full JP name: ') + row[JP_NAME] + BREAKLINE
        message += bold('Sex: ') + row[SEX] + BREAKLINE
        message += bold('Role: ') + row[ROLE][0].upper() + row[ROLE][1:]

        output = get_embed('Yu-Gi-Oh! {} - {}'.format(gen_attributes[key][FULL_GEN], row[NAME]), message, gen_attributes[key][GEN_COLOUR])
        output.add_field(name='Decks:', value=format_decks(), inline=True)
        output.add_field(name='Taken by:', value=row[USER], inline=True)
        img_url = img_link.format(row[NAME])
        output.set_thumbnail(url=img_url)

        await client.say(embed=output)


    try:
        if args[0] == 'list':
            await char_list()
        elif args[0] == 'take':
            await char_take()
        elif args[0] == 'leave':
            await char_leave()
        else:
            await char_status()
    except IndexError:
        await client.say(char_help())


@client.command(pass_context=True)
async def status(ctx):
    author = ctx.message.author
    character = get_user_character(author)

    if character is None:
        await client.say(embed=get_embed('', 'You are not assigned to a character! Use `>>char take (character)` to get one!', discord.Colour.blue()))
    else:
        await client.say(embed=get_embed('', 'You are {}!'.format(character), discord.Colour.blue()))


@client.command()
async def help():
    message = 'A bot that helps character roleplaying!' + BREAKLINE + BREAKLINE
    message += bold('Usage:') + BREAKLINE
    message += bold('>>char: ') + 'Lets you see and pick a Yu-Gi-Oh! character.' + BREAKLINE
    message += bold('>>status: ') + "Checks wether you're assigned to a character or not"

    await client.say(message)


client.run(TOKEN)
