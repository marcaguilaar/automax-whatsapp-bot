#!/usr/bin/env python3
"""
Python wrapper para el Chat Agent de JavaScript
"""

import subprocess
import json
import os
import sys
from typing import Dict, Any, Optional, List
import tempfile

class CarDealershipChatAgent:
    """
    Wrapper de Python para el agente de chat de JavaScript del concesionario
    """
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()  # Cargar variables de entorno desde .env
        
        self.script_path = os.path.join(os.path.dirname(__file__), 'chat-agent.js')
        self.conversation_histories = {}  # Historial por usuario
        
        # Verificar que el archivo JavaScript existe
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"No se encontró el agente de chat en: {self.script_path}")
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """Obtiene el historial de conversación para un usuario específico"""
        return self.conversation_histories.get(user_id, [])
    
    def add_to_history(self, user_id: str, role: str, content: str):
        """Añade un mensaje al historial de conversación"""
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = []
        
        self.conversation_histories[user_id].append({
            "role": role,
            "content": content
        })
        
        # El límite de historial ahora se maneja en el agente JS
    
    def create_temp_script(self, user_message: str, user_id: str) -> str:
        """
        Crea un script temporal de Node.js para procesar el mensaje
        """
        history = self.get_conversation_history(user_id)
        
        # Crear el script Node.js que ejecutará el agente
        script_dir = os.path.dirname(self.script_path)
        openai_key = os.getenv('OPENAI_API_KEY', '')
        node_script = f"""
const path = require('path');

// Establecer la API key de OpenAI como variable de entorno
process.env.OPENAI_API_KEY = '{openai_key}';

const {{ CarDealershipChatAgent }} = require(path.join(__dirname, 'chat-agent.js'));

async function processMessage() {{
    try {{
        const agent = new CarDealershipChatAgent();
        
        // Cargar historial existente desde Python y configurar en el agente
        const existingHistory = {json.dumps(history)};
        if (existingHistory.length > 0) {{
            // Mantener solo el mensaje del sistema del agente y cargar el historial externo
            const systemMessage = agent.getHistory()[0];
            agent.conversationHistory = [systemMessage, ...existingHistory];
            
            // Aplicar límite de historial
            agent.limitHistory();
        }}
        
        // Procesar el mensaje usando el historial cargado
        const response = await agent.chat("{user_message.replace('"', '\\"')}");
        
        // Retornar respuesta y historial actualizado (sin el mensaje del sistema)
        const fullHistory = agent.getHistory();
        const historyWithoutSystem = fullHistory.slice(1); // Remover mensaje del sistema para Python
        
        const result = {{
            response: response,
            history: historyWithoutSystem
        }};
        
        console.log(JSON.stringify(result));
        
    }} catch (error) {{
        const errorResult = {{
            error: error.message,
            response: "Lo siento, hubo un error procesando tu solicitud. ¿Podrías intentarlo de nuevo?",
            history: []
        }};
        console.log(JSON.stringify(errorResult));
    }}
}}

processMessage();
"""
        return node_script
    
    def process_message(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario usando el agente de JavaScript
        
        Args:
            user_message: Mensaje del usuario
            user_id: ID único del usuario
            
        Returns:
            Dict con la respuesta del agente y metadatos
        """
        try:
            # Verificar que Node.js está disponible
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                return {
                    "response": "❌ Error: Node.js no está instalado. Por favor instala Node.js para usar el agente de chat.",
                    "error": "nodejs_not_found"
                }
            
            # Crear script temporal
            node_script = self.create_temp_script(user_message, user_id)
            
            # Escribir script a archivo temporal en el mismo directorio que chat-agent.js
            script_dir = os.path.dirname(self.script_path)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, dir=script_dir) as temp_file:
                temp_file.write(node_script)
                temp_script_path = temp_file.name
            
            try:
                # Ejecutar el script de Node.js
                result = subprocess.run(
                    ['node', temp_script_path],
                    cwd=os.path.dirname(self.script_path),
                    capture_output=True,
                    text=True,
                    timeout=30  # Timeout de 30 segundos
                )
                
                if result.returncode != 0:
                    print(f"❌ Error en Node.js: {result.stderr}")
                    return {
                        "response": "Lo siento, hubo un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?",
                        "error": "nodejs_execution_error",
                        "details": result.stderr
                    }
                
                # Parsear la respuesta JSON
                try:
                    response_data = json.loads(result.stdout.strip())
                    
                    if "error" in response_data:
                        print(f"❌ Error del agente: {response_data['error']}")
                        return {
                            "response": response_data.get("response", "Error procesando mensaje"),
                            "error": "agent_error",
                            "details": response_data["error"]
                        }
                    
                    # Actualizar historial local con el historial devuelto por el agente JS
                    if "history" in response_data:
                        self.conversation_histories[user_id] = response_data["history"]
                    
                    return {
                        "response": response_data.get("response", ""),
                        "status": "success"
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error parseando JSON: {e}")
                    print(f"Salida de Node.js: {result.stdout}")
                    return {
                        "response": "Hubo un error interno. ¿Podrías intentarlo de nuevo?",
                        "error": "json_parse_error",
                        "details": str(e)
                    }
                
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_script_path)
                except:
                    pass
            
        except subprocess.TimeoutExpired:
            return {
                "response": "La consulta está tomando demasiado tiempo. ¿Podrías ser más específico?",
                "error": "timeout"
            }
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return {
                "response": "Lo siento, hubo un error inesperado. ¿Podrías intentarlo de nuevo?",
                "error": "unexpected_error",
                "details": str(e)
            }
    
    def get_conversation_summary(self, user_id: str) -> str:
        """
        Genera un resumen de la conversación para un usuario
        """
        history = self.get_conversation_history(user_id)
        
        if not history:
            return "Sin conversación previa"
        
        user_messages = [msg for msg in history if msg["role"] == "user"]
        assistant_messages = [msg for msg in history if msg["role"] == "assistant"]
        
        summary = f"Conversación: {len(history)} mensajes ({len(user_messages)} del usuario)"
        
        # Extraer temas principales de los mensajes del usuario
        topics = []
        for msg in user_messages[-3:]:  # Últimos 3 mensajes del usuario
            content = msg["content"].lower()
            if any(word in content for word in ["busco", "quiero", "necesito", "auto", "carro", "vehículo"]):
                topics.append("búsqueda de autos")
            if any(word in content for word in ["cita", "prueba", "manejo", "agendar", "visita"]):
                topics.append("agendamiento")
            if any(word in content for word in ["precio", "financiamiento", "crédito", "pago", "costo"]):
                topics.append("precios/financiamiento")
            if any(word in content for word in ["información", "horario", "ubicación", "contacto"]):
                topics.append("información general")
        
        if topics:
            summary += f". Temas: {', '.join(set(topics))}"
        
        return summary


# Función de prueba
def test_agent():
    """Función de prueba para el agente"""
    print("🧪 PROBANDO AGENTE DE CHAT PYTHON")
    print("=" * 50)
    
    agent = CarDealershipChatAgent()
    
    test_messages = [
        "Hola, busco un auto económico",
        "¿Qué BMW tienen disponibles?",
        "Quiero agendar una cita para mañana"
    ]
    
    user_id = "test_user"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 TEST {i}: {message}")
        print("-" * 40)
        
        result = agent.process_message(message, user_id)
        
        print(f"Respuesta: {result.get('response', 'Sin respuesta')}")
        
        if result.get('error'):
            print(f"⚠️  Error: {result['error']}")
            if 'details' in result:
                print(f"   Detalles: {result['details']}")
        
    # Mostrar resumen
    print(f"\n📊 RESUMEN: {agent.get_conversation_summary(user_id)}")


if __name__ == "__main__":
    test_agent()
