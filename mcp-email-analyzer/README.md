# MCP Email Analyzer

Un servidor MCP (Model Context Protocol) para análisis inteligente de emails de Gmail.

## Características

- Análisis de sentimientos de emails
- Categorización automática
- Priorización de mensajes
- Integración con Gmail API
- Arquitectura modular con patrones Repository + Service + Controller

## Instalación

```bash
pip install -e .
```

## Configuración

Copie `.env.example` a `.env` y configure las variables necesarias:

```bash
cp .env.example .env
```

## Uso

```bash
mcp-email-analyzer
```

## Arquitectura

- **Repository Layer**: Abstracción de acceso a datos
- **Service Layer**: Lógica de negocio y análisis
- **Controller Layer**: Manejo de protocolo MCP
- **Models**: Estructuras de datos tipadas
- **Logging**: Logging estructurado con JSON

## Desarrollo

```bash
# Instalar dependencias de desarrollo
poetry install

# Ejecutar tests
pytest

# Formateo de código
black src/
isort src/
```