from modules.chat_utils import bold, markdown
from modules.preset_manager import get_presets, import_db

async def run(client, ctx, args, parameters):
    msgs = {
        'insufficient_permissions': 'You don\'t have the permissions to do that',
        'nonexistent': 'The preset ' + bold('{}') + ' doesn\'t exist!' + '\n' +
                       'Do ' + markdown('>>char import list') + ' to see what\'s available!',
        'confirmation': 'All of your current characters will be deleted. Type ' + markdown('yes') + ' to continue',
        'success': 'Successfully imported ' + bold('{}') + '!',
        'failure': 'Did not import ' + bold('{}')
    }

    if not ctx.message.author.server_permissions.administrator:
        await client.say(msgs['insufficient_permissions'])
        return

    to_import = args[parameters['to_import']]
    if to_import.lower() == 'list':
        available_presets = get_presets()
        msg = 'Available presets: '
        for p in available_presets:
            msg += markdown(p) + ' '
        await client.say(msg)
        return

    await client.say(msgs['confirmation'])
    response = await client.wait_for_message(author=ctx.message.author, timeout = 30)
    try:
        if response is not None and response.clean_content == 'yes':
            server = ctx.message.server.id
            import_db(server, to_import)
            await client.say(msgs['success'].format(to_import))
        else:
            await client.say(msgs['failure'].format(to_import))

    except SyntaxError as e:
        await client.say(msgs[str(e)].format(to_import))
