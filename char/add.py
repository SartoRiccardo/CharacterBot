from modules.chat_utils import markdown, bold
from modules.data_getter import get_tables, get_character_info, get_correct_table
from modules.data_manager import get_columns, insert, delete_character
from modules.misc_utils import in_range, get_dict_keys

async def run(client, ctx, args, parameters):
    # check if exists
    # put quotes for spaces
    # check if parameters are correct
    msgs = {
        'insufficient_permissions': "You don't have the permissions to do that!",
        'invalid_table': 'Invalid table: {}',
        'already_exists': 'Character already exists in table ' + markdown('{}') + '\n'
                          'To modify that character\'s info, use ' + markdown('{}'),
        'invalid_parameters': 'Invalid parameters. This is what you should put:\n{}',
        'usage' : 'Usage: ' + markdown('>>char add (table) (character) (parameters)'),
        'success_added': 'Successfully added ' + bold('{}') + ' into ' + bold('{}'),
        'success_modified': 'Successfully modified ' + bold('{}') + '\'s data!'
    }

    if not ctx.message.author.server_permissions.administrator:
        await client.say(msgs['insufficient_permissions'])
        return

    if not in_range(parameters['char'], args):
        await client.say(msgs['usage'])
        return

    server = ctx.message.server.id
    table = get_correct_table(server, args[parameters['table']])#table = args[parameters['table']]
    if table not in get_tables(server):
        await client.say(msgs['invalid_table'].format(args[parameters['table']]))
        return

    if not len(args[parameters['args']:]) == len(get_columns(server))-2:
        template = ''
        for c in get_columns(server)[2:]:
            template += markdown(c) + ' '
        await client.say(msgs['invalid_parameters'].format(template))
        return

    char = args[parameters['char']]
    char_data = get_character_info(server, char)
    if len(char_data) == 0:
        condition = 'INSERT INTO {} VALUES("{}", "nobody"'.format(table, char)
        for p in args[parameters['args']:]:
            condition += ', "{}"'.format(p)
        condition += ')'

        insert(server, condition)
        await client.say(msgs['success_added'].format(char, table))

    else:
        char = char_data[get_dict_keys(char_data)[0]][0]
        if not get_dict_keys(char_data)[0] == table:
            correct_cmd = '>>char add {} {}'.format(get_dict_keys(char_data)[0], char)
            for p in args[parameters['args']:]:
                correct_cmd += ' {}'.format(p)

            await client.say(msgs['already_exists'].format(get_dict_keys(char_data)[0], correct_cmd))
            return

        delete_character(server, char)

        condition = 'INSERT INTO {} VALUES("{}", "nobody"'.format(table, char)
        for p in args[parameters['args']:]:
            condition += ', "{}"'.format(p)
        condition += ')'
        insert(server, condition)
        await client.say(msgs['success_modified'].format(char))