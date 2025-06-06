# MCP Email Analyzer Server

Servidor MCP (Model Context Protocol) para análisis inteligente de emails con integración Gmail.

## 🚀 Características

- **Análisis Individual**: Analiza emails con sentiment, prioridad, categoría y resumen
- **Clasificación en Lote**: Procesa múltiples emails simultáneamente
- **Acciones Gmail**: Marcar como leído, archivar, eliminar, etiquetar
- **Búsqueda Avanzada**: Filtros por remitente, fecha, adjuntos, etc.
- **Logging Estructurado**: Registro JSON para monitoring y debugging

## 🛠️ Instalación

### Prerequisitos

```bash
pip install mcp>=1.0.0
pip install google-api-python-client google-auth-oauthlib
pip install openai anthropic  # Para análisis AI
```

### Configuración

1. **Variables de Entorno**:
```bash
# Gmail API
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json

# OpenAI (opcional)
OPENAI_API_KEY=your_openai_key

# Anthropic (opcional)  
ANTHROPIC_API_KEY=your_anthropic_key

# Configuración
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

2. **Credenciales Gmail**:
   - Crear proyecto en Google Cloud Console
   - Habilitar Gmail API
   - Descargar credentials.json
   - Ejecutar autorización inicial

## 🎯 Herramientas MCP

### 1. email_analyze
Analiza un email individual con múltiples tipos de análisis.

**Parámetros**:
```json
{
  "email_id": "gmail_message_id",
  "analysis_types": ["sentiment", "priority", "category", "summary"]
}
```

**Ejemplo de Uso**:
```python
result = await session.call_tool(
    name="email_analyze",
    arguments={
        "email_id": "17a1b2c3d4e5f6g7",
        "analysis_types": ["sentiment", "priority", "category"]
    }
)
```

**Respuesta**:
```json
{
  "email_id": "17a1b2c3d4e5f6g7",
  "subject": "Urgente: Revisión del proyecto",
  "analysis": {
    "sentiment": "neutral",
    "priority": "high",
    "category": "work"
  },
  "confidence": 0.89,
  "analyzed_at": "2025-06-06T10:30:00Z"
}
```

### 2. email_classify
Clasifica múltiples emails en lote por categoría, prioridad o sentimiento.

**Parámetros**:
```json
{
  "email_ids": ["id1", "id2", "id3"],
  "classification_type": "category",
  "batch_size": 10
}
```

**Ejemplo de Uso**:
```python
result = await session.call_tool(
    name="email_classify",
    arguments={
        "email_ids": ["email1", "email2", "email3"],
        "classification_type": "priority",
        "batch_size": 2
    }
)
```

**Respuesta**:
```json
{
  "classification_type": "priority",
  "total_processed": 3,
  "results": [
    {
      "email_id": "email1",
      "subject": "Reunión equipo",
      "classification": "medium",
      "confidence": 0.76,
      "success": true
    }
  ],
  "processed_at": "2025-06-06T10:35:00Z"
}
```

### 3. email_action
Ejecuta acciones sobre emails: marcar como leído, archivar, eliminar, etiquetar.

**Parámetros**:
```json
{
  "email_ids": ["id1", "id2"],
  "action": "read|archive|delete|label",
  "action_params": {
    "label_ids": ["LABEL_ID1", "LABEL_ID2"]
  }
}
```

**Ejemplo de Uso**:
```python
# Marcar como leído
result = await session.call_tool(
    name="email_action",
    arguments={
        "email_ids": ["email1", "email2"],
        "action": "read"
    }
)

# Agregar etiquetas
result = await session.call_tool(
    name="email_action",
    arguments={
        "email_ids": ["email3"],
        "action": "label",
        "action_params": {
            "label_ids": ["Label_1", "Label_2"]
        }
    }
)
```

**Respuesta**:
```json
{
  "action": "read",
  "total_emails": 2,
  "results": [
    {
      "email_id": "email1",
      "action": "read",
      "success": true
    },
    {
      "email_id": "email2", 
      "action": "read",
      "success": true
    }
  ],
  "executed_at": "2025-06-06T10:40:00Z"
}
```

### 4. email_search
Busca emails con sintaxis de consulta Gmail y filtros adicionales.

**Parámetros**:
```json
{
  "query": "from:sender@example.com is:unread",
  "filters": {
    "sender": "specific@email.com",
    "subject_contains": "urgent",
    "date_from": "2025-06-01",
    "date_to": "2025-06-06",
    "has_attachments": true,
    "is_unread": false
  },
  "limit": 20,
  "include_analysis": false
}
```

**Ejemplo de Uso**:
```python
result = await session.call_tool(
    name="email_search",
    arguments={
        "query": "is:unread has:attachment",
        "filters": {
            "sender": "boss@company.com",
            "date_from": "2025-06-01"
        },
        "limit": 10,
        "include_analysis": true
    }
)
```

**Respuesta**:
```json
{
  "query": "is:unread has:attachment",
  "filters": {
    "sender": "boss@company.com",
    "date_from": "2025-06-01"
  },
  "total_results": 3,
  "results": [
    {
      "email_id": "email_xyz",
      "subject": "Q2 Financial Report",
      "sender": "boss@company.com",
      "received_at": "2025-06-05T14:30:00Z",
      "is_read": false,
      "has_attachments": true,
      "analysis": {
        "category": "business",
        "priority": "high",
        "confidence": 0.91
      }
    }
  ],
  "searched_at": "2025-06-06T10:45:00Z"
}
```

## 🚀 Ejecución

### Iniciar Servidor
```bash
# Método 1: Directamente
python -m src.server

# Método 2: Con configuración específica
LOG_LEVEL=DEBUG python -m src.server

# Método 3: Como servicio
python -c "from src.server.mcp_server import main; import asyncio; asyncio.run(main())"
```

### Pruebas
```bash
# Probar todas las herramientas
python scripts/test_mcp_server.py

# Probar herramienta específica
python scripts/test_mcp_server.py --tool analyze
python scripts/test_mcp_server.py --tool search
python scripts/test_mcp_server.py --tool classify
python scripts/test_mcp_server.py --tool action
```

## 🔧 Configuración Avanzada

### Archivo de Configuración MCP
```json
{
  "mcpServers": {
    "email-analyzer": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/project",
      "env": {
        "PYTHONPATH": ".",
        "GMAIL_CREDENTIALS_PATH": "/path/to/credentials.json",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Logging Personalizado
```python
# Configuración en src/server/config.py
class Settings:
    log_level: str = "INFO"
    log_to_file: bool = True
    log_format: str = "json"  # json, text
    log_file_path: str = "logs/mcp_server.log"
```

### Limitaciones y Cuotas
- **email_classify**: Máximo 50 emails por lote
- **email_search**: Máximo 100 resultados por búsqueda  
- **batch_size**: Máximo 20 emails por batch interno
- **Rate Limiting**: Respeta límites de Gmail API

## 📊 Monitoring

### Logs Estructurados
```json
{
  "action": "email_analyze",
  "email_id": "abc123",
  "analysis_types": ["sentiment", "priority"],
  "timestamp": "2025-06-06T10:30:00Z",
  "success": true,
  "processing_time_ms": 234
}
```

### Métricas Disponibles
- Emails procesados por minuto/hora
- Tiempo de procesamiento promedio
- Tasa de éxito por herramienta
- Errores por categoría
- Uso de cuota Gmail API

## 🛡️ Seguridad

### Autenticación Gmail
- OAuth 2.0 flow completo
- Tokens encriptados localmente
- Refresh automático de credenciales
- Scopes mínimos necesarios

### Validación de Entrada
- Sanitización de parámetros
- Validación de schemas JSON
- Límites de rate limiting
- Manejo seguro de errores

## 🐛 Troubleshooting

### Errores Comunes

**1. Gmail API Authentication Error**
```bash
# Solución: Re-autorizar credenciales
rm token.json
python scripts/setup_gmail_auth.py
```

**2. MCP Connection Failed**
```bash
# Verificar servidor está ejecutándose
ps aux | grep "src.server"

# Verificar logs
tail -f logs/mcp_server.log
```

**3. Analysis Service Timeout**
```bash
# Verificar configuración AI provider
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Reducir batch_size
python scripts/test_mcp_server.py --tool classify
```

### Debug Mode
```bash
# Ejecutar con debug completo
LOG_LEVEL=DEBUG python -m src.server

# Verificar herramientas registradas
python -c "
from src.server.mcp_server import EmailAnalyzerServer
from src.server.config import Settings
server = EmailAnalyzerServer(Settings())
print('Tools:', server.server.list_tools())
"
```

## 📈 Extensiones

### Agregar Nueva Herramienta MCP
```python
# En src/server/mcp_server.py
@self.server.call_tool()
async def email_custom_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Nueva herramienta personalizada."""
    # Implementación
    pass

# Registrar herramienta
self.server.register_tool(
    Tool(
        name="email_custom_tool",
        description="Descripción de la nueva herramienta",
        inputSchema={...}
    )
)
```

### Integrar Nuevo Provider AI
```python
# En src/analysis/service.py
class CustomAIProvider(AnalysisProvider):
    async def analyze_sentiment(self, text: str) -> str:
        # Implementación personalizada
        pass
```

## 📝 Changelog

### v1.0.0 (2025-06-06)
- ✅ Implementación inicial servidor MCP
- ✅ 4 herramientas principales (analyze, classify, action, search)
- ✅ Integración Gmail API completa
- ✅ Logging estructurado JSON
- ✅ Validación schemas entrada
- ✅ Manejo errores robusto
- ✅ Scripts de prueba y configuración

## 🤝 Contribuir

1. Fork del repositorio
2. Crear feature branch
3. Implementar cambios con tests
4. Actualizar documentación
5. Submit pull request

## 📄 Licencia

MIT License - Ver LICENSE file para detalles.