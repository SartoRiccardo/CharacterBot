import discord
from discord.ext import commands
import sqlite3

TOKEN = 'NDc1NzA3MDY4MTk2NTg1NDcz.Dkn0Cg.joaqG_doRLcK3h2kSuODyzv7bpo'
client = commands.Bot(command_prefix = '>>')
client.remove_command('help')
conn = sqlite3.connect('characters.db')
c = conn.cursor()

BREAKLINE = '\n'
TAB = '\t'
generations = ('dm', 'gx', 'fiveds', 'zexal', 'arcv', 'vrains')
expanded_names = {
	'dm': 'Duel Monsters',
	'gx': 'GX',
	'fiveds': "5Ds",
	'zexal': 'ZeXal',
	'arcv': 'Arc-V',
	'vrains': 'VRAINS'
}
roles = {
	'dm': ('Duel Monsters', discord.Colour(0x9742c9)),
	'gx': ('GX', discord.Colour(0xcc240e)),
	'fiveds': ("5Ds", discord.Colour(0xbc681a)),
	'zexal': ('ZeXal', discord.Colour(0xffcf53)),
	'arcv': ('Arc-V', discord.Colour(0x69c42d)),
	'vrains': ('VRAINS', discord.Colour(0x3b7be2))
}

@client.event
async def on_ready():
	print("Logged in as", end=' ')
	print("{}".format(client.user.name))
	print("------------------------")


def get_embed(title, message, color):
	embed = discord.Embed(
		title = title,
		description = message,
		colour = color
	)
	return embed

def bold(string):
	return '**' + string + '**'

async def create_role(author, gen):
	return await client.create_role(author.server, name=roles[gen][0], colour=roles[gen][1])

def get_character_info(character):
	table = ''
	for table in expanded_names:
		c.execute('SELECT * FROM {} WHERE name="{}"'.format(table, character[0].upper()+character[1:]))
		row = c.fetchall()
		if len(row) > 0:
			return table, row[0]

	return table, []

def get_user_character(user):
	for table in expanded_names:
		c.execute('SELECT * FROM {} WHERE taken="{}"'.format(table, user))
		row = c.fetchall()
		if len(row) > 0:
			return row[0][0]

	return None


@client.command(pass_context=True)
async def char(ctx, *args):
	def index_in_range(i):
		return i >= 0 and i < len(args)

	def char_help():
		COMMAND = '>>char '
		message = bold('Usage:') + BREAKLINE
		message += bold(COMMAND + 'list (generation) [main | villain | side | all] [all]') + BREAKLINE
		message += bold(COMMAND + 'take (character)') + BREAKLINE
		message += bold(COMMAND + 'status (character)') + BREAKLINE
		message += bold(COMMAND + 'leave') + BREAKLINE
		message += 'For more information see ' + bold('>>help')
		return message


	async def char_list():			# >>char list command
		def list_help():
			message = 'Usage: >>char list (dm | gx | fiveds | zexal | arcv | vrains) [main | villain | side | all] [all]'
			return message

		def error_wrong_gen():
			message = "{} is not a valid parameter. correct parameters:".format(args[1]) + BREAKLINE
			for gen in generations:
				message += gen + ' '
			return message

		try:
			if args[1] not in generations:
				await client.say(error_wrong_gen())
				return
		except IndexError:
			await client.say(list_help())
			return
			

		condition = 'SELECT name FROM {}'.format(args[1])
		if not index_in_range(2):
			condition += ' WHERE (role="main" OR role="villain")'
		elif args[2] in ['main', 'villain', 'side'] and not args[2] == 'all':
			condition += ' WHERE role="{}"'.format(args[2])

		if not index_in_range(3):
			if index_in_range(2) and args[2] == 'all':
				condition += ' WHERE'
			else:
				condition += ' AND'
			condition += ' taken="Nobody"'

		c.execute(condition)

		message = '```' + BREAKLINE
		for name in c.fetchall():
			message += name[0] + BREAKLINE
		message += '```'

		await client.say(embed=get_embed('Yu-Gi-Oh! ' + expanded_names[args[1]] + ' characters', message, discord.Colour.blue()))

	async def char_take():			# >>char take command
		def take_help():
			message = 'Usage: >>char take (character)'
			return message

		async def give_role(author, gen):
			role = discord.utils.get(author.server.roles, name=roles[gen][0])
			if role == None:
				role = await create_role(author, gen)

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
			await client.say("Couldn't find any duelist named {}.".format(character) + BREAKLINE + """CaSe SeNsItIvE! Writing `Z-ONE` insatead of `z-one` makes a big difference!""")

		else:
			if not get_user_character(str(author)) == None:
				await client.say("You already have character! Use `>>char leave` to leave your current one so you can get another!")

			elif row[2] == "Nobody":
				c.execute('UPDATE {} SET taken="{}" WHERE taken="Nobody" AND name="{}"'.format(table, str(author), character))
				conn.commit()
				await give_role(author, table)
				congrats = 'You are now {}!'.format(character)
				await client.change_nickname(author, character)
				await client.say(embed=get_embed('', congrats, discord.Colour.blue()))

			else:
				await client.say('{} is already taken.'.format(character))


	async def char_leave():			# >>char leave command
		author = ctx.message.author
		character = get_user_character(author)

		if not character == None:
			table, row = get_character_info(character)
			c.execute('UPDATE {} SET taken="Nobody" WHERE taken="{}"'.format(table, author))
			conn.commit()
			role = discord.utils.get(author.server.roles, name=roles[table][0])
			await client.remove_roles(author, role)
			await client.change_nickname(author, '')
			await client.say(embed=get_embed('', "You aren't {} anymore!".format(row[0]), discord.Colour.blue()))

		else:
			await client.say("You don't have a character!")


	async def char_status():		# >>char_status command
		def status_help():
			message = '`Usage: >>char status (character)`'
			return message

		try:
			args[1]
		except IndexError:
			await client.say(status_help())
			return

		table, row = get_character_info(args[1])
		output = get_embed('Yu-Gi-Oh! {} - {}'.format(expanded_names[table], row[0]), '', discord.Colour.blue())
		output.add_field(name='Status', value=row[1], inline=True)
		output.add_field(name='Taken by', value=row[2], inline=True)
		await client.say(embed=output)
		
	try:
		if args[0] == 'list':
			await char_list()
		elif args[0] == 'take':
			await char_take()
		elif args[0] == 'leave':
			await char_leave()
		elif args[0] == 'status':
			await char_status()
		else:
			await client.say(char_help())
	except IndexError:
		await client.say(char_help())
		


@client.command(pass_context=True)
async def status(ctx):
	author = ctx.message.author
	character = get_user_character(author)
	
	if character == None:
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


@client.command(pass_context=True)
async def test(ctx, *args):
	author = ctx.message.author
	role = discord.utils.get(author.server.roles, name=args[0])
	await client.remove_roles(author, role)


client.run(TOKEN)
