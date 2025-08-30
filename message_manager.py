import time
from typing import Dict, Any, Optional, List
from whatsapp_sender import WhatsAppSender, create_main_menu_buttons, create_car_type_buttons, create_appointment_buttons
from car_dealership_agent import CarDealershipWhatsAppAgent

class MessageManager:
    """
    Gestiona los mensajes entre WhatsApp y el agente del concesionario
    """
    
    def __init__(self, whatsapp_sender: WhatsAppSender, car_agent: CarDealershipWhatsAppAgent):
        self.sender = whatsapp_sender
        self.car_agent = car_agent  # Cambié de 'agent' a 'car_agent' para consistencia
        
        # Información del concesionario
        self.dealership_info = {
            "name": "AutoMax",
            "address": "123 Avenida Principal, Ciudad, Estado 12345",
            "phone": "(555) 123-4567",
            "email": "info@automax.com",
            "latitude": 19.4326,
            "longitude": -99.1332,  # Coordenadas de ejemplo
            "hours": {
                "Lunes": "9:00 AM - 8:00 PM",
                "Martes": "9:00 AM - 8:00 PM", 
                "Miércoles": "9:00 AM - 8:00 PM",
                "Jueves": "9:00 AM - 8:00 PM",
                "Viernes": "9:00 AM - 8:00 PM",
                "Sábado": "9:00 AM - 6:00 PM",
                "Domingo": "12:00 PM - 5:00 PM"
            }
        }
    
    async def handle_text_message(self, user_phone: str, user_name: Optional[str], 
                                  message_text: str, message_id: str) -> Dict[str, Any]:
        """
        Maneja mensajes de texto del usuario
        """
        try:
            print(f"📝 Procesando texto de {user_name or user_phone}: {message_text}")
            
            # Marcar mensaje como leído
            self.sender.mark_as_read(message_id)
            
            # Verificar si es un usuario nuevo
            user_state = self.car_agent.get_user_state(user_phone)
            
            if user_state["status"] == "new":
                # Usuario nuevo - mostrar bienvenida
                welcome_data = self.car_agent.get_welcome_message(user_name)
                self._send_response(user_phone, welcome_data)
                
                # Actualizar estado
                self.car_agent.update_user_state(user_phone, {"status": "welcomed"})
                return {"status": "welcome_sent"}
            
            # Comandos especiales
            if message_text.lower().strip() in ["/start", "/menu", "/inicio", "menu", "inicio"]:
                return self._send_main_menu(user_phone)
            
            if message_text.lower().strip() in ["/reset", "/reiniciar", "reiniciar"]:
                self.car_agent.reset_user_session(user_phone)
                self.sender.send_text(user_phone, "🔄 Sesión reiniciada. ¡Empecemos de nuevo!")
                return {"status": "session_reset"}
            
            if message_text.lower().strip() in ["/help", "/ayuda", "ayuda"]:
                return self._send_help_message(user_phone)
            
            # Procesar mensaje con el agente de chat
            agent_result = self.car_agent.process_message(user_phone, user_name, message_text, "text")
            
            if agent_result["success"]:
                # Enviar respuesta del agente
                response_data = {
                    "response": agent_result["response"],
                    "response_type": agent_result["response_type"],
                    "actions": agent_result["actions"],
                    "suggestions": agent_result["suggestions"],
                    "has_image": agent_result.get("has_image", False),
                    "image_path": agent_result.get("image_path")
                }
                
                self._send_response(user_phone, response_data)
                return {"status": "processed", "response_type": agent_result["response_type"]}
            else:
                # Error en el procesamiento
                self.sender.send_text(user_phone, agent_result["response"])
                return {"status": "error"}
                
        except Exception as e:
            print(f"❌ Error manejando texto: {str(e)}")
            self.sender.send_text(user_phone, 
                "Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo.")
            return {"status": "error", "details": str(e)}
    
    async def handle_interactive_message(self, user_phone: str, user_name: Optional[str],
                                       button_id: str, button_title: str, message_id: str) -> Dict[str, Any]:
        """
        Maneja botones y respuestas interactivas
        """
        try:
            print(f"🔘 Procesando botón de {user_name or user_phone}: {button_id}")
            
            # Marcar como leído
            self.sender.mark_as_read(message_id)
            
            # Procesar botones del menú principal
            if button_id == "search_cars":
                return self._handle_search_cars(user_phone)
            
            elif button_id == "schedule_appointment":
                return self._handle_schedule_appointment(user_phone)
            
            elif button_id == "contact_info":
                return self._handle_contact_info(user_phone)
            
            # Procesar botones de tipos de auto
            elif button_id.startswith("car_type_"):
                car_type = button_id.replace("car_type_", "")
                return self._handle_car_type_selection(user_phone, car_type)
            
            # Procesar botones de citas
            elif button_id in ["test_drive", "consultation", "inspection"]:
                return self._handle_appointment_type(user_phone, button_id)
            
            # Procesar otros botones específicos del agente
            elif button_id in ["see_details", "compare_cars", "schedule_test"]:
                # Convertir acción de botón en mensaje de texto para el agente
                action_messages = {
                    "see_details": "Quiero ver más detalles de los autos",
                    "compare_cars": "Quiero comparar los autos",
                    "schedule_test": "Quiero agendar una prueba de manejo"
                }
                
                message_text = action_messages.get(button_id, button_title)
                return await self.handle_text_message(user_phone, user_name, message_text, message_id)
            
            else:
                # Botón no reconocido, tratar como mensaje de texto
                return await self.handle_text_message(user_phone, user_name, button_title, message_id)
                
        except Exception as e:
            print(f"❌ Error manejando botón: {str(e)}")
            self.sender.send_text(user_phone, "Error procesando tu selección.")
            return {"status": "error", "details": str(e)}
    
    async def handle_list_selection(self, user_phone: str, user_name: Optional[str],
                                   selection_id: str, selection_title: str, message_id: str) -> Dict[str, Any]:
        """
        Maneja selecciones de listas
        """
        try:
            print(f"📋 Procesando selección de {user_name or user_phone}: {selection_id}")
            
            # Marcar como leído
            self.sender.mark_as_read(message_id)
            
            # Convertir selección en mensaje de texto para el agente
            message_text = f"Me interesa: {selection_title}"
            return await self.handle_text_message(user_phone, user_name, message_text, message_id)
            
        except Exception as e:
            print(f"❌ Error manejando lista: {str(e)}")
            return {"status": "error", "details": str(e)}
    
    async def handle_image_message(self, user_phone: str, user_name: Optional[str],
                                  image_id: str, caption: str, message_id: str) -> Dict[str, Any]:
        """
        Maneja imágenes enviadas por el usuario
        """
        try:
            print(f"🖼️ Procesando imagen de {user_name or user_phone}: {image_id}")
            
            # Marcar como leído
            self.sender.mark_as_read(message_id)
            
            # Por ahora, solo responder que recibimos la imagen
            response = "📸 ¡Gracias por la imagen! "
            
            if caption:
                response += f"Veo que escribiste: '{caption}'. "
                # Procesar el caption como mensaje de texto
                await self.handle_text_message(user_phone, user_name, caption, message_id)
            else:
                response += "¿En qué puedo ayudarte con respecto a esta imagen?"
                self.sender.send_text(user_phone, response)
            
            return {"status": "image_received"}
            
        except Exception as e:
            print(f"❌ Error manejando imagen: {str(e)}")
            return {"status": "error", "details": str(e)}
    
    def _send_response(self, user_phone: str, response_data: Dict[str, Any]):
        """
        Envía respuestas de texto y opcionalmente imágenes
        """
        # Enviar imagen primero si está disponible
        if response_data.get("has_image", False) and response_data.get("image_path"):
            image_path = response_data["image_path"]
            print(f"📸 Enviando imagen: {image_path}")
            
            # Verificar que el archivo existe
            import os
            full_path = os.path.join(os.getcwd(), image_path)
            if os.path.exists(full_path):
                try:
                    # Enviar imagen con el texto como caption
                    self.sender.send_image(user_phone, full_path, response_data["response"])
                    print(f"✅ Imagen enviada exitosamente: {image_path}")
                    return  # No enviar texto adicional ya que va como caption
                except Exception as e:
                    print(f"❌ Error enviando imagen {image_path}: {e}")
                    # Si falla el envío de imagen, enviar solo texto
                    self.sender.send_text(user_phone, response_data["response"])
            else:
                print(f"❌ Imagen no encontrada: {full_path}")
                # Si no existe la imagen, enviar solo texto
                self.sender.send_text(user_phone, response_data["response"])
        else:
            # Solo enviar el texto principal
            self.sender.send_text(user_phone, response_data["response"])
        
        # NOTA: Botones, acciones y sugerencias desactivados intencionalmente
        # Para reactivar, descomenta las secciones comentadas abajo
        
        # # Pequeña pausa para evitar saturar WhatsApp
        # time.sleep(0.5)
        # 
        # # Enviar acciones (botones, listas, etc.)
        # for action in response_data.get("actions", []):
        #     if action["type"] == "buttons":
        #         data = action["data"]
        #         self.sender.send_buttons(
        #             user_phone,
        #             data["header"],
        #             data["body"],
        #             data["buttons"],
        #             "AutoMax"
        #         )
        #         time.sleep(0.3)
        #     
        #     elif action["type"] == "contact_info":
        #         self._send_contact_info(user_phone)
        #         time.sleep(0.3)
        # 
        # # Enviar sugerencias si las hay
        # for suggestion in response_data.get("suggestions", []):
        #     if suggestion["type"] == "buttons":
        #         data = suggestion["data"]
        #         self.sender.send_buttons(
        #             user_phone,
        #             data["header"],
        #             data["body"],
        #             data["buttons"],
        #             "AutoMax"
        #         )
        #         time.sleep(0.3)
    
    def _send_main_menu(self, user_phone: str) -> Dict[str, Any]:
        """
        Envía el menú principal
        """
        self.sender.send_buttons(
            user_phone,
            "🚗 AutoMax - Menú Principal",
            "¿En qué puedo ayudarte hoy?",
            create_main_menu_buttons(),
            "Selecciona una opción"
        )
        return {"status": "main_menu_sent"}
    
    def _handle_search_cars(self, user_phone: str) -> Dict[str, Any]:
        """
        Maneja la búsqueda de autos
        """
        self.sender.send_buttons(
            user_phone,
            "🔍 Buscar Autos",
            "¿Qué tipo de auto te interesa?",
            create_car_type_buttons(),
            "AutoMax"
        )
        return {"status": "car_search_menu_sent"}
    
    def _handle_car_type_selection(self, user_phone: str, car_type: str) -> Dict[str, Any]:
        """
        Maneja la selección de tipo de auto
        """
        type_messages = {
            "economic": "Busco un auto económico",
            "family": "Busco un auto familiar", 
            "luxury": "Busco un auto de lujo"
        }
        
        message = type_messages.get(car_type, "Busco un auto")
        return self.handle_text_message(user_phone, None, message, "button_selection")
    
    def _handle_schedule_appointment(self, user_phone: str) -> Dict[str, Any]:
        """
        Maneja el agendamiento de citas
        """
        self.sender.send_buttons(
            user_phone,
            "📅 Agendar Cita",
            "¿Qué tipo de cita necesitas?",
            create_appointment_buttons(),
            "AutoMax"
        )
        return {"status": "appointment_menu_sent"}
    
    def _handle_appointment_type(self, user_phone: str, appointment_type: str) -> Dict[str, Any]:
        """
        Maneja el tipo de cita seleccionado
        """
        type_messages = {
            "test_drive": "Quiero agendar una prueba de manejo",
            "consultation": "Quiero agendar una consulta",
            "inspection": "Quiero agendar una inspección"
        }
        
        message = type_messages.get(appointment_type, "Quiero agendar una cita")
        return self.handle_text_message(user_phone, None, message, "appointment_selection")
    
    def _handle_contact_info(self, user_phone: str) -> Dict[str, Any]:
        """
        Maneja la información de contacto
        """
        self._send_contact_info(user_phone)
        return {"status": "contact_info_sent"}
    
    def _send_contact_info(self, user_phone: str):
        """
        Envía información de contacto completa
        """
        # Enviar horarios
        hours_text = "🕒 *Horarios de atención:*\n\n"
        for day, hours in self.dealership_info["hours"].items():
            hours_text += f"• {day}: {hours}\n"
        
        self.sender.send_text(user_phone, hours_text)
        time.sleep(0.5)
        
        # Enviar ubicación
        self.sender.send_location(
            user_phone,
            self.dealership_info["latitude"],
            self.dealership_info["longitude"],
            self.dealership_info["name"],
            self.dealership_info["address"]
        )
        time.sleep(0.5)
        
        # Enviar contacto
        self.sender.send_contact(
            user_phone,
            "AutoMax Ventas",
            self.dealership_info["phone"],
            self.dealership_info["name"]
        )
    
    def _send_help_message(self, user_phone: str) -> Dict[str, Any]:
        """
        Envía mensaje de ayuda
        """
        help_text = """🆘 *Ayuda - AutoMax WhatsApp Bot*

📝 *Comandos disponibles:*
• /menu - Mostrar menú principal
• /ayuda - Mostrar esta ayuda
• /reiniciar - Reiniciar conversación

🚗 *Puedes preguntarme sobre:*
• Búsqueda de autos por marca, precio, tipo
• Información detallada de vehículos
• Agendamiento de citas y pruebas de manejo
• Opciones de financiamiento
• Horarios y ubicación del concesionario

💬 *Ejemplos de preguntas:*
• "Busco un auto económico"
• "¿Qué SUVs tienen disponibles?"
• "Quiero agendar una prueba de manejo"
• "¿Cuáles son sus horarios?"

¡Estoy aquí para ayudarte a encontrar el auto perfecto! 🚗✨"""
        
        self.sender.send_text(user_phone, help_text)
        return {"status": "help_sent"}
