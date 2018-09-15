from modules.data_manager import update_template


async def run(client, ctx, args):
    if ctx.message.author.server_permissions.administrator:
        await update_template(ctx.message.server.id, args[1:])
        await client.say("Template was updated!")
    else:
        await client.say("You don't have the permissions to do that!")