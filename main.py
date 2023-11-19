import telebot
import os
from telebot import types
import pythoncom
import win32gui
from multiprocessing import Process


TOKEN = 'your token'
bot = telebot.TeleBot(TOKEN)


TIMEZONE = 'Europe/Moscow'


print("привет ")
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я бот для заметок. Используй команды:\n"
        "/notes - показать заметки\n"
        "/addnote - добавить заметку\n"
        "/deletenote - удалить заметку\n"
        "/deletenotes - удалить все заметки\n"
        "/help - показать это сообщение"
    )
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['notes'])
def show_notes(message):
    chat_id = message.chat.id
    notes = get_notes(chat_id)

    if notes:
        bot.send_message(chat_id, "Заметки:")
        for i, note in enumerate(notes, 1):
            bot.send_message(chat_id, f"{i}. {note}")
    else:
        bot.send_message(chat_id, "У вас нет заметок.")


@bot.message_handler(commands=['addnote'])
def add_note(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите новую заметку:")
    bot.register_next_step_handler(message, process_new_note)


def process_new_note(message):
    chat_id = message.chat.id
    note = message.text
    save_note(chat_id, note)
    bot.send_message(chat_id, "Заметка добавлена.")


@bot.message_handler(commands=['deletenote'])
def delete_note(message):
    chat_id = message.chat.id
    notes = get_notes(chat_id)

    if notes:
        markup = create_keyboard(notes)
        bot.send_message(chat_id, "Выберите заметку для удаления:", reply_markup=markup)
        bot.register_next_step_handler(message, process_delete_note)
    else:
        bot.send_message(chat_id, "У вас нет заметок.")


def process_delete_note(message):
    chat_id = message.chat.id
    try:
        note_number = int(message.text)
        notes = get_notes(chat_id)

        if 1 <= note_number <= len(notes):
            deleted_note = notes.pop(note_number - 1)
            save_notes(chat_id, notes)
            bot.send_message(chat_id, f"Заметка удалена: {deleted_note}")
        else:
            bot.send_message(chat_id, "Неверный номер заметки.")
    except ValueError:
        bot.send_message(chat_id, "Введите корректный номер заметки.")


def get_notes(chat_id):
    file_path = f"notes_{chat_id}.txt"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            notes = file.read().splitlines()
        return notes
    else:
        return []


def save_note(chat_id, note):
    file_path = f"notes_{chat_id}.txt"
    with open(file_path, "a") as file:
        file.write(note + "\n")


def save_notes(chat_id, notes):
    file_path = f"notes_{chat_id}.txt"
    with open(file_path, "w") as file:
        file.write("\n".join(notes))


def create_keyboard(notes):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    for i, note in enumerate(notes, 1):
        markup.add(types.KeyboardButton(str(i)))
    return markup



def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    pythoncom.CoInitialize()
    win32gui.ShowWindow(win32gui.GetForegroundWindow(), 0)
    p = Process(target=run_bot)
    p.start()
    p.join()
