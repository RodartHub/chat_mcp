# Multi-MCP Chat con Gemini y Camphouse

Este proyecto demuestra una arquitectura para construir un agente de chat conversacional que puede interactuar con múltiples "Multi-Capability Providers" (MCPs). Utiliza el modelo Gemini de Google para el razonamiento y la selección de herramientas, una interfaz de usuario de Gradio y conectores específicos para cada MCP, con un enfoque detallado en la implementación del MCP de Camphouse.

## Arquitectura

El sistema se compone de las siguientes partes principales:

1.  **Interfaz de Usuario (Gradio)**: `main.py` lanza una interfaz de chat simple usando Gradio, que sirve como punto de entrada para las consultas del usuario.
2.  **Orquestador LLM (Gemini)**: `llm/gemini_llm.py` es el cerebro de la operación. Recibe las consultas del usuario, gestiona el historial de la conversación y decide si debe responder directamente o utilizar una de las herramientas disponibles de los MCPs (function calling).
3.  **Conectores MCP**: La carpeta `connectors/` contiene los clientes que saben cómo comunicarse con cada servidor MCP.
    *   `mcp_base_connector.py`: Una clase base abstracta que define la interfaz común para todos los conectores.
    *   `camphouse_connector.py`: Un conector que inicia y se comunica con el servidor MCP de Camphouse a través de `stdio`.
    *   `ga4_connector.py`: Un conector similar para Google Analytics 4.
4.  **Servidor MCP de Camphouse**: El directorio `camphouse_mcp/` es un paquete de Python autocontenido que implementa el servidor de herramientas para Camphouse.

El flujo de una consulta es el siguiente:
`Usuario -> Gradio UI -> GeminiLLM -> [Decisión de usar herramienta] -> Conector (ej. CamphouseConnector) -> Servidor MCP (ej. Camphouse MCP) -> Ejecución de Herramienta -> API Externa (Camphouse API) -> Retorno de datos -> GeminiLLM -> Respuesta final -> Usuario`

---

## Enfoque: El MCP de Camphouse

El MCP de Camphouse está diseñado como un paquete de Python independiente que se ejecuta en su propio proceso. El `CamphouseConnector` lo inicia utilizando `mcp.stdio_client`.

### Estructura de Archivos del MCP

-   `camphouse_mcp/`
    -   `server.py`: El punto de entrada del servidor. Se ejecuta con `python -m camphouse_mcp.server` y simplemente inicia el servidor MCP.
    -   `coordinator.py`: Aquí se define la instancia principal de `FastMCP`. Se le da un nombre, descripción e instrucciones generales para el LLM sobre cómo usar las herramientas de este MCP.
    -   `camphouse_connector/`: Contiene la lógica de las herramientas, organizadas por entidad.
        -   `organizations/main.py`: Define herramientas relacionadas con organizaciones (obtener detalles, subsidiarias, etc.).
        -   `campaigns/main.py`: Herramientas para campañas.
        -   `...` (otros módulos de herramientas).
    -   `tools/`: Utilidades compartidas por las herramientas.
        -   `requests.py`: Un wrapper para realizar llamadas a la API REST de Camphouse (Mediatool), gestionando la autenticación y el manejo de errores.

### Definición de una Herramienta

Las herramientas se definen de manera declarativa usando el decorador `@mcp.tool` sobre una función de Python. `FastMCP` se encarga de introsccionar la firma de la función, los type hints y el docstring para generar el esquema que se presentará al LLM.

**Ejemplo (`camphouse_mcp/camphouse_connector/organizations/main.py`):**

```python
from ...coordinator import mcp

@mcp.tool(title="Camphouse: Get organization details")
def get_organization(organization_id: str) -> Dict[str, Any]:
    """
    Camphouse: Get details of a specific organization by its ID.
    Args:
        organization_id (str): The ID of the organization to retrieve.
    Returns:
        Dict[str, Any]: A dictionary containing the organizations details.
    """
    endpoint = f"organizations/{organization_id}"
    return make_request(endpoint, method='GET')
```

-   `@mcp.tool(...)`: Registra la función `get_organization` como una herramienta disponible.
-   `get_organization(organization_id: str)`: El nombre del argumento (`organization_id`) y su tipo (`str`) se usan para definir los parámetros que el LLM debe proporcionar.
-   `"""Docstring"""`: La descripción de la herramienta y sus argumentos se extrae del docstring para que el LLM entienda para qué sirve la herramienta.
-   `make_request(...)`: La lógica interna de la herramienta utiliza el helper para interactuar con la API real.

### Comunicación y Aislamiento

El `CamphouseConnector` (`connectors/camphouse_connector.py`) es responsable de:
1.  Iniciar el proceso del servidor MCP de Camphouse.
2.  Pasar las variables de entorno necesarias (`CAMPHOUSE_TOKEN_ID`, `CAMPHOUSE_COMPANY_MAIN_ID`) al proceso del servidor. Esto es crucial para que el MCP pueda autenticarse contra la API de Camphouse.
3.  Establecer una sesión de comunicación a través de `stdio` para llamar a las herramientas y recibir los resultados.

Este enfoque aísla completamente la lógica del MCP del resto de la aplicación, permitiendo que se desarrolle y se pruebe de forma independiente.

## Configuración y Ejecución

### 1. Requisitos Previos

-   Python 3.8+
-   Instalar las dependencias (asumiendo que hay un `requirements.txt`):
    ```bash
    pip install -r requirements.txt
    ```

### 2. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto o exporta las siguientes variables de entorno:

```
# Para el LLM de Gemini
GEMINI_API_KEY="tu_api_key_de_gemini"
GEMINI_MODEL="gemini-1.5-pro-latest" # O el modelo que prefieras

# Para el MCP de Camphouse (Mediatool)
CAMPHOUSE_TOKEN_ID="tu_token_de_api_de_mediatool"
CAMPHOUSE_COMPANY_MAIN_ID="el_id_de_tu_compañia_principal"

# Para el MCP de GA4
# Puede ser la ruta a un archivo JSON o el contenido del JSON como string
GOOGLE_APPLICATION_CREDENTIALS="..."
```

### 3. Ejecutar la Aplicación

Una vez configuradas las variables de entorno, inicia la aplicación:

```bash
python main.py
```

Esto levantará el servidor de Gradio. Abre la URL que aparece en la consola (normalmente `http://0.0.0.0:8080`) en tu navegador para empezar a chatear.
