import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from chat_agent_python import CarDealershipChatAgent

load_dotenv()

class CarDealershipWhatsAppAgent:
    """
    Adaptador del agente del concesionario para WhatsApp
    """
    
    def __init__(self):
        # Usar nuestro agente real de chat
        self.chat_agent = CarDealershipChatAgent()
        
        # Almacenamiento temporal de conversaciones por usuario
        # (después será reemplazado por Firestore)
        self.user_conversations: Dict[str, List[Dict[str, str]]] = {}
        
        # Estado de cada usuario
        self.user_states: Dict[str, Dict[str, Any]] = {}
    
    def get_user_history(self, user_phone: str) -> List[Dict[str, str]]:
        """
        Obtiene el historial de conversación de un usuario
        """
        if user_phone not in self.user_conversations:
            self.user_conversations[user_phone] = []
        
        return self.user_conversations[user_phone]
    
    def get_user_state(self, user_phone: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual del usuario
        """
        if user_phone not in self.user_states:
            self.user_states[user_phone] = {
                "status": "new",
                "last_interaction": None,
                "selected_cars": [],
                "appointment_data": {},
                "preferences": {}
            }
        
        return self.user_states[user_phone]
    
    def update_user_state(self, user_phone: str, state_updates: Dict[str, Any]):
        """
        Actualiza el estado del usuario
        """
        current_state = self.get_user_state(user_phone)
        current_state.update(state_updates)
        self.user_states[user_phone] = current_state
    
    def add_to_conversation(self, user_phone: str, role: str, content: str):
        """
        Añade un mensaje al historial de conversación
        """
        conversation = self.get_user_history(user_phone)
        conversation.append({
            "role": role,
            "content": content
        })
        
        # Mantener solo los últimos 50 mensajes para evitar tokens excesivos
        if len(conversation) > 50:
            conversation = conversation[-50:]
        
        self.user_conversations[user_phone] = conversation
    
    def process_message(self, user_phone: str, user_name: Optional[str], 
                             message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario y devuelve la respuesta
        """
        try:
            # Añadir mensaje del usuario al historial
            self.add_to_conversation(user_phone, "user", message)
            
            # Procesar con el agente de chat usando la nueva interfaz
            agent_result = self.chat_agent.process_message(message, user_phone)
            
            if agent_result.get("error"):
                # Si hay error, devolver mensaje de error amigable
                response = agent_result.get("response", "Lo siento, hubo un problema. ¿Podrías intentarlo de nuevo?")
            else:
                response = agent_result.get("response", "")
            
            # Añadir respuesta del agente al historial
            self.add_to_conversation(user_phone, "assistant", response)
            
            # Verificar si hay una imagen para enviar (cuando se solicitan detalles de vehículo)
            vehicle_image = self.chat_agent.get_last_vehicle_image()
            
            # Actualizar estado del usuario
            self.update_user_state(user_phone, {
                "last_interaction": message,
                "status": "active"
            })
            
            # Determinar tipo de respuesta y acciones adicionales
            response_data = self._analyze_response(response, user_phone)
            
            result = {
                "success": True,
                "response": response,
                "response_type": response_data["type"],
                "actions": response_data["actions"],
                "suggestions": response_data["suggestions"]
            }
            
            # Agregar información de imagen si está disponible
            if vehicle_image:
                result["image_path"] = vehicle_image
                result["has_image"] = True
            else:
                result["has_image"] = False
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing message from {user_phone}: {str(e)}")
            return {
                "success": False,
                "response": "Sorry, there was an error processing your message. Can you try again?",
                "response_type": "error",
                "actions": [],
                "suggestions": [],
                "has_image": False
            }
    
    def _analyze_response(self, response: str, user_phone: str) -> Dict[str, Any]:
        """
        Analiza la respuesta del agente para determinar acciones de WhatsApp
        """
        response_lower = response.lower()
        
        # Detectar si se mencionan autos específicos
        car_mentions = []
        if "bmw" in response_lower:
            car_mentions.append("BMW")
        if "toyota" in response_lower:
            car_mentions.append("Toyota")
        if "tesla" in response_lower:
            car_mentions.append("Tesla")
        if "honda" in response_lower:
            car_mentions.append("Honda")
        if "ford" in response_lower:
            car_mentions.append("Ford")
        if "audi" in response_lower:
            car_mentions.append("Audi")
        
        actions = []
        suggestions = []
        response_type = "text"
        
        # Si menciona autos, ofrecer botones para ver más
        if car_mentions:
            response_type = "cars_mentioned"
            actions.append({
                "type": "buttons",
                "data": {
                    "header": "🚗 Autos encontrados",
                    "body": "¿Te gustaría ver más detalles de alguno?",
                    "buttons": [
                        {"id": "see_details", "title": "Ver detalles"},
                        {"id": "compare_cars", "title": "Comparar"},
                        {"id": "schedule_test", "title": "Agendar prueba"}
                    ]
                }
            })
        
        # Si menciona precios, ofrecer financiamiento
        if "$" in response or "precio" in response_lower or "cuesta" in response_lower:
            response_type = "price_mentioned"
            suggestions.append({
                "type": "buttons",
                "data": {
                    "header": "💰 Opciones de pago",
                    "body": "¿Te interesa información sobre financiamiento?",
                    "buttons": [
                        {"id": "financing_options", "title": "Ver financiamiento"},
                        {"id": "calculate_payment", "title": "Calcular pago"},
                        {"id": "trade_in", "title": "Valor de cambio"}
                    ]
                }
            })
        
        # Si menciona citas o horarios
        if any(word in response_lower for word in ["cita", "horarios", "agendar", "appointment"]):
            response_type = "appointment_mentioned"
            actions.append({
                "type": "buttons",
                "data": {
                    "header": "📅 Agendar cita",
                    "body": "¿Qué tipo de cita necesitas?",
                    "buttons": [
                        {"id": "test_drive", "title": "Prueba de manejo"},
                        {"id": "consultation", "title": "Consulta"},
                        {"id": "inspection", "title": "Inspección"}
                    ]
                }
            })
        
        # Si menciona contacto o ubicación
        if any(word in response_lower for word in ["contacto", "ubicación", "dirección", "teléfono"]):
            response_type = "contact_mentioned"
            actions.append({
                "type": "contact_info",
                "data": {
                    "send_location": True,
                    "send_contact": True
                }
            })
        
        # Si no hay autos disponibles
        if "no hay" in response_lower or "no tengo" in response_lower:
            response_type = "no_results"
            suggestions.append({
                "type": "buttons",
                "data": {
                    "header": "🔍 Otras opciones",
                    "body": "¿Te gustaría intentar otra búsqueda?",
                    "buttons": [
                        {"id": "broaden_search", "title": "Ampliar búsqueda"},
                        {"id": "notify_arrival", "title": "Notificar llegada"},
                        {"id": "see_all_cars", "title": "Ver todo"}
                    ]
                }
            })
        
        return {
            "type": response_type,
            "actions": actions,
            "suggestions": suggestions,
            "car_mentions": car_mentions
        }
    
    def get_welcome_message(self, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate welcome message for new users - ENGLISH VERSION
        """
        name_part = f" {user_name}" if user_name else ""
        
        return {
            "response": f"Hello{name_part}! 👋 Welcome to AutoMax, your trusted car dealership.\n\n🚗 I'm here to help you find the perfect car for you.\n\nHow can I assist you today?",
            "response_type": "welcome",
            "actions": [{
                "type": "buttons",
                "data": {
                    "header": "🚗 AutoMax",
                    "body": "What would you like to do?",
                    "buttons": [
                        {"id": "search_cars", "title": "🔍 Search cars"},
                        {"id": "schedule_appointment", "title": "📅 Schedule appointment"},
                        {"id": "contact_info", "title": "📞 Contact"}
                    ]
                }
            }],
            "suggestions": []
        }
    
    def get_conversation_summary(self, user_phone: str) -> str:
        """
        Genera un resumen de la conversación del usuario
        """
        conversation = self.get_user_history(user_phone)
        
        if not conversation:
            return "Sin conversación previa"
        
        # Contar mensajes
        total_messages = len(conversation)
        user_messages = len([msg for msg in conversation if msg["role"] == "user"])
        
        # Obtener últimos temas mencionados
        recent_messages = conversation[-10:] if len(conversation) > 10 else conversation
        recent_content = " ".join([msg["content"] for msg in recent_messages])
        
        # Detectar temas principales
        topics = []
        if any(brand in recent_content.lower() for brand in ["bmw", "toyota", "tesla", "honda", "ford", "audi"]):
            topics.append("búsqueda de autos")
        if any(word in recent_content.lower() for word in ["cita", "agendar", "appointment", "schedule"]):
            topics.append("appointment")
        if any(word in recent_content.lower() for word in ["precio", "financiamiento", "$", "price", "financing"]):
            topics.append("pricing/financing")
        
        return f"Conversation: {total_messages} messages ({user_messages} from user). Topics: {', '.join(topics) if topics else 'general conversation'}."
    
    def reset_user_session(self, user_phone: str):
        """
        Reset a user's session
        """
        if user_phone in self.user_conversations:
            del self.user_conversations[user_phone]
        if user_phone in self.user_states:
            del self.user_states[user_phone]
        
        print(f"🔄 Sesión reiniciada para {user_phone}")
    
    def get_active_users_count(self) -> int:
        """
        Obtiene el número de usuarios activos
        """
        return len(self.user_conversations)
