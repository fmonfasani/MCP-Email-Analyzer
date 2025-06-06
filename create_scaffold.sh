#!/bin/bash

# Nombre del proyecto
PROJECT_NAME="mcp-email-analyzer"

# Crear estructura de carpetas
mkdir -p $PROJECT_NAME/src/server
mkdir -p $PROJECT_NAME/src/tools
mkdir -p $PROJECT_NAME/src/prompts
mkdir -p $PROJECT_NAME/src/gas
mkdir -p $PROJECT_NAME/tests
mkdir -p $PROJECT_NAME/examples
mkdir -p $PROJECT_NAME/docs
mkdir -p $PROJECT_NAME/.github/workflows

# Crear archivos vacíos
touch $PROJECT_NAME/src/server/__init__.py
touch $PROJECT_NAME/src/server/email_server.py
touch $PROJECT_NAME/src/server/gmail_client.py
touch $PROJECT_NAME/src/server/email_analyzer.py

touch $PROJECT_NAME/src/tools/__init__.py
touch $PROJECT_NAME/src/tools/email_tools.py
touch $PROJECT_NAME/src/tools/classification_tools.py

touch $PROJECT_NAME/src/prompts/__init__.py
touch $PROJECT_NAME/src/prompts/analysis_prompts.py
touch $PROJECT_NAME/src/prompts/classification_prompts.py

touch $PROJECT_NAME/src/gas/Code.gs
touch $PROJECT_NAME/src/gas/EmailProcessor.gs
touch $PROJECT_NAME/src/gas/appsscript.json

touch $PROJECT_NAME/tests/test_server.py
touch $PROJECT_NAME/tests/test_tools.py
touch $PROJECT_NAME/tests/test_prompts.py

touch $PROJECT_NAME/examples/basic_usage.py
touch $PROJECT_NAME/examples/advanced_classification.py

touch $PROJECT_NAME/docs/installation.md
touch $PROJECT_NAME/docs/configuration.md
touch $PROJECT_NAME/docs/api_reference.md

touch $PROJECT_NAME/pyproject.toml
touch $PROJECT_NAME/README.md
touch $PROJECT_NAME/LICENSE
touch $PROJECT_NAME/.github/workflows/ci.yml

echo "✅ Proyecto '$PROJECT_NAME' creado con éxito!"
