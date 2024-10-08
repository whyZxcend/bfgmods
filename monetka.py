import asyncio
import random
from bot import bot
from aiogram import types, Dispatcher
from commands.db import conn, cursor, url_name, get_balance
from assets.transform import transform_int as tr
from commands.games.db import gametime
from commands.main import win_luser
from assets.antispam import antispam
from decimal import Decimal

from commands.help import CONFIG

#конфиг
CONFIG['help_game'] += '\n   🪙 Монетка (ставка)'

#бд
async def upd_balance(uid, summ, type):
  balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (uid,)).fetchone()[0]
  if type == "win":
    summ = Decimal(balance) + Decimal(summ)
  else:
    summ = Decimal(balance) - Decimal(summ)

  cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?", (str(summ), uid))
  cursor.execute(f"UPDATE users SET games = games + 1 WHERE user_id = ?", (uid,))
  conn.commit()

#играем
@antispam
async def coin_game(message: types.Message):
  uid = message.from_user.id
  rwin, rloser = await win_luser()
  balance = await get_balance(uid)
  url = await url_name(uid)

  try:
    if message.text.lower().split()[1] in ['все', 'всё']:
      summ = balance
    else:
      summ = message.text.split()[1].replace('е', 'e')
      summ = int(float(summ))
  except:
    await message.answer(f'{url}, вы не ввели ставку для игры {rloser}')
    return

  gt = await gametime(uid)
  if gt == 1:
    await message.answer(f'{url}, играть можно каждые 5 секунд. Подождите немного {rloser}')
    return

  if summ < 100:
    await message.answer(f'{url}, ваша ставка не может быть меньше 100$ {rloser}')
    return

  if balance < summ:
    await message.answer(f'{url}, у вас недостаточно денег {rloser}')
    return

  result = random.choice(['орел', 'решка'])
  
  if result == 'орел':
    await upd_balance(uid, summ, 'win')
    await message.answer(f'{url}, выпал орел! Вы выиграли {tr(summ)} ${rwin}')
  else:
    await upd_balance(uid, summ, 'lose')
    await message.answer(f'{url}, выпала решка! Вы проиграли {tr(summ)} ${rloser}')

#регистр
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(coin_game, lambda message: message.text.lower().startswith('монетка'))

#дескрипт
MODULE_DESCRIPTION = {
  'name': '🪙 Монетка',
  'description': 'Простая игра "Монетка", где вы можете сделать ставку и попытаться угадать, что выпадет: орел или решка.'
}

