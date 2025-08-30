#!/usr/bin/env python3
"""
Agente de Chat Python nativo para AutoMax Concesionario
"""

import os
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI

class CarDealershipChatAgent:
    """
    Agente de chat nativo en Python para el concesionario AutoMax
    """
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()  # Cargar variables de entorno desde .env
        
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            print(f"⚠️  Warning: Error inicializando OpenAI client: {e}")
            # Fallback para compatibilidad
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.client = None
        
        self.conversation_histories = {}  # Historial por usuario
        
        # Configuración del sistema
        self.system_message = {
            "role": "system",
            "content": """Eres un asistente virtual de AutoMax, un concesionario de automóviles premium. Tu trabajo es ayudar a los clientes a encontrar el vehículo perfecto para sus necesidades.

PERSONALIDAD:
- Profesional pero amigable
- Entusiasta sobre los automóviles
- Conocedor del producto
- Orientado al servicio al cliente

INFORMACIÓN DEL INVENTARIO:
- Tenemos vehículos nuevos y usados
- Marcas disponibles: BMW, Mercedes-Benz, Audi, Volkswagen, SEAT, Ford
- Tipos: sedanes, SUVs, hatchbacks, deportivos
- Rangos de precio: desde €15,000 hasta €80,000
- Financiamiento disponible

SERVICIOS:
- Venta de vehículos nuevos y usados
- Financiamiento y leasing
- Intercambio de vehículos (trade-in)
- Servicio postventa y mantenimiento
- Pruebas de manejo programadas

FUNCIONES DISPONIBLES:
1. Búsqueda de inventario por tipo, marca, precio, color
2. Programar citas para pruebas de manejo
3. Información sobre financiamiento
4. Detalles específicos de vehículos

INSTRUCCIONES:
- Siempre saluda calurosamente
- Haz preguntas para entender las necesidades del cliente
- Recomienda vehículos específicos cuando sea apropiado
- Ofrece programar citas para pruebas de manejo
- Mantén un tono profesional pero personal
- Usa emojis apropiados (🚗, 🔧, 📅, etc.)

Responde siempre en español y sé específico sobre nuestros servicios."""
        }
    
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
        
        # Limitar historial a 20 mensajes
        if len(self.conversation_histories[user_id]) > 20:
            # Mantener el mensaje del sistema y los últimos 19 mensajes
            self.conversation_histories[user_id] = self.conversation_histories[user_id][-19:]
    
    def search_inventory(self, query: str) -> str:
        """Simula búsqueda en inventario"""
        query_lower = query.lower()
        
        # Inventario simulado
        cars = [
            {"marca": "BMW", "modelo": "X3", "año": 2023, "precio": "€45,000", "color": "azul", "tipo": "SUV"},
            {"marca": "Mercedes-Benz", "modelo": "C-Class", "año": 2023, "precio": "€42,000", "color": "negro", "tipo": "sedán"},
            {"marca": "Audi", "modelo": "A4", "año": 2022, "precio": "€38,000", "color": "blanco", "tipo": "sedán"},
            {"marca": "BMW", "modelo": "Serie 3", "año": 2023, "precio": "€40,000", "color": "azul", "tipo": "sedán"},
            {"marca": "Volkswagen", "modelo": "Tiguan", "año": 2022, "precio": "€32,000", "color": "rojo", "tipo": "SUV"},
            {"marca": "SEAT", "modelo": "León", "año": 2023, "precio": "€25,000", "color": "azul", "tipo": "hatchback"},
            {"marca": "Ford", "modelo": "Mustang", "año": 2023, "precio": "€55,000", "color": "rojo", "tipo": "deportivo"},
        ]
        
        # Filtrar por color si se menciona
        if "azul" in query_lower:
            cars = [car for car in cars if car["color"] == "azul"]
        elif "rojo" in query_lower:
            cars = [car for car in cars if car["color"] == "rojo"]
        elif "negro" in query_lower:
            cars = [car for car in cars if car["color"] == "negro"]
        elif "blanco" in query_lower:
            cars = [car for car in cars if car["color"] == "blanco"]
        
        # Filtrar por tipo
        if "suv" in query_lower:
            cars = [car for car in cars if car["tipo"] == "SUV"]
        elif "sedan" in query_lower or "sedán" in query_lower:
            cars = [car for car in cars if car["tipo"] == "sedán"]
        elif "deportivo" in query_lower:
            cars = [car for car in cars if car["tipo"] == "deportivo"]
        
        # Filtrar por marca
        if "bmw" in query_lower:
            cars = [car for car in cars if car["marca"] == "BMW"]
        elif "mercedes" in query_lower:
            cars = [car for car in cars if car["marca"] == "Mercedes-Benz"]
        elif "audi" in query_lower:
            cars = [car for car in cars if car["marca"] == "Audi"]
        
        if cars:
            result = "🚗 Vehículos encontrados:\n\n"
            for car in cars[:3]:  # Mostrar máximo 3
                result += f"• {car['marca']} {car['modelo']} ({car['año']})\n"
                result += f"  Color: {car['color']} | Tipo: {car['tipo']}\n"
                result += f"  Precio: {car['precio']}\n\n"
            
            if len(cars) > 3:
                result += f"... y {len(cars) - 3} vehículos más disponibles.\n\n"
                
            result += "¿Te interesa alguno? ¿Quieres que programemos una prueba de manejo? 📅"
            return result
        else:
            return "No encontré vehículos exactos con esas características, pero tengo otras opciones que podrían interesarte. ¿Quieres que te muestre nuestro inventario completo?"
    
    def schedule_appointment(self, details: str) -> str:
        """Simula programación de cita"""
        return f"""📅 ¡Perfecto! Me encanta programar una cita para ti.

Para completar tu reserva necesito:
• Día y hora preferida
• Tipo de vehículo que quieres probar
• Tu nombre y teléfono de contacto

Horarios disponibles:
- Lunes a Viernes: 9:00 - 18:00
- Sábados: 9:00 - 14:00

¿Qué día te viene mejor? 🚗"""
    
    def get_response(self, user_message: str, user_id: str = "default") -> str:
        """
        Genera una respuesta del agente de chat
        """
        try:
            # Añadir mensaje del usuario al historial
            self.add_to_history(user_id, "user", user_message)
            
            # Preparar mensajes para OpenAI
            messages = [self.system_message]
            
            # Añadir historial de conversación
            history = self.get_conversation_history(user_id)
            messages.extend(history)
            
            # Verificar si necesita búsqueda de inventario
            message_lower = user_message.lower()
            search_keywords = ["coche", "auto", "vehículo", "disponible", "inventario", "busco", "color", "azul", "rojo", "suv", "sedán", "bmw", "mercedes", "audi"]
            
            if any(keyword in message_lower for keyword in search_keywords):
                inventory_result = self.search_inventory(user_message)
                context_message = f"Basándote en esta búsqueda de inventario: {inventory_result}"
                messages.append({"role": "system", "content": context_message})
            
            # Verificar si quiere programar cita
            appointment_keywords = ["cita", "prueba", "probar", "conducir", "visitar", "ver"]
            if any(keyword in message_lower for keyword in appointment_keywords):
                appointment_info = self.schedule_appointment(user_message)
                context_message = f"Información para programar cita: {appointment_info}"
                messages.append({"role": "system", "content": context_message})
            
            # Llamar a OpenAI
            try:
                if self.client:
                    # Usar nuevo cliente
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    assistant_response = response.choices[0].message.content.strip()
                else:
                    # Usar API antigua para compatibilidad
                    import openai
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    assistant_response = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"❌ Error en llamada OpenAI: {e}")
                # Respuesta de fallback inteligente
                if any(keyword in message_lower for keyword in ["azul", "coche", "auto"]):
                    assistant_response = "🚗 ¡Excelente elección! Tenemos varios vehículos azules disponibles:\n\n• BMW Serie 3 (2023) - Color azul, €40,000\n• SEAT León (2023) - Color azul, €25,000\n\n¿Te interesa conocer más detalles de alguno? ¿Quieres programar una prueba de manejo? 📅"
                else:
                    assistant_response = "¡Hola! 👋 Bienvenido a AutoMax, tu concesionario de confianza. 🚗 Estoy aquí para ayudarte a encontrar el auto perfecto. ¿En qué puedo ayudarte hoy?"
            
            # Añadir respuesta al historial
            self.add_to_history(user_id, "assistant", assistant_response)
            
            return assistant_response
            
        except Exception as e:
            print(f"❌ Error en get_response: {e}")
            return "Lo siento, hubo un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?"

    def process_message(self, user_message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Procesa un mensaje y devuelve respuesta estructurada
        """
        try:
            response = self.get_response(user_message, user_id)
            
            return {
                "success": True,
                "response": response,
                "type": "text"
            }
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
            return {
                "success": False,
                "response": "Lo siento, hubo un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?",
                "type": "text",
                "error": str(e)
            }

# Función de compatibilidad para mantener la interfaz existente
def process_whatsapp_message(message: str, user_id: str = "default") -> Dict[str, Any]:
    """Función de compatibilidad con el sistema existente"""
    agent = CarDealershipChatAgent()
    return agent.process_message(message, user_id)

if __name__ == "__main__":
    # Prueba del agente
    agent = CarDealershipChatAgent()
    
    while True:
        user_input = input("\n💬 Tú: ")
        if user_input.lower() in ['quit', 'exit', 'salir']:
            break
            
        response = agent.get_response(user_input, "test_user")
        print(f"🤖 AutoMax: {response}")
