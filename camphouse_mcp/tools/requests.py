import json
import os
import requests
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MEDIATOOL_URL = 'https://api.mediatool.com'
MEDIATOOL_TOKEN = os.getenv("CAMPHOUSE_TOKEN_ID", None)


# Define una excepción personalizada para errores de la API
class MediatoolAPIError(Exception):
    """Excepción personalizada para errores de la API de Mediatool."""
    pass


def make_request(endpoint, payload=None, method='GET'):
    if not MEDIATOOL_TOKEN:
        raise MediatoolAPIError("La variable de entorno CAMPHOUSE_TOKEN_ID no está configurada.")

    api_url = MEDIATOOL_URL.rstrip('/')
    url = f"{api_url}/{endpoint.lstrip('/')}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f"Bearer {MEDIATOOL_TOKEN}"
    }

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=payload, timeout=60)
        else:
            json_payload = json.dumps(payload) if payload else None
            response = requests.request(method, url, data=json_payload, headers=headers, timeout=60)

        # Lanza una excepción para respuestas con código de error (4xx o 5xx)
        response.raise_for_status()

        if response.status_code == 204:
            return None  # No content

        return response.json()

    except requests.exceptions.HTTPError as e:
        # Maneja errores HTTP de forma más elegante
        error_message = f"Error HTTP: {e.response.status_code} para la URL: {e.request.url}"
        try:
            # Intenta obtener un mensaje de error más específico del cuerpo de la respuesta
            error_details = e.response.json()
            msg = error_details.get('message') or error_details.get('error')
            if msg:
                error_message = f"Error de la API de Mediatool: {msg}"
        except requests.exceptions.JSONDecodeError:
            error_message = f"Error de la API de Mediatool: {e.response.text}"

        logger.error(error_message)
        raise MediatoolAPIError(error_message) from e

    except requests.exceptions.ConnectionError as e:
        logger.exception("No se pudo conectar a la API de Mediatool en %s", url)
        raise MediatoolAPIError(f"Mediatool: No se pudo establecer una conexión con la API en {url}.") from e

    except requests.exceptions.RequestException as e:
        # Captura cualquier otro error relacionado con requests
        logger.exception("La solicitud a la API de Mediatool falló: %s", str(e))
        raise MediatoolAPIError(f"Mediatool: Ocurrió un error inesperado al conectar con la API: {e}") from e
