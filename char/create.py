from modules.chat_utils import bold, markdown
from modules.data_manager import create_table
from modules.data_getter import get_correct_table
from modules.misc_utils import in_range

async def run(client, ctx, args, parameters):
    msgs = {
        'usage': 'Usage: ' + markdown('>>char create (table)'),
        'insufficient_permissions': 'You don\'t have the permissions to do that!',
        'already_exists': bold('{}') + ' already exists! Try using ' +
                          markdown('>>char list {}') + ' to see who\'s there!',
        'spaces': 'You can\'t use spaces in your table name!' + '\n' +
                    'Suggestions: ' + markdown('{}') + ' ' + markdown('{}'),
        'success': 'Table ' + bold('{}') + 'successfully created!'
    }

    if not ctx.message.author.server_permissions.administrator:
        await client.say(msgs['insufficient_permissions'])
        return

    if not in_range(parameters['table'], args):
        await client.say(msgs['usage'])
        return

    to_create = args[parameters['table']]

    if len(args[parameters['table']:]) > len(parameters) or ' ' in to_create:
        camelCase, snake_case = [], []
        for i in range(parameters['table'], len(args)):
            camelCase += args[i].split(' ')
            snake_case += args[i].split(' ')

        camelCase = [camelCase[i][0].upper() + camelCase[i][1:] for i in range(len(camelCase))]
        camelCase[0] = camelCase[0].lower()

        await client.say(msgs['spaces'].format(''.join(camelCase), '_'.join(snake_case)))
        return

    if get_correct_table(ctx, to_create) is not None:
        await client.say(msgs['already_exists'].format(to_create, to_create))
        return

    create_table(ctx, to_create)
    await client.say(msgs['success'].format(to_create))