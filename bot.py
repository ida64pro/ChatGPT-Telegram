import asyncio

from g4f.client import AsyncClient
from g4f.Provider import Ecosia

from aiogram import (Router, Bot, Dispatcher,
                     F, types)
import logging

router = Router(name=__name__)
lock = asyncio.Lock()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def response_gpt(message):
    client = AsyncClient(
        provider=Ecosia
    )
# Провайдер Ecosia не работает в РФ, если вы не из РФ или сервер не РФ, можете неиспользовать прокси и удалить строку ниже
    client.proxies = {
        "http": "http://user:pass@ip:port" ,
        "https": "http://user:pass@ip:port"
    }

    try:
        completion = await client.chat.completions.create(
            max_tokens=4096,
            model="",
            messages=message,
        )

        return completion.choices[0].message.content

    except Exception as ex:
        print(ex)
        return None


@router.business_message(F.text)
async def handler_message(message: types.Message):
    async with lock:
        user_id = message.chat.id
        logger.info(f"Received business message from {user_id}: {message.text}")

        messages = [
            {"role": "system",
             "content": "Hello! You - AI-Assistant in Telegram. Answer on asks by players"},
            {"role": "user", "content": message.text}
        ]

        response = await response_gpt(messages)

        if response is None:
            await message.answer("Response is None")
        else:
            logger.info(f"Response sent to business chat: {response}")
            await message.answer(response)


async def main() -> None:
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
