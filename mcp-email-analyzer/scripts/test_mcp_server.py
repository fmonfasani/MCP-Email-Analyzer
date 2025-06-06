#!/usr/bin/env python3
"""
Script de prueba para el servidor MCP Email Analyzer.
Permite probar todas las herramientas MCP implementadas.
"""

import asyncio
import json
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_email_analyze():
    """Probar la herramienta email_analyze."""
    print("🔍 Probando email_analyze...")
    
    # Configurar cliente MCP
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Listar herramientas disponibles
            tools = await session.list_tools()
            print(f"Herramientas disponibles: {[tool.name for tool in tools.tools]}")
            
            # Probar email_analyze
            try:
                result = await session.call_tool(
                    name="email_analyze",
                    arguments={
                        "email_id": "test_email_123",
                        "analysis_types": ["sentiment", "priority", "category"]
                    }
                )
                print("✅ email_analyze resultado:")
                print(json.dumps(result.content[0].text, indent=2))
            except Exception as e:
                print(f"❌ email_analyze error: {e}")

async def test_email_search():
    """Probar la herramienta email_search."""
    print("\n🔍 Probando email_search...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            try:
                result = await session.call_tool(
                    name="email_search",
                    arguments={
                        "query": "is:unread",
                        "filters": {
                            "sender": "example@gmail.com",
                            "has_attachments": True
                        },
                        "limit": 5,
                        "include_analysis": True
                    }
                )
                print("✅ email_search resultado:")
                print(json.dumps(result.content[0].text, indent=2))
            except Exception as e:
                print(f"❌ email_search error: {e}")

async def test_email_classify():
    """Probar la herramienta email_classify."""
    print("\n🔍 Probando email_classify...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            try:
                result = await session.call_tool(
                    name="email_classify",
                    arguments={
                        "email_ids": ["email_1", "email_2", "email_3"],
                        "classification_type": "priority",
                        "batch_size": 2
                    }
                )
                print("✅ email_classify resultado:")
                print(json.dumps(result.content[0].text, indent=2))
            except Exception as e:
                print(f"❌ email_classify error: {e}")

async def test_email_action():
    """Probar la herramienta email_action."""
    print("\n🔍 Probando email_action...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            try:
                # Probar acción de marcar como leído
                result = await session.call_tool(
                    name="email_action",
                    arguments={
                        "email_ids": ["email_1", "email_2"],
                        "action": "read"
                    }
                )
                print("✅ email_action (read) resultado:")
                print(json.dumps(result.content[0].text, indent=2))
                
                # Probar acción de etiquetado
                result = await session.call_tool(
                    name="email_action",
                    arguments={
                        "email_ids": ["email_3", "email_4"],
                        "action": "label",
                        "action_params": {
                            "label_ids": ["LABEL_1", "LABEL_2"]
                        }
                    }
                )
                print("✅ email_action (label) resultado:")
                print(json.dumps(result.content[0].text, indent=2))
                
            except Exception as e:
                print(f"❌ email_action error: {e}")

async def test_all_tools():
    """Ejecutar todas las pruebas de herramientas MCP."""
    print("🚀 Iniciando pruebas del servidor MCP Email Analyzer\n")
    
    try:
        await test_email_analyze()
        await test_email_search()
        await test_email_classify()
        await test_email_action()
        
        print("\n✅ Todas las pruebas completadas!")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")

def main():
    """Función principal del script de pruebas."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Probar servidor MCP Email Analyzer")
    parser.add_argument(
        "--tool",
        choices=["analyze", "search", "classify", "action", "all"],
        default="all",
        help="Herramienta específica a probar"
    )
    
    args = parser.parse_args()
    
    if args.tool == "analyze":
        asyncio.run(test_email_analyze())
    elif args.tool == "search":
        asyncio.run(test_email_search())
    elif args.tool == "classify":
        asyncio.run(test_email_classify())
    elif args.tool == "action":
        asyncio.run(test_email_action())
    else:
        asyncio.run(test_all_tools())

if __name__ == "__main__":
    main()