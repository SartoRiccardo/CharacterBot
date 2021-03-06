import discord


def bold(string):
    return '**{}**'.format(string)


def underline(string):
    return '_{}_'.format(string)


def markdown(string):
    return '`{}`'.format(string)


def markdown_multiline(string):
    return '```{}```'.format(string)


def strikethrough(string):
    return '~~{}~~'.format(string)


def underline(string):
    return '__{}__'.format(string)


def first_upper(string):
    return string[0].upper() + string[1:]


def get_embed(title, message, color):
    embed = discord.Embed(
        title = title,
        description = message,
        colour = color
    )
    return embed