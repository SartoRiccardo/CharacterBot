from modules.data_initializer import update_template


async def run(client, ctx, args):
    update_template(ctx, args[1:])
    await client.say("Template was updated!")