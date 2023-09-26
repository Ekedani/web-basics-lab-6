import logging
import sys
import io

from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, BufferedInputFile

import qrcode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()

# WebHook related part of the application
WEB_SERVER_HOST = "::"
WEB_SERVER_PORT = 8350

WEBHOOK_PATH = "/bot/"
BASE_WEBHOOK_URL = "https://ekedani.alwaysdata.net"


@dp.message(CommandStart())
@dp.message(Command("help"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Hello! I'm here to help you create QR codes for all your needs. Whether it's a link, a message, "
        f"I've got you covered.\n"
        f"\nTo generate a QR code, send me the information you want to encode using commands /common or /styled, "
        f"and I'll create a QR code for you in an instant. You can then download and share it as you like."
    )


@dp.message(Command("common"))
async def common_qr_handler(message: types.Message, command: CommandObject) -> None:
    try:
        extracted_text = command.args
        qr = qrcode.make(extracted_text)
        if not extracted_text:
            raise ValueError("No text provided for QR code. Please, try again.")

        output = io.BytesIO()
        qr.save(output)
        output.seek(0)

        await message.answer_photo(
            photo=BufferedInputFile(output.getvalue(), filename='qr.jpg'),
            caption=f'Your QR code is ready.'
                    f'\nContent: {extracted_text}',
            reply_to_message_id=message.message_id
        )
    except ValueError as e:
        await message.answer(str(e))
    except TypeError:
        await message.answer("Incorrect input. Please, try again.")


@dp.message(Command("styled"))
async def styled_qr_handler(message: types.Message, command: CommandObject) -> None:
    try:
        extracted_text = command.args
        qr = qrcode.QRCode()
        if not extracted_text:
            raise ValueError("No text provided for QR code. Please, try again.")
        qr.add_data(extracted_text)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradiantColorMask()
        )

        output = io.BytesIO()
        img.save(output)
        output.seek(0)

        await message.answer_photo(
            photo=BufferedInputFile(output.getvalue(), filename='qr.jpg'),
            caption=f'Your QR code is ready.'
                    f'\nContent: {extracted_text}',
            reply_to_message_id=message.message_id
        )
    except ValueError as e:
        await message.answer(str(e))
    except TypeError:
        await message.answer("Incorrect input. Please, try again.")


@dp.message()
async def handle_text_message(message: Message):
    await message.answer("Please use the /common or /styled command to generate QR codes from text.")


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")


def main() -> None:
    dp.startup.register(on_startup)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
