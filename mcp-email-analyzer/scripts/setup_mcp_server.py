#!/usr/bin/env python3
"""
Script de configuración inicial para el servidor MCP Email Analyzer.
Configura credenciales, dependencias y realiza verificaciones iniciales.
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any

def print_banner():
    """Mostrar banner de bienvenida."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   MCP EMAIL ANALYZER SETUP                   ║
    ║                                                              ║
    ║  Configuración inicial del servidor MCP para análisis       ║
    ║  inteligente de emails con integración Gmail                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Verificar versión de Python."""
    print("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} - OK")

def install_dependencies():
    """Instalar dependencias necesarias."""
    print("\n📦 Instalando dependencias...")
    
    requirements = [
        "mcp>=1.0.0",
        "google-api-python-client>=2.0.0",
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.1.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.0.0"
    ]
    
    for req in requirements:
        try:
            print(f"  Instalando {req}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", req
            ], check=True, capture_output=True)
            print(f"  ✅ {req.split('>=')[0]} instalado")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error instalando {req}: {e}")
            return False
    
    print("✅ Todas las dependencias instaladas correctamente")
    return True

def create_directory_structure():
    """Crear estructura de directorios necesaria."""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        "logs",
        "data",
        "config",
        "credentials",
        "tests",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ Estructura de directorios creada")

def create_env_file():
    """Crear archivo .env con configuración por defecto."""
    print("\n⚙️  Creando archivo de configuración...")
    
    env_content = """# MCP Email Analyzer Configuration

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json
GMAIL_TOKEN_PATH=credentials/gmail_token.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.modify

# AI Analysis Providers (configure at least one)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Analysis Configuration
ANALYSIS_PROVIDER=openai
ANALYSIS_MODEL=gpt-3.5-turbo
ANALYSIS_MAX_TOKENS=1000
ANALYSIS_TEMPERATURE=0.3

# Server Configuration
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=logs/mcp_server.log
LOG_FORMAT=json

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
CACHE_TTL=300

# Gmail API Limits
GMAIL_RATE_LIMIT_REQUESTS_PER_SECOND=10
GMAIL_BATCH_SIZE=100
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content)
        print("✅ Archivo .env creado")
        print("   📝 Edita .env para configurar tus API keys")
    else:
        print("⚠️  Archivo .env ya existe, no se sobreescribió")

def create_mcp_config():
    """Crear configuración MCP para Claude."""
    print("\n🔧 Creando configuración MCP...")
    
    mcp_config = {
        "mcpServers": {
            "email-analyzer": {
                "command": "python",
                "args": ["-m", "src.server"],
                "cwd": str(Path.cwd()),
                "env": {
                    "PYTHONPATH": "."
                }
            }
        }
    }
    
    config_file = Path("config/mcp_config.json")
    config_file.write_text(json.dumps(mcp_config, indent=2))
    print("✅ Configuración MCP creada en config/mcp_config.json")

def create_gmail_setup_script():
    """Crear script para configurar Gmail API."""
    print("\n📧 Creando script de configuración Gmail...")
    
    gmail_setup = '''#!/usr/bin/env python3
"""
Script para configurar autenticación Gmail API.
Ejecutar después de descargar credentials.json de Google Cloud Console.
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes necesarios para el Email Analyzer
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def setup_gmail_auth():
    """Configurar autenticación Gmail OAuth2."""
    print("🔐 Configurando autenticación Gmail...")
    
    credentials_path = Path("credentials/gmail_credentials.json")
    token_path = Path("credentials/gmail_token.json")
    
    if not credentials_path.exists():
        print("❌ Error: credentials/gmail_credentials.json no encontrado")
        print("   1. Ve a Google Cloud Console")
        print("   2. Crea un proyecto o selecciona uno existente")
        print("   3. Habilita Gmail API")
        print("   4. Crea credenciales OAuth 2.0")
        print("   5. Descarga el archivo JSON y guárdalo como credentials/gmail_credentials.json")
        return False
    
    creds = None
    
    # Cargar token existente si existe
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, obtener nuevas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para próximas ejecuciones
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    print("✅ Autenticación Gmail configurada correctamente")
    return True

if __name__ == "__main__":
    setup_gmail_auth()
'''
    
    script_file = Path("scripts/setup_gmail_auth.py")
    script_file.write_text(gmail_setup)
    script_file.chmod(0o755)
    print("✅ Script de configuración Gmail creado")

def verify_installation():
    """Verificar que la instalación sea correcta."""
    print("\n🔍 Verificando instalación...")
    
    # Verificar imports críticos
    try:
        import mcp
        print("  ✅ MCP library")
    except ImportError:
        print("  ❌ MCP library no disponible")
        return False
    
    try:
        import google.oauth2.credentials
        print("  ✅ Google Auth")
    except ImportError:
        print("  ❌ Google Auth no disponible")
        return False
    
    try:
        from pathlib import Path
        import json
        import asyncio
        print("  ✅ Dependencias estándar")
    except ImportError:
        print("  ❌ Error en dependencias estándar")
        return False
    
    # Verificar estructura de archivos del proyecto
    required_files = [
        "src/server/mcp_server.py",
        "src/core/interfaces.py", 
        "src/gmail/client.py",
        "src/analysis/service.py",
        "src/server/config.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("  ❌ Archivos del proyecto faltantes:")
        for file in missing_files:
            print(f"     - {file}")
        return False
    
    print("  ✅ Archivos del proyecto")
    print("✅ Instalación verificada correctamente")
    return True

def show_next_steps():
    """Mostrar próximos pasos después de la instalación."""
    print("""
    🎉 ¡Instalación completada exitosamente!
    
    📋 PRÓXIMOS PASOS:
    
    1. 🔐 Configurar Gmail API:
       • Ve a Google Cloud Console (console.cloud.google.com)
       • Crea/selecciona un proyecto
       • Habilita Gmail API
       • Crea credenciales OAuth 2.0
       • Descarga credentials.json → credentials/gmail_credentials.json
       • Ejecuta: python scripts/setup_gmail_auth.py
    
    2. 🤖 Configurar AI Provider:
       • Edita el archivo .env
       • Agrega tu OPENAI_API_KEY o ANTHROPIC_API_KEY
       • Configura ANALYSIS_PROVIDER (openai/anthropic)
    
    3. 🚀 Iniciar servidor:
       python -m src.server
    
    4. 🧪 Probar herramientas:
       python scripts/test_mcp_server.py
    
    5. 📖 Ver documentación:
       cat docs/MCP_SERVER.md
    
    ⚠️  IMPORTANTE:
    • Nunca compartas tus API keys
    • Mantén credentials.json seguro
    • Revisa los scopes de Gmail antes de autorizar
    
    🔗 Enlaces útiles:
    • Gmail API: https://developers.google.com/gmail/api
    • MCP Protocol: https://modelcontextprotocol.io/
    • OpenAI API: https://platform.openai.com/api-keys
    • Anthropic API: https://console.anthropic.com/
    """)

def main():
    """Función principal del script de configuración."""
    print_banner()
    
    try:
        # Verificaciones y configuración
        check_python_version()
        
        if not install_dependencies():
            print("❌ Error en la instalación de dependencias")
            sys.exit(1)
        
        create_directory_structure()
        create_env_file()
        create_mcp_config()
        create_gmail_setup_script()
        
        if not verify_installation():
            print("❌ Error en la verificación de instalación")
            sys.exit(1)
        
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante la instalación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()