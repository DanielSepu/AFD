
from channels.generic.websocket import WebsocketConsumer
import json
import requests

class FrequencyConsumer(WebsocketConsumer):
   def connect(self):
      self.accept()

def receive(self, text_data=None, bytes_data=None):
   data = json.loads(text_data)
   frequency = data.get('frequency')
   # Lógica para enviar la frecuencia a Node-RED
   send_frequency_to_node_red(frequency)


def send_frequency_to_node_red(self, frequency):
   # Enviar una solicitud HTTP a Node-RED
   node_red_url = 'http://localhost:1880/update-frequency'
   data = {'frequency': frequency}
   requests.post(node_red_url, json=data)