import json
import locale
import os
import pytz
import time
import schedule
import random
import requests
import sqlite3
import urllib.parse

from datetime import datetime, timedelta
from flask import Flask, request, Response, send_from_directory
from threading import Thread


class VStatic:

  def __init__(self, cucina, bagni, aree_comuni, ids, member, ragazzi,
               last_message_id, cassa):
    self.cucina = cucina
    self.bagni = bagni
    self.aree_comuni = aree_comuni
    self.ids = ids
    self.member = member
    self.ragazzi = ragazzi
    self.last_message_id = last_message_id
    self.cassa = cassa

  def __str__(self):
    return f"Cucina: {self.cucina}\nBagni: {self.bagni}\nAree Comuni: {self.aree_comuni}\nIDs: {self.ids}\nMembers: {', '.join(self.member)}"


bot_token = my_secret = os.environ['BOT_TOKEN']

url = f'https://api.telegram.org/bot{bot_token}/getUpdates'

webhook = 'https://9a7c26ec-3261-4edc-906b-9ab275cedc85-00-bpju7sbse62g.kirk.replit.dev/webhook'

webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook}'

print(webhook_url)

dataBase = "./full.sqlite"
conn = sqlite3.connect("./full.sqlite")

admin_id = "6392248910"

os.environ['TZ'] = 'Europe/Rome'
time.tzset()

print(f'Starting time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')


def init_data():
  global dataBase
  try:
    con = sqlite3.connect(dataBase)
    cor = con.cursor()
    res = cor.execute("SELECT * FROM ids")
    ids = [int(id[0]) for id in res.fetchall()]
    res = cor.execute("SELECT * FROM users")
    obj = res.fetchone()
    cor.close()
    con.close()
    return VStatic(obj[1], obj[2], obj[3], ids, json.loads(obj[4]),
                   json.loads(obj[5]), obj[6], obj[7])
  except FileNotFoundError:
    return VStatic(0, 0, 0, [], [])


pippo = init_data()


def get_closest_day():
  current_day = datetime.today().weekday()
  if current_day < 3:
    day = ["lunedì", "giovedi"]
  else:
    day = ["giovedi", "lunedi"]
  return day


def get_next_day():
  current_day = datetime.today().weekday()
  print("current_day: %d", current_day)
  if current_day == 6:
    return "Giovedi"
  else:
    return "Lunedi"


def get_name_of_day(shift):
  day = [
      "Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi", "Sabato",
      "Domendica"
  ]
  current_day = (datetime.today().weekday() + shift) % 7
  return (day[current_day])


def update_varible(col_name, val):
  global dataBase

  try:
    con = sqlite3.connect(dataBase)
    cor = con.cursor()
    res = cor.execute(f"UPDATE users SET {col_name} = {val} WHERE id=1")

    con.commit()
    cor.close()
    con.close()
  except FileNotFoundError:
    pass


def update_ids_db(user_ids):
  global dataBase

  pippo.ids = list(set(pippo.ids + user_ids))
  try:
    con = sqlite3.connect(dataBase)
    cor = con.cursor()
    res = cor.executemany("INSERT OR IGNORE INTO ids(id) VALUES(?)",
                          [tuple([str(i)]) for i in pippo.ids])
    con.commit()
    cor.close()
    con.close()
  except FileNotFoundError:
    pass


def get_chatID(data):

  user_ids = []
  id_list = [data['message']['from']['id']]
  user_ids.extend(id_list)
  user_ids = list(dict.fromkeys(user_ids))

  update_ids_db(user_ids)
  return pippo.ids


def telegram_bot_sendtext(bot_message, chat_id):
  global bot_token

  send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(
      chat_id) + '&parse_mode=Markdown&text=' + urllib.parse.quote(bot_message)

  response = requests.get(send_text)
  return response.json()


def prossimi_days_aree(start_count, dd):
  global pippo

  oggi = datetime.now()
  giorni_mancanti_lunedi = (0 - oggi.weekday() + 7) % 7
  giorni_mancanti_giovedi = (3 - oggi.weekday() + 7) % 7

  prossimo_lunedi = oggi + timedelta(days=giorni_mancanti_lunedi)
  prossimo_giovedi = oggi + timedelta(days=giorni_mancanti_giovedi)

  if prossimo_lunedi.weekday() == oggi.weekday():
    prossimo_lunedi = prossimo_lunedi + timedelta(days=7)
  if prossimo_giovedi.weekday() == oggi.weekday():
    prossimo_giovedi = prossimo_giovedi + timedelta(days=7)

  messaggi = []
  for _ in range(dd):
    messaggio_lunedi = f"Lunedi {prossimo_lunedi.day} {prossimo_lunedi.strftime('%B')}"
    messaggio_giovedi = f"Giovedi {prossimo_giovedi.day} {prossimo_giovedi.strftime('%B')}"
    messaggi += [messaggio_lunedi, messaggio_giovedi]

    prossimo_lunedi += timedelta(weeks=1)
    prossimo_giovedi += timedelta(weeks=1)

  messaggi = sorted(
      messaggi,
      key=lambda x:
      (datetime.strptime(x.split()[2], '%B').month, int(x.split()[1])))
  new_msg = [
      f"{messaggio}: \n     `{pippo.member[(start_count + i) % len(pippo.member)]}`"
      for i, messaggio in enumerate(messaggi, start=0)
  ]
  return new_msg


def prossimi_days_bagni(start_count, dd):
  global pippo

  oggi = datetime.now()
  giorni_mancanti_lunedi = (0 - oggi.weekday() + 7) % 7
  giorni_mancanti_giovedi = (3 - oggi.weekday() + 7) % 7

  prossimo_lunedi = oggi + timedelta(days=giorni_mancanti_lunedi)
  prossimo_giovedi = oggi + timedelta(days=giorni_mancanti_giovedi)

  if prossimo_lunedi.weekday() == oggi.weekday():
    prossimo_lunedi = prossimo_lunedi + timedelta(days=7)
  if prossimo_giovedi.weekday() == oggi.weekday():
    prossimo_giovedi = prossimo_giovedi + timedelta(days=7)

  messaggi = []
  for _ in range(dd):
    messaggio_lunedi = f"Lunedi {prossimo_lunedi.day} {prossimo_lunedi.strftime('%B %Y')}"
    messaggio_giovedi = f"Giovedi {prossimo_giovedi.day} {prossimo_giovedi.strftime('%B %Y')}"
    messaggi += [messaggio_lunedi, messaggio_giovedi]

    prossimo_lunedi += timedelta(weeks=1)
    prossimo_giovedi += timedelta(weeks=1)

  messaggi = sorted(
      messaggi,
      key=lambda x:
      (datetime.strptime(x.split()[2], '%B').month, int(x.split()[1])))
  new_msg = [
      f"{messaggio}: \n     `{pippo.ragazzi[(start_count + i) % len(pippo.ragazzi)]}`"
      for i, messaggio in enumerate(messaggi, start=0)
  ]
  return new_msg


def prossimi_days_cucina(start_count, dd):
  global pippo

  oggi = datetime.now()
  messaggi = []
  shift = 0
  for _ in range(dd):
    oggi += timedelta(days=1)
    messaggio = f"{get_name_of_day(_ + 1)} {oggi.day} {oggi.strftime('%B')}: \n     `{pippo.member[(start_count + _) % len(pippo.member)]}`"
    messaggi += [messaggio]
  return messaggi


def schedule_mese():
  global pippo

  messaggi = []
  messaggi += ["Bagni:"]
  messaggi += prossimi_days_bagni(pippo.bagni, 4)
  messaggi += ["\nAree comuni:"]
  messaggi += prossimi_days_aree(pippo.aree_comuni, 4)
  messaggi += ["\nCucina:"]
  messaggi += prossimi_days_cucina(pippo.cucina, 30)

  return messaggi


def schedule_settimana():
  global pippo

  messaggi = []
  messaggi += ["Bagni:"]
  messaggi += prossimi_days_bagni(pippo.bagni, 1)
  messaggi += ["\nAree comuni:"]
  messaggi += prossimi_days_aree(pippo.aree_comuni, 1)
  messaggi += ["\nCucina:"]
  messaggi += prossimi_days_cucina(pippo.cucina, 7)

  return messaggi


def msg_schedule_mese():
  messaggi = schedule_mese()

  out = ""
  for msg in messaggi:
    out += msg
    out += "\n"
  return out


def msg_schedule_settimana():
  messaggi = schedule_settimana()

  out = ""
  for msg in messaggi:
    out += msg
    out += "\n"
  return out


def find_user(user_id):
  for members_string in pippo.member:
    members_list = members_string.split(', ')
    if user_id in members_list:
      return 1

  return 0


def my_schedule_mese(user_id):
  tourn = ""

  if find_user(user_id) == 0:
    return "Utente non trovato"

  for msg in schedule_mese():
    if msg.find(user_id) != -1 or msg.find("Cucina:") != -1 or \
      msg.find("Bagni:") != -1 or msg.find("Aree comuni:") != -1:
      tourn += msg.split(':')[0]  # add only the part before ':'
      tourn += "\n"
  return tourn


def get_admin_commands(data):
  global pippo

  new_admin_commands = []

  try:
    message = data.get('message')
    message_id = message['message_id']
    chat_id = message['chat']['id']
    text = message['text']
    if text.startswith('%'):
      if str(chat_id) != admin_id:
        telegram_bot_sendtext("Ehi campione... posa subito quel comando",
                              chat_id)
        return
      if message_id > pippo.last_message_id:
        new_admin_commands.append({
            'id_msg': message_id,
            'id': chat_id,
            'text': text
        })
        pippo.last_message_id = message_id
        update_varible('id_last_msg', pippo.last_message_id)
    return new_admin_commands
  except Exception as e:
    print(f'Error parsing JSON: {e}')


def get_new_bot_commands(data):
  global pippo

  new_bot_commands = []
  try:
    message = data.get('message')
    if message and 'entities' in message:
      entities = message['entities']
      if entities and entities[0]['type'] == 'bot_command':
        message_id = message['message_id']
        chat_id = message['chat']['id']
        text = message['text']
        if message_id > pippo.last_message_id:
          new_bot_commands.append({
              'id_msg': message_id,
              'id': chat_id,
              'text': text
          })
          pippo.last_message_id = message_id
          update_varible('id_last_msg', pippo.last_message_id)
    return new_bot_commands
  except Exception as e:
    print(f'Error parsing JSON: {e}')


def fCucina(chat_id):
  pre_index = (pippo.cucina - 1 + len(pippo.member)) % len(pippo.member)
  my_message = f"Turno di oggi({get_name_of_day(0)}): `{pippo.member[pre_index]}`\n\n"
  my_message += f"Prossimo turno({get_name_of_day(1)}): `{pippo.member[pippo.cucina]}`\n"
  telegram_bot_sendtext(my_message, chat_id)


def fBagni(chat_id):
  day = get_closest_day()
  pre_index = (pippo.bagni - 1 + len(pippo.ragazzi)) % len(pippo.ragazzi)

  my_message = f"Turno di {day[0]}: `{pippo.ragazzi[pre_index]}`\n\n"
  my_message += f"Turno di {day[1]}: `{pippo.ragazzi[pippo.bagni]}`\n"
  telegram_bot_sendtext(my_message, chat_id)


def fAreeComuni(chat_id):
  day = get_closest_day()

  pre_index = (pippo.aree_comuni - 1 + len(pippo.member)) % len(pippo.member)
  my_message = f"Turno di {day[0]}: `{pippo.member[pre_index]}`\n\n"
  my_message += f"Turno di {day[1]}: `{pippo.member[pippo.aree_comuni]}`\n"
  telegram_bot_sendtext(my_message, chat_id)


def command_handler(data):
  line = get_new_bot_commands(data)
  if line:
    id_chat = line[0]["id"]
    cmd = line[0]["text"]
    if cmd == "/start":
      telegram_bot_sendtext(
          "Hi Welcome To Lospollos Hermano.\nUse /help per avere la lista dei comandi di questo botiino.",
          id_chat)
    if cmd == "/cucina":
      fCucina(id_chat)
    if cmd == "/bagni":
      fBagni(id_chat)
    if cmd == "/areecomuni":
      fAreeComuni(id_chat)
    if cmd == "/mdi-paol":
      telegram_bot_sendtext("Mia sorella e' incinta ...\n", id_chat)
      time.sleep(1)
      telegram_bot_sendtext("Diventero' padre!", id_chat)
    if cmd == "/cassa":
      telegram_bot_sendtext(f"La cassa ammonta a {pippo.cassa}$", id_chat)
    if cmd == "/mese":
      telegram_bot_sendtext(msg_schedule_mese(), id_chat)
    if cmd == "/settimana":
      telegram_bot_sendtext(msg_schedule_settimana(), id_chat)
    elif cmd.find("/mese") == 0:
      index = cmd.find("/mese") + len("/mese")
      user = cmd[index:].strip()
      telegram_bot_sendtext(my_schedule_mese(user), id_chat)
    if cmd == "/cschiavo":
      telegram_bot_sendtext("Cosa hai detto della sorella di Celso?", id_chat)
    if cmd == "/ciusca":
      telegram_bot_sendtext(
          "Sei bravo con le parole... ma con i pugni nel culo come te la cavi?",
          id_chat)
    if cmd == "/naal-jen":
      telegram_bot_sendtext("Succhiami lu cazzo Cristo morto", id_chat)
    if cmd == "/help":
      telegram_bot_sendtext(
          "I comandi disponibili sono:\n/mese\n/mese name\n/cucina\n/bagni\n/areecomuni\n/help",
          id_chat)


def admin_command_handler(data):
  cmd = get_admin_commands(data)
  if cmd:
    chat_id = cmd[0]["id"]
    text = cmd[0]["text"]
    if text.startswith("%msg"):
      msg = cmd[0]["text"].split("%msg")[1].strip()
      for id in pippo.ids:
        telegram_bot_sendtext(msg, id)
    elif text == "%cucina":
      pippo.cucina = (pippo.cucina + 1) % len(pippo.member)
      update_varible("cucina", pippo.cucina)
      telegram_bot_sendtext(
          f"Turno cucina aggiornato.\nValore attuale:{pippo.cucina}", chat_id)
    elif text == "%bagni":
      pippo.bagni = (pippo.bagni + 1) % len(pippo.member)
      update_varible("bagni", pippo.bagni)
      telegram_bot_sendtext(
          f"Turno bagni aggiornato.\nValore attuale:{pippo.bagni}", chat_id)
    elif text == "%areecomuni":
      pippo.aree_comuni = (pippo.aree_comuni + 1) % len(pippo.member)
      update_varible("aree_comuni", pippo.aree_comuni)
      telegram_bot_sendtext(
          f"Turno aree comuni aggiornato.\nValore attuale:{pippo.aree_comuni}",
          chat_id)
    elif text.startswith("%cassa"):
      valore_testo = text.split("%cassa")[1].strip()
      try:
        importo = float(valore_testo.rstrip('%'))
        pippo.cassa += importo
        update_varible("cassa", pippo.cassa)
        telegram_bot_sendtext(
            f"Cassa aggiornata.\nValore attuale: {pippo.cassa}$", chat_id)
      except ValueError:
        telegram_bot_sendtext(f"Valore non valido", chat_id)
    else:
      telegram_bot_sendtext(f"Comando non riconosciuto", chat_id)


def up_cucina():
  pippo.cucina = (pippo.cucina + 1) % (len(pippo.member))
  update_varible("cucina", pippo.cucina)


def cucina():
  user_ids = pippo.ids

  prev_d = (pippo.cucina - 1 + (len(pippo.member)) % (len(pippo.member)))
  my_message = f"Turno cucina di oggi({get_name_of_day(0)}): `{pippo.member[prev_d]}`\n"
  my_message += f"Prossimo turno cucina({get_name_of_day(1)}): `{pippo.member[pippo.cucina]}`\n"

  for user_id in user_ids:
    telegram_bot_sendtext(my_message, user_id)


def bagni():
  user_ids = pippo.ids

  my_message = f"Turno bagni di domami({get_name_of_day(1)}): `{pippo.ragazzi[pippo.bagni]}`\n"
  pippo.bagni = (pippo.bagni + 1) % (len(pippo.ragazzi))
  my_message += f"Prossimo turno bagni({get_next_day()}): `{pippo.ragazzi[pippo.bagni]}`\n"

  for user_id in user_ids:
    telegram_bot_sendtext(my_message, user_id)

  update_varible("bagni", pippo.bagni)


def aree_comuni():
  user_ids = pippo.ids

  my_message = f"Turno aree comuni domani({get_name_of_day(1)}): `{pippo.member[pippo.aree_comuni]}`\n"
  pippo.aree_comuni = (pippo.aree_comuni + 1) % (len(pippo.member))
  my_message += f"Prossimo turno aree comuni({get_next_day()}): `{pippo.member[pippo.aree_comuni]}`\n"

  for user_id in user_ids:
    telegram_bot_sendtext(my_message, user_id)

  update_varible("aree_comuni", pippo.aree_comuni)


def spesa():
  user_ids = pippo.ids

  random_num = random.randint(0, len(pippo.member))
  my_message = f"I fortunati per le compere sono: `{pippo.member[random_num]}`"

  for user_id in user_ids:
    telegram_bot_sendtext(my_message, user_id)
  print(my_message)


# Increase day count
schedule.every().day.at("18:00:00").do(cucina)

schedule.every().day.at("01:00:00").do(up_cucina)

schedule.every().sunday.at("21:00:30").do(bagni)
schedule.every().sunday.at("21:01").do(aree_comuni)

schedule.every().wednesday.at("21:00:30").do(bagni)
schedule.every().wednesday.at("21:01").do(aree_comuni)

schedule.every(14).days.at("21:01:30").do(spesa)
#------------------------------------

# Create flask app
app = Flask(__name__)
#------------------------------------

#Disable flask logging
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#------------------------------------


# Define homepage route
@app.route("/")
def homepage():
  return send_from_directory("static", 'index.html')


@app.route('/<path:path>')
def serve_static(path):
  return send_from_directory('static', path)


#------------------------------------


# Define server starting function
def runServer():
  app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)


#------------------------------------


# Other work which is blocking code
def doStuff():
  pass


#------------------------------------


@app.route('/webhook', methods=['POST'])
def return_response():
  data = request.get_json()
  command_handler(data)
  admin_command_handler(data)
  get_chatID(data)
  return Response(status=200)


if __name__ == '__main__':
  # Run flask app on it's own thread
  webThread = Thread(target=runServer)
  webThread.start()

  # Run stuff on it's own thread
  # Or simply run it on main thread
  # doStuff()
  while True:
    pippo = init_data()
    schedule.run_pending()
    time.sleep(1)

#cit del giorno
