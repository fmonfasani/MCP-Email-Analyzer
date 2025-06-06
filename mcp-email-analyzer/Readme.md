# MCP Email Analyzer

Un servidor MCP (Model Context Protocol) para análisis automático y gestión de emails usando Google Apps Script.

## 🎯 Descripción

Este proyecto implementa un servidor MCP que permite analizar, clasificar y gestionar emails de Gmail de forma automática usando IA. Integra Google Apps Script para acceso directo a Gmail y proporciona herramientas MCP para análisis inteligente de contenido.

## 🏗️ Arquitectura

```
mcp-email-analyzer/
├── src/
│   ├── server/
│   │   ├── __init__.py
│   │   ├── email_server.py          # Servidor MCP principal
│   │   ├── gmail_client.py          # Cliente Gmail API
│   │   └── email_analyzer.py        # Análisis de contenido
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── email_tools.py           # Herramientas MCP
│   │   └── classification_tools.py  # Clasificación automática
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── analysis_prompts.py      # Prompts para análisis
│   │   └── classification_prompts.py # Prompts para clasificación
│   └── gas/
│       ├── Code.gs                  # Google Apps Script
│       ├── EmailProcessor.gs        # Procesamiento de emails
│       └── appsscript.json         # Configuración GAS
├── tests/
│   ├── test_server.py
│   ├── test_tools.py
│   └── test_prompts.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_classification.py
├── docs/
│   ├── installation.md
│   ├── configuration.md
│   └── api_reference.md
├── pyproject.toml
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml
```

## 📦 Instalación

```bash
pip install mcp-email-analyzer
```

## 🚀 Inicio Rápido

### 1. Configuración de Google Apps Script

1. Crea un nuevo proyecto en [Google Apps Script](https://script.google.com)
2. Copia el contenido de `src/gas/Code.gs`
3. Habilita Gmail API en el proyecto
4. Configura los triggers para ejecución automática

### 2. Configuración del Servidor MCP

```python
from mcp_email_analyzer import EmailAnalyzerServer

# Inicializar servidor
server = EmailAnalyzerServer(
    gmail_credentials_path="credentials.json",
    classification_rules="rules.json"
)

# Ejecutar servidor
server.run()
```

### 3. Uso con Claude Desktop

Agrega a tu configuración de Claude Desktop:

```json
{
  "mcpServers": {
    "email-analyzer": {
      "command": "python",
      "args": ["-m", "mcp_email_analyzer"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  }
}
```

## 🛠️ Herramientas MCP

### email_analyze
Analiza el contenido de un email específico.

```python
{
  "name": "email_analyze",
  "description": "Analiza el contenido y contexto de un email",
  "inputSchema": {
    "type": "object",
    "properties": {
      "email_id": {"type": "string"},
      "analysis_type": {"type": "string", "enum": ["content", "sentiment", "priority", "category"]}
    }
  }
}
```

### email_classify
Clasifica emails automáticamente.

```python
{
  "name": "email_classify",
  "description": "Clasifica emails en categorías predefinidas",
  "inputSchema": {
    "type": "object",
    "properties": {
      "email_ids": {"type": "array", "items": {"type": "string"}},
      "categories": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```

### email_action
Ejecuta acciones sobre emails (marcar como leído, archivar, eliminar).

```python
{
  "name": "email_action",
  "description": "Ejecuta acciones sobre emails seleccionados",
  "inputSchema": {
    "type": "object",
    "properties": {
      "email_ids": {"type": "array", "items": {"type": "string"}},
      "action": {"type": "string", "enum": ["mark_read", "archive", "delete", "label"]}
    }
  }
}
```

## 📝 Prompts MCP

### email_analysis_prompt
Prompt para análisis detallado de emails.

### bulk_classification_prompt
Prompt para clasificación masiva de emails.

### priority_assessment_prompt
Prompt para evaluación de prioridad de emails.

## 🔧 Configuración Avanzada

### Reglas de Clasificación (rules.json)

```json
{
  "rules": [
    {
      "name": "newsletter",
      "conditions": {
        "sender_pattern": ".*newsletter.*|.*no-reply.*",
        "subject_keywords": ["newsletter", "unsubscribe", "weekly"]
      },
      "actions": ["mark_read", "label:newsletters"]
    },
    {
      "name": "spam_detection",
      "conditions": {
        "content_keywords": ["urgent", "act now", "limited time"],
        "sender_not_in_contacts": true
      },
      "actions": ["delete"]
    }
  ]
}
```

### Variables de Entorno

```bash
GMAIL_CREDENTIALS=path/to/credentials.json
CLASSIFICATION_RULES=path/to/rules.json
LOG_LEVEL=INFO
MAX_EMAILS_PER_BATCH=50
```

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest tests/

# Tests específicos
python -m pytest tests/test_server.py -v
```

## 📊 Métricas y Monitoreo

El servidor incluye métricas integradas:

- Emails procesados por minuto
- Precisión de clasificación
- Tiempo de respuesta promedio
- Errores de API

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🔗 Enlaces

- [Documentación MCP](https://modelcontextprotocol.io/)
- [Google Apps Script](https://developers.google.com/apps-script)
- [Gmail API](https://developers.google.com/gmail/api)

## 📞 Soporte

- Issues: [GitHub Issues](https://github.com/tu-usuario/mcp-email-analyzer/issues)
- Documentación: [Docs](https://mcp-email-analyzer.readthedocs.io/)
- Email: support@mcp-email-analyzer.com

---

**Nota**: Este es un proyecto de código abierto diseñado para cumplir con los estándares del Model Context Protocol y ser incluido en el SDK oficial de Python.