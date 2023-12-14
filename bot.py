import discord
from discord.ext import commands
import json
import os

# Проверка или файл с данными уже существует
if not os.path.exists("bank_data.json"):
    with open("bank_data.json", "w") as f:
        json.dump({}, f)

# Загрузка данных из файла
with open("bank_data.json", "r") as f:
    bank_data = json.load(f)

# Создаем объект бота
bot = commands.Bot(command_prefix='!')

# Событие, срабатывающее при успешном запуске бота
@bot.event
async def on_ready():
    print(f'Бот запущен как {bot.user.name}')

# Команда для просмотра баланса
@bot.command()
async def баланс(ctx):
    user_id = str(ctx.author.id)
    balance = bank_data.get(user_id, 0)
    await ctx.send(f'Ваш баланс: {balance} монет')

# Команда для просмотра истории транзакций
@bot.command()
async def история(ctx):
    user_id = str(ctx.author.id)
    transactions = bank_data.get(f'{user_id}_history', [])
    history_message = '\n'.join(transactions) if transactions else 'История пуста'
    await ctx.send(f'История транзакций:\n{history_message}')

# Команда для перевода средств другому пользователю
@bot.command()
async def перевести(ctx, получатель: discord.Member, сумма: int):
    if сумма <= 0:
        await ctx.send('Сумма должна быть положительной.')
        return

    отправитель_id = str(ctx.author.id)
    получатель_id = str(получатель.id)

    if отправитель_id not in bank_data:
        await ctx.send('У вас недостаточно средств для перевода.')
    elif bank_data[отправитель_id] < сумма:
        await ctx.send('У вас недостаточно средств для перевода.')
    else:
        # Выполняем перевод
        bank_data[отправитель_id] -= сумма
        bank_data[получатель_id] = bank_data.get(получатель_id, 0) + сумма

        # Обновляем историю транзакций
        transaction_history = bank_data.get(f'{отправитель_id}_history', [])
        transaction_history.append(f'Перевод {сумма} монет пользователю {получатель.name}')
        bank_data[f'{отправитель_id}_history'] = transaction_history

        transaction_history = bank_data.get(f'{получатель_id}_history', [])
        transaction_history.append(f'Получено {сумма} монет от пользователя {ctx.author.name}')
        bank_data[f'{получатель_id}_history'] = transaction_history

        # Сохраняем изменения в файл
        with open("bank_data.json", "w") as f:
            json.dump(bank_data, f)

        await ctx.send(f'Перевод {сумма} монет пользователю {получатель.name} выполнен успешно.')

# Команда для пополнения баланса
@bot.command()
async def пополнить(ctx, сумма: int):
    if сумма <= 0:
        await ctx.send('Сумма должна быть положительной.')
        return

    user_id = str(ctx.author.id)
    bank_data[user_id] = bank_data.get(user_id, 0) + сумма

    # Обновляем историю транзакций
    transaction_history = bank_data.get(f'{user_id}_history', [])
    transaction_history.append(f'Пополнение баланса на {сумма} монет')
    bank_data[f'{user_id}_history'] = transaction_history

    # Сохраняем изменения в файл
    with open("bank_data.json", "w") as f:
        json.dump(bank_data, f)

    await ctx.send(f'Баланс успешно пополнен на {сумма} монет.')

# Команда для просмотра топа пользователей
@bot.command()
async def топ(ctx):
    top_users = sorted(bank_data.items(), key=lambda x: x[1], reverse=True)[:10]
    top_message = '\n'.join([f'{ctx.guild.get_member(int(user[0]))}: {user[1]} монет' for user in top_users])
    await ctx.send(f'Топ пользователей:\n{top_message}')

# Токен вашего бота
token = 'ВАШ_ТОКЕН'
bot.run(token)
