from copy import copy
from dotenv import load_dotenv
import telebot
import random
import time
import os

from questions_python import questions

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if TOKEN is None:
    raise Exception(
        "Telegram bot token is not set. Please set the TELEGRAM_BOT_TOKEN environment variable.")

bot = telebot.TeleBot(TOKEN)

user_progress = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id not in user_progress:
        user_questions = copy(questions)
        random.shuffle(user_questions)
        start_time = time.time()
        user_progress[message.from_user.id] = {'question_index': 0, 'score': 0, 'answers': {
        }, 'user_questions': user_questions, 'start_time': start_time}
    bot.send_message(message.chat.id, "Тест розпочато!")
    ask_question(message)


def ask_question(message):
    user_id = message.from_user.id
    user_data = user_progress[user_id]
    question_data = user_data['user_questions'][user_data['question_index']]
    options = question_data['options']
    bot.send_message(message.chat.id, f"Запитання {
                     user_data['question_index']+1}:")

    random.shuffle(options)

    question_text = question_data['question'] + '\n\n'
    for i, option in enumerate(options):
        question_text += f"{i+1}. {option}\n"
    bot.send_message(message.chat.id, question_text)

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for option in options:
        markup.add(option)
    bot.send_message(user_id, "Виберіть вірний варіант:", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    try:
        user_id = message.from_user.id
        user_data = user_progress[user_id]
        question_data = user_data['user_questions'][user_data['question_index']]
        correct_answer = question_data['correct_answer']

        if message.text == correct_answer:
            bot.send_message(message.chat.id, "Правильно!")
            user_data['score'] += 1
        else:
            bot.send_message(message.chat.id, f"Неправильно. Правильна відповідь: {
                             correct_answer}")

        user_data['answers'][question_data['question']] = message.text

        user_data['question_index'] += 1
        if user_data['question_index'] < len(user_data['user_questions']):
            ask_question(message)
        else:
            end_quiz(message)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Будь ласка, виберіть відповідь.")


def end_quiz(message):
    user_id = message.from_user.id
    user_data = user_progress[user_id]
    end_time = time.time()
    duration = round(end_time - user_data['start_time'], 2)

    report = f"Тест завершено!!\n\n" \
        f"Правильних відповідей: {user_data['score']}/{len(user_data['user_questions'])}\n\n" \
        f"Тривалість: {duration} секунд\n\n" \
        f"Ваші відповіді:\n"
    for question, answer in user_data['answers'].items():
        report += f"- {question}\n  Обрано: {answer}\n"

    bot.send_message(
        user_id, report, reply_markup=telebot.types.ReplyKeyboardRemove())

    del user_progress[user_id]


print('Bot started.')
bot.polling()
