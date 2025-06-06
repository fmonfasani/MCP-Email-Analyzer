# src/server/mcp_server.py
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from mcp import Server
from mcp.types import Tool, TextContent, CallToolResult, ErrorCode, McpError

from ..core.interfaces import EmailData, AnalysisResult, EmailRepository
from ..gmail.client import GmailRepository
from ..analysis.service import EmailAnalyzerService
from .config import Settings

# Configurar logging estructurado
logger = logging.getLogger(__name__)

class EmailAnalyzerServer:
    """Servidor MCP para análisis de emails con Gmail integration."""
    
    def __init__(self, config: Settings):
        self.server = Server("email-analyzer")
        self.config = config
        self.gmail_repo = GmailRepository(config.gmail)
        self.analyzer = EmailAnalyzerService(config.analyzer)
        self._register_tools()
    
    def _register_tools(self):
        """Registrar herramientas MCP exactas según especificación."""
        
        # Tool 1: email_analyze - Analizar email individual
        @self.server.call_tool()
        async def email_analyze(arguments: Dict[str, Any]) -> List[TextContent]:
            """Analizar un email individual con tipos de análisis específicos."""
            try:
                email_id = arguments.get("email_id")
                analysis_types = arguments.get("analysis_types", ["sentiment", "priority", "category", "summary"])
                
                if not email_id:
                    raise McpError(ErrorCode.INVALID_PARAMS, "email_id is required")
                
                # Obtener email
                email_data = await self.gmail_repo.get_email(email_id)
                if not email_data:
                    raise McpError(ErrorCode.INVALID_PARAMS, f"Email {email_id} not found")
                
                # Realizar análisis
                analysis_result = await self.analyzer.analyze_email(email_data, analysis_types)
                
                # Log estructurado
                logger.info(json.dumps({
                    "action": "email_analyze",
                    "email_id": email_id,
                    "analysis_types": analysis_types,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": True
                }))
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "email_id": email_id,
                        "subject": email_data.subject,
                        "analysis": {
                            "sentiment": analysis_result.sentiment if "sentiment" in analysis_types else None,
                            "priority": analysis_result.priority if "priority" in analysis_types else None,
                            "category": analysis_result.category if "category" in analysis_types else None,
                            "summary": analysis_result.summary if "summary" in analysis_types else None
                        },
                        "confidence": analysis_result.confidence,
                        "analyzed_at": analysis_result.analyzed_at.isoformat()
                    }, indent=2)
                )]
                
            except Exception as e:
                logger.error(json.dumps({
                    "action": "email_analyze",
                    "error": str(e),
                    "email_id": arguments.get("email_id"),
                    "timestamp": datetime.utcnow().isoformat()
                }))
                raise McpError(ErrorCode.INTERNAL_ERROR, f"Analysis failed: {str(e)}")
        
        # Tool 2: email_classify - Clasificar emails en lote
        @self.server.call_tool()
        async def email_classify(arguments: Dict[str, Any]) -> List[TextContent]:
            """Clasificar múltiples emails en lote."""
            try:
                email_ids = arguments.get("email_ids", [])
                classification_type = arguments.get("classification_type", "category")
                batch_size = arguments.get("batch_size", 10)
                
                if not email_ids:
                    raise McpError(ErrorCode.INVALID_PARAMS, "email_ids list is required")
                
                if len(email_ids) > 50:
                    raise McpError(ErrorCode.INVALID_PARAMS, "Maximum 50 emails per batch")
                
                # Procesar en lotes
                results = []
                for i in range(0, len(email_ids), batch_size):
                    batch = email_ids[i:i + batch_size]
                    batch_results = await self._classify_batch(batch, classification_type)
                    results.extend(batch_results)
                
                logger.info(json.dumps({
                    "action": "email_classify",
                    "total_emails": len(email_ids),
                    "classification_type": classification_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": True
                }))
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "classification_type": classification_type,
                        "total_processed": len(results),
                        "results": results,
                        "processed_at": datetime.utcnow().isoformat()
                    }, indent=2)
                )]
                
            except Exception as e:
                logger.error(json.dumps({
                    "action": "email_classify",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
                raise McpError(ErrorCode.INTERNAL_ERROR, f"Classification failed: {str(e)}")
        
        # Tool 3: email_action - Ejecutar acciones
        @self.server.call_tool()
        async def email_action(arguments: Dict[str, Any]) -> List[TextContent]:
            """Ejecutar acciones sobre emails (read, archive, delete, label)."""
            try:
                email_ids = arguments.get("email_ids", [])
                action = arguments.get("action")
                action_params = arguments.get("action_params", {})
                
                if not email_ids:
                    raise McpError(ErrorCode.INVALID_PARAMS, "email_ids list is required")
                
                if action not in ["read", "archive", "delete", "label"]:
                    raise McpError(ErrorCode.INVALID_PARAMS, 
                                 "action must be one of: read, archive, delete, label")
                
                # Ejecutar acción
                results = await self._execute_action(email_ids, action, action_params)
                
                logger.info(json.dumps({
                    "action": "email_action",
                    "email_action_type": action,
                    "email_count": len(email_ids),
                    "success_count": sum(1 for r in results if r["success"]),
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "action": action,
                        "total_emails": len(email_ids),
                        "results": results,
                        "executed_at": datetime.utcnow().isoformat()
                    }, indent=2)
                )]
                
            except Exception as e:
                logger.error(json.dumps({
                    "action": "email_action",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
                raise McpError(ErrorCode.INTERNAL_ERROR, f"Action execution failed: {str(e)}")
        
        # Tool 4: email_search - Buscar emails con filtros
        @self.server.call_tool()
        async def email_search(arguments: Dict[str, Any]) -> List[TextContent]:
            """Buscar emails con filtros específicos."""
            try:
                query = arguments.get("query", "")
                filters = arguments.get("filters", {})
                limit = arguments.get("limit", 20)
                include_analysis = arguments.get("include_analysis", False)
                
                if limit > 100:
                    raise McpError(ErrorCode.INVALID_PARAMS, "Maximum limit is 100")
                
                # Realizar búsqueda
                search_results = await self.gmail_repo.search_emails(
                    query=query,
                    sender=filters.get("sender"),
                    subject_contains=filters.get("subject_contains"),
                    date_from=filters.get("date_from"),
                    date_to=filters.get("date_to"),
                    has_attachments=filters.get("has_attachments"),
                    is_unread=filters.get("is_unread"),
                    limit=limit
                )
                
                # Incluir análisis si se solicita
                results = []
                for email in search_results:
                    result = {
                        "email_id": email.email_id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "received_at": email.received_at.isoformat(),
                        "is_read": email.is_read,
                        "has_attachments": email.has_attachments
                    }
                    
                    if include_analysis:
                        analysis = await self.analyzer.analyze_email(email, ["category", "priority"])
                        result["analysis"] = {
                            "category": analysis.category,
                            "priority": analysis.priority,
                            "confidence": analysis.confidence
                        }
                    
                    results.append(result)
                
                logger.info(json.dumps({
                    "action": "email_search",
                    "query": query,
                    "results_count": len(results),
                    "include_analysis": include_analysis,
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "query": query,
                        "filters": filters,
                        "total_results": len(results),
                        "results": results,
                        "searched_at": datetime.utcnow().isoformat()
                    }, indent=2)
                )]
                
            except Exception as e:
                logger.error(json.dumps({
                    "action": "email_search",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
                raise McpError(ErrorCode.INTERNAL_ERROR, f"Search failed: {str(e)}")
        
        # Registrar herramientas con schemas
        self.server.register_tool(
            Tool(
                name="email_analyze",
                description="Analyze an individual email with specific analysis types",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {"type": "string", "description": "Gmail email ID"},
                        "analysis_types": {
                            "type": "array",
                            "items": {"enum": ["sentiment", "priority", "category", "summary"]},
                            "description": "Types of analysis to perform",
                            "default": ["sentiment", "priority", "category", "summary"]
                        }
                    },
                    "required": ["email_id"]
                }
            )
        )
        
        self.server.register_tool(
            Tool(
                name="email_classify",
                description="Classify multiple emails in batch",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of Gmail email IDs",
                            "maxItems": 50
                        },
                        "classification_type": {
                            "type": "string",
                            "enum": ["category", "priority", "sentiment"],
                            "description": "Type of classification",
                            "default": "category"
                        },
                        "batch_size": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20,
                            "description": "Number of emails to process per batch",
                            "default": 10
                        }
                    },
                    "required": ["email_ids"]
                }
            )
        )
        
        self.server.register_tool(
            Tool(
                name="email_action",
                description="Execute actions on emails (read, archive, delete, label)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of Gmail email IDs"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["read", "archive", "delete", "label"],
                            "description": "Action to execute"
                        },
                        "action_params": {
                            "type": "object",
                            "description": "Additional parameters for the action",
                            "properties": {
                                "label_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Label IDs for labeling action"
                                }
                            }
                        }
                    },
                    "required": ["email_ids", "action"]
                }
            )
        )
        
        self.server.register_tool(
            Tool(
                name="email_search",
                description="Search emails with specific filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail search query",
                            "default": ""
                        },
                        "filters": {
                            "type": "object",
                            "description": "Additional search filters",
                            "properties": {
                                "sender": {"type": "string"},
                                "subject_contains": {"type": "string"},
                                "date_from": {"type": "string", "format": "date"},
                                "date_to": {"type": "string", "format": "date"},
                                "has_attachments": {"type": "boolean"},
                                "is_unread": {"type": "boolean"}
                            }
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of results",
                            "default": 20
                        },
                        "include_analysis": {
                            "type": "boolean",
                            "description": "Include email analysis in results",
                            "default": False
                        }
                    }
                }
            )
        )
    
    async def _classify_batch(self, email_ids: List[str], classification_type: str) -> List[Dict]:
        """Clasificar un lote de emails."""
        results = []
        
        for email_id in email_ids:
            try:
                email_data = await self.gmail_repo.get_email(email_id)
                if not email_data:
                    results.append({
                        "email_id": email_id,
                        "success": False,
                        "error": "Email not found"
                    })
                    continue
                
                analysis = await self.analyzer.analyze_email(email_data, [classification_type])
                
                classification_value = getattr(analysis, classification_type, None)
                
                results.append({
                    "email_id": email_id,
                    "subject": email_data.subject,
                    "classification": classification_value,
                    "confidence": analysis.confidence,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "email_id": email_id,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def _execute_action(self, email_ids: List[str], action: str, action_params: Dict) -> List[Dict]:
        """Ejecutar acción sobre emails."""
        results = []
        
        for email_id in email_ids:
            try:
                success = False
                
                if action == "read":
                    success = await self.gmail_repo.mark_as_read(email_id)
                elif action == "archive":
                    success = await self.gmail_repo.archive_email(email_id)
                elif action == "delete":
                    success = await self.gmail_repo.delete_email(email_id)
                elif action == "label":
                    label_ids = action_params.get("label_ids", [])
                    if label_ids:
                        success = await self.gmail_repo.add_labels(email_id, label_ids)
                    else:
                        raise ValueError("label_ids required for label action")
                
                results.append({
                    "email_id": email_id,
                    "action": action,
                    "success": success
                })
                
            except Exception as e:
                results.append({
                    "email_id": email_id,
                    "action": action,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def run(self):
        """Ejecutar el servidor MCP."""
        logger.info(json.dumps({
            "event": "server_starting",
            "server_name": "email-analyzer",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        try:
            # Inicializar conexiones
            await self.gmail_repo.initialize()
            await self.analyzer.initialize()
            
            logger.info(json.dumps({
                "event": "server_started",
                "server_name": "email-analyzer",
                "tools_registered": 4,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Ejecutar servidor
            await self.server.run()
            
        except Exception as e:
            logger.error(json.dumps({
                "event": "server_error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }))
            raise
        finally:
            # Cleanup
            await self.gmail_repo.cleanup()
            await self.analyzer.cleanup()
            
            logger.info(json.dumps({
                "event": "server_stopped",
                "timestamp": datetime.utcnow().isoformat()
            }))

async def main():
    """Punto de entrada principal del servidor MCP."""
    # Cargar configuración
    config = Settings()
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(message)s',  # Solo mensaje JSON
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/mcp_server.log') if config.log_to_file else logging.NullHandler()
        ]
    )
    
    # Crear y ejecutar servidor
    server = EmailAnalyzerServer(config)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())