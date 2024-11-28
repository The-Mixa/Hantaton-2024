
    dp.update.middleware(DataBaseSession(session_pool = session_maker))
    await bot.delete_webhook(drop_pending_updates = True)

    await bot.set_my_commands(admin_commands, scope = types.BotCommandScopeAllGroupChats())
    await bot.set_my_commands(user_commands, scope = types.BotCommandScopeAllPrivateChats())

    time_now = datetime.today()
    print(f"[{str(time_now)[:19]}]: Bot started")