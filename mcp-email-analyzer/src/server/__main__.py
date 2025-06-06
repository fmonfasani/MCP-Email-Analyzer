# src/server/__main__.py
"""
Punto de entrada principal para el servidor MCP Email Analyzer.
Permite ejecutar el servidor con: python -m src.server
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.server.mcp_server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor MCP Email Analyzer detenido por el usuario.")
    except Exception as e:
        print(f"Error fatal en el servidor: {e}")
        sys.exit(1)