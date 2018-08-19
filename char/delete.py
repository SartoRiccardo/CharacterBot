from modules.chat_utils import markdown, bold
from modules.misc_utils import in_range
from modules.data_manager import delete_character, delete_table
from modules.data_getter import get_tables, get_character_info

async def run(client, ctx, args, parameters):
    msgs = {
        'usage': 'Usage: ' + markdown('>>char del (table | character)'),
        'insufficient_permissions': 'You don\'t have the permissions to do that!',
        'not_found': 'Didn\'t find anything with the name: ' + bold('{}'),
        'confirmation': 'You are about to delete a whole table. Type ' + markdown('yes') + ' to continue',
        'success': bold('{}') + ' successfully deleted!',
        'failure': 'Did not delete ' + bold('{}'),
    }

    if not ctx.message.author.server_permissions.administrator:
        await client.say(msgs['insufficient_permissions'])
        return

    if not in_range(parameters['to_delete'], args):
        await client.say(msgs['usage'])

    to_delete = args[parameters['to_delete']]
    tables = get_tables(ctx)
    char_info = get_character_info(ctx, to_delete)

    if to_delete in tables:
        await client.say(msgs['confirmation'])
        response = await client.wait_for_message(author=ctx.message.author, timeout = 30)

        if response is not None and response.clean_content == 'yes':
            delete_table(ctx, to_delete)
            await client.say(msgs['success'].format(to_delete))
        else:
            await client.say(msgs['failure'].format(to_delete))

    elif not char_info == {}:
        delete_character(ctx, to_delete)
        await client.say(msgs['success'].format(to_delete))

    else:
        await client.say(msgs['not_found'].format(to_delete))