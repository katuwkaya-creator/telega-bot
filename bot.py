from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8847795048:AAEnilm7FUfqm3ImKrS-ncGhcsGpjImD54E"

warnings = {} 
last_posts = set()

BAD_WORDS = [
    "хер",
    "член",
    "пенис",
    "голый",
    "голая",
    "голое",
    "голые",
    "ню",
    "nude",
    "naked",
    "topless",
    "слив",
    "слить",
    "сливы",
    "башня"
]


# ======================
# ПРИВЕТСТВИЕ ПОД ПОСТОМ
# ======================

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return
# защита от повторного приветствия для альбомов
    media_group = update.message.media_group_id

    if media_group:

        if media_group in last_posts:
            return

        last_posts.add(media_group)

    # только посты канала
    if not update.message.is_automatic_forward:
        return


    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📖 Правила",
                    url="https://nekopopsek.my.canva.site/nekopopsek"
                )
            ],
            [
                InlineKeyboardButton(
                    "📸 Instagram",
                    url="https://www.instagram.com/nekopopsek"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎵 TikTok",
                    url="https://www.tiktok.com/@nekopopsek7"
                )
            ]
        ]
    )


    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.message.message_id,

        text=(
            " Заходи общаться в чат!\n\n"
            "Ссылка на чат:\n"
            "https://t.me/+7wZS-5odlKMyODcy\n\n"
            "Пожалуйста, соблюдай правила ❤️"
        ),

        reply_markup=keyboard
    )



# ======================
# УДАЛЕНИЕ СИСТЕМНЫХ СООБЩЕНИЙ
# ======================

async def delete_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return


    if (
        update.message.new_chat_members
        or update.message.left_chat_member
    ):

        try:
            await update.message.delete()

        except:
            pass



# ======================
# МОДЕРАЦИЯ
# ======================

async def moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return


    # не трогаем посты канала
    if update.message.is_automatic_forward:
        return


    user = update.message.from_user

    if not user:
        return


    user_id = user.id

    violation = None


    # фото

    if update.message.photo:

        violation = "📷 Фото запрещены"



    # видео

    elif update.message.video:

        violation = "🎥 Видео запрещены"



    # текст

    elif update.message.text:

        text = update.message.text.lower()


        for word in BAD_WORDS:

            if word in text:


                try:
                    await update.message.delete()
                except:
                    pass


                try:

                    await context.bot.ban_chat_member(
                        chat_id=update.effective_chat.id,
                        user_id=user_id
                    )


                except Exception as e:

                    print("Ошибка бана:", e)


                return



        if (
            "http://" in text
            or "https://" in text
            or "t.me/" in text
        ):

            violation = "🔗 Ссылки запрещены"



    if violation:


        try:
            await update.message.delete()

        except:
            pass



        warnings[user_id] = warnings.get(user_id, 0) + 1


        count = warnings[user_id]


        if count >= 3:


            try:

                await context.bot.ban_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id
                )

            except Exception as e:

                print("Ошибка бана:", e)



        else:


            await context.bot.send_message(
                chat_id=update.effective_chat.id,

                text=f"⚠️ Предупреждение {count}/3\n{violation}"
            )# ======================
# ГЛАВНЫЙ ОБРАБОТЧИК
# ======================

async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message and update.message.is_automatic_forward:

        await welcome(update, context)

        return


    await moderation(update, context)



# ======================
# ЗАПУСК
# ======================

app = (
    Application.builder()
    .token(TOKEN)
    .connect_timeout(60)
    .read_timeout(60)
    .write_timeout(60)
    .build()
)



app.add_handler(
    MessageHandler(
        filters.ChatType.GROUPS,
        delete_service_messages
    ),
    group=0
)



app.add_handler(
    MessageHandler(
        filters.ChatType.GROUPS & (
            filters.TEXT |
            filters.PHOTO |
            filters.VIDEO
        ),
        main_handler
    ),
    group=1
)



print(" Бот запущен")

app.run_polling()