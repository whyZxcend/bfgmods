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

CONFIG['help_game'] += '\n  🎲 Рулетка (ставка)'

# цифарки и букавки
bets = [
  'красное',
  'черное',
  'четное',
  'нечетное',
  '1-12',
  '13-24',
  '25-36',
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '10',
  '11',
  '12',
  '13',
  '14',
  '15',
  '16',
  '17',
  '18',
  '19',
  '20',
  '21',
  '22',
  '23',
  '24',
  '25',
  '26',
  '27',
  '28',
  '29',
  '30',
  '31',
  '32',
  '33',
  '34',
  '35',
  '36',
  '0'
]

# цвета
colors = {
  0: 'зеленый',
  1: 'красный',
  2: 'черный',
  3: 'красный',
  4: 'черный',
  5: 'красный',
  6: 'черный',
  7: 'красный',
  8: 'черный',
  9: 'красный',
  10: 'черный',
  11: 'черный',
  12: 'красный',
  13: 'черный',
  14: 'красный',
  15: 'черный',
  16: 'красный',
  17: 'черный',
  18: 'красный',
  19: 'красный',
  20: 'черный',
  21: 'красный',
  22: 'черный',
  23: 'красный',
  24: 'черный',
  25: 'красный',
  26: 'черный',
  27: 'красный',
  28: 'черный',
  29: 'черный',
  30: 'красный',
  31: 'черный',
  32: 'красный',
  33: 'черный',
  34: 'красный',
  35: 'черный',
  36: 'красный',
}

#датабаса
async def upd_balance(uid, summ, type):
  balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (uid,)).fetchone()[0]
  if type == "win":
    summ = Decimal(balance) + Decimal(summ)
  else:
    summ = Decimal(balance) - Decimal(summ)

  cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?", (str(summ), uid))
  cursor.execute(f"UPDATE users SET games = games + 1 WHERE user_id = ?", (uid,))
  conn.commit()

# играем?
@antispam
async def roulette(message: types.Message):
  uid = message.from_user.id
  rwin, rloser = await win_luser()
  balance = await get_balance(uid)
  url = await url_name(uid)

  try:
    bet = message.text.lower().split()[1]
    if bet not in bets:
      await message.answer(f'{url}, вы не ввели корректную ставку {rloser}')
      return
    if message.text.lower().split()[2] in ['все', 'всё']:
            summ = balance
    else:
            summ = message.text.split()[2].replace('е', 'e')
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

    win_conditions = []
    if bet == 'красное':
        win_conditions = [i for i in range(1, 37) if colors[i] == 'красный']
    elif bet == 'черное':
        win_conditions = [i for i in range(1, 37) if colors[i] == 'черный']
    elif bet == 'четное':
        win_conditions = [i for i in range(1, 37) if i % 2 == 0]
    elif bet == 'нечетное':
        win_conditions = [i for i in range(1, 37) if i % 2 != 0]
    elif bet in ['1-12', '13-24', '25-36']:
        start, end = [int(x) for x in bet.split('-')]
        win_conditions = [i for i in range(start, end + 1)]
    else:
        win_conditions = [int(bet)]

    # вращаемся и кидаем дизы
    winning_number = random.randint(0, 36)
    
    # проверка на вин
    if winning_number in win_conditions:
        if bet in ['красное', 'черное', 'четное', 'нечетное']:
            su = int(summ * 2)
            txt = f"🎲 | Шарик остановился на {winning_number} ({colors[winning_number]}). Вы выиграли {su} $"
            await upd_balance(uid, su, 'win')
        elif bet in ['1-12', '13-24', '25-36']:
            su = int(summ * 3)
            txt = f"🎲 | Шарик остановился на {winning_number}. Вы выиграли {su} $"
            await upd_balance(uid, su, 'win')
        else:
            su = int(summ * 36)
            txt = f"🎲 | Шарик остановился на {winning_number}. Вы выиграли {su} $"
            await upd_balance(uid, su, 'win')
    else:
        txt = f"🎲 | Шарик остановился на {winning_number} ({colors[winning_number]}). Вы проиграли."
        await upd_balance(uid, summ, 'lose')

    msg = await message.answer("🎲 | Крутим барабан...")
    await asyncio.sleep(2)
    await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=txt)

#регистр
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(roulette, lambda message: message.text.lower().startswith('рулетка'))

# о модуле
MODULE_DESCRIPTION = {
    'name': '🎲 Рулетка',
    'description': 'простенькая игра в рулетку'
}
