
def perform(ctx, condition, action):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('UPDATE ', 'UPDATE t'))
        conn.commit()

    conn.close()