import asyncio
import logging
import sys
import io

from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, BufferedInputFile

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


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


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
