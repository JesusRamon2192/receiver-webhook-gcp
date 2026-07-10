import json
import os
from google.cloud import pubsub_v1
from flask import make_response

import functions_framework
#hola
# Inicializa el cliente fuera de la función para reutilizar la conexión en instancias cálidas
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = 'alerts-etl'  # El ID de tu proyecto asignado directamente como texto
TOPIC_ID = 'newrelic-ingestion-topic'
TOPIC_PATH = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@functions_framework.http
def receive_webhook(request):
    """HTTP Cloud Function para recibir webhooks."""
    # 1. (Opcional) Validación de seguridad simple
    # auth_header = request.headers.get('Authorization')
    # if auth_header != 'tu-secret-token':
    #     return make_response('Unauthorized', 401)

    try:
        # 2. Extraer el payload de New Relic
        request_json = request.get_json(silent=True)
        if not request_json:
            return make_response('Invalid JSON', 400)

        # 3. Empaquetar y enviar a Pub/Sub
        message_bytes = json.dumps(request_json).encode('utf-8')
        future = publisher.publish(TOPIC_PATH, data=message_bytes)
        future.result() # Espera a que el mensaje se publique

        return make_response('Event published', 200)

    except Exception as e:
        print(f"Error publishing message: {e}")
        return make_response('Internal Server Error', 500)