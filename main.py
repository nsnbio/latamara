from keep_alive import keep_alive
import requests
import subprocess
import time
from datetime import datetime


def enviar_mensaje(mensaje):
  url = f"https://api.telegram.org/bot{token}/sendMessage"
  params = {"chat_id": chat_id2, "text": mensaje}
  response = requests.get(url, params=params)
  if response.status_code == 200:
    print("Mensaje enviado con éxito.")
  else:
    print(response)
    print("Hubo un error al enviar el mensaje.")

def segs_faltantes(str_hora_mensaje):
  try:
    hora_mensaje = datetime.strptime(str_hora_mensaje, "%H:%M:%S").time()
    save_hour(str_hora_mensaje)
  except ValueError:
    enviar_mensaje("El mensaje no contiene una hora válida en formato HH:MM:SS.")
    return None
            
  # Obtener hora actual en formato de 24 horas GMT
  hora_actual = datetime.utcnow().time()

  # Calcular la diferencia en segundos entre la hora actual y la hora del mensaje
  print('Hora actual: '+str(hora_actual))
  print('Hora de alarma: '+str(hora_mensaje))
  segundos_faltantes = (
      ((hora_mensaje.hour + 3) * 3600 + hora_mensaje.minute * 60 + hora_mensaje.second) -
      (hora_actual.hour * 3600 + hora_actual.minute * 60 + hora_actual.second)
  )
  if segundos_faltantes < 0:
    segundos_faltantes += 24 * 60 * 60  # Agregar 24 horas si la hora ya pasó

  return segundos_faltantes

def save_hour(hr):
  writer = open('lasthour.txt','w')
  writer.write(hr)
  writer.close()

def get_seconds_to_alarm():
  url = f"https://api.telegram.org/bot{token}/getUpdates"
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    if data["ok"] and len(data["result"]) > 0:
      mensaje = data["result"][-1]["message"]
      hora_str = mensaje["text"]
      return segs_faltantes(hora_str)
    else:
      lasthour = open('lasthour.txt','r').read()
      return segs_faltantes(lasthour)
  else:
    time.sleep(10)
    return set_time()

def chequear(flag):
  try:
    latampass_url = 'https://latampass.latam.com/es_ar/'
    descuento_url = 'https://latampass.latam.com/es_ar/acumula-millas/compra-millas-latam-pass-con-descuento'

    string1 = 'Millas con descuento'
    string2 = '-con-descuento'
    # data-pagination-label="Millas con descuento"
    # o buscar el string '-con-descuento'

    try1 = subprocess.check_output('curl ' + latampass_url, shell=True).decode('UTF-8')

    if string1 in try1 or string2 in try1:
      enviar_mensaje("¡Descuento disponible! " + latampass_url)
    else:
      
      #try2 = subprocess.check_output('curl ' + descuento_url, shell=True).decode('UTF-8')
      
      #if string1 in try2 or string2 in try2:
        #enviar_mensaje("¡Revisar! Figura la promo en el sitio: " + descuento_url)
      #else:
      if flag == True:
        enviar_mensaje("Revisado, hoy no hay descuento.")

  except subprocess.CalledProcessError as e:
    enviar_mensaje('Error:\n' + str(e))

# Token telegram
token = "6237784406:AAFaScTOWv3UkIF5bzo0Wc0EAqncPbVfVe8"

# ID chat
chat_id = "869167960"
chat_id2 = "@LATAMARA400"

keep_alive()

hrs_AR_check = ['01:01:10','06:01:01','10:02:10','13:01:00','20:02:00']

while True:

  # Obtener la hora actual
  hora_actual = datetime.now().time()

  # Convertir la hora actual a un objeto datetime
  hora_actual_dt = datetime.combine(datetime.today(), hora_actual).time()

  # Calcular la diferencia de tiempo mínima inicialmente a un valor grande
  tiempo_minimo = 48 * 60 * 60

  # Recorrer la lista de horas y encontrar la hora más cercana
  for hora_str in hrs_AR_check:
    # Convertir la hora de la lista a un objeto datetime
    hora_lista_dt = datetime.strptime(hora_str, "%H:%M:%S").time()

    # Calcular la diferencia de tiempo entre la hora actual y la hora de la lista
    tiempo_diferencia = (((hora_lista_dt.hour + 3) * 3600) + hora_lista_dt.minute * 60 + hora_lista_dt.second) - (hora_actual_dt.hour * 3600 + hora_actual_dt.minute * 60 + hora_actual_dt.second)

    # Si la diferencia de tiempo es negativa, sumar un día
    if tiempo_diferencia < 0:
      tiempo_diferencia += 24 * 60 * 60  # Agregar 24 horas si la hora ya pasó

    # Actualizar el tiempo mínimo si la diferencia de tiempo es menor
    if tiempo_diferencia < tiempo_minimo:
      tiempo_minimo = tiempo_diferencia

  # Obtener los segundos faltantes para la próxima hora más cercana
  segundos_faltantes_checks = tiempo_minimo

  seconds_to_alarm = get_seconds_to_alarm()
  
  if segundos_faltantes_checks < seconds_to_alarm:
    segundos_faltantes = segundos_faltantes_checks
    print('Chequeo próximo sin alarma.')
    alarm = False
  else:
    segundos_faltantes = seconds_to_alarm
    print('Chequeo próximo con alarma.')
    alarm = True

  while segundos_faltantes > 30:
    time.sleep(30)
    segundos_faltantes = segundos_faltantes - 30
    print(segundos_faltantes)

  print(segundos_faltantes)
  time.sleep(segundos_faltantes)
  
  chequear(alarm)
