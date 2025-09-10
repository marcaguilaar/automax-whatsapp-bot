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
        
        # Sistema de mensajes multiidioma con detección automática
        self.system_message = {
            "role": "system",
            "content": """You are a virtual assistant for AutoMax, a premium car dealership. Your job is to help customers with vehicle information and in-person appointments.

ALWAYS respond in ENGLISH ONLY. This is an English-only system.

AVAILABLE SERVICES:
1. Vehicle Consultation: Show available cars with detailed specifications
2. Detailed Vehicle Information: Complete details for each specific vehicle
3. In-Person Appointments: Schedule visits to the dealership (NOT test drives)
4. Company Information: Details about AutoMax dealership

INVENTORY INFORMATION:
- New and used vehicles available
- Brands: BMW, Mercedes-Benz, Audi, Volkswagen, SEAT, Ford
- Types: sedans, SUVs, hatchbacks, sports cars
- Price range: €15,000 to €80,000
- All vehicles come with warranty and after-sales service

COMPANY INFO - AutoMax:
- Premium car dealership established in 2010
- Located in Madrid, Spain
- Specializes in European luxury and reliable vehicles
- Expert sales team with 10+ years experience
- Full after-sales service and maintenance
- Customer satisfaction guarantee
- Operating hours: Mon-Fri 9:00-18:00, Sat 9:00-14:00

WHAT YOU CAN DO:
✅ Search vehicles by brand, type, color, price range
✅ Provide complete vehicle specifications and features
✅ Schedule in-person appointments to visit the dealership
✅ Share company information and services
✅ Answer questions about vehicle availability

WHAT YOU CANNOT DO:
❌ NO financing or budget calculations
❌ NO test drive scheduling (only in-person visits)
❌ NO price negotiations or quotes
❌ NO loan or payment plans

INSTRUCTIONS:
- Always greet warmly in the customer's language
- Focus on vehicle consultation and appointment scheduling
- Provide detailed, accurate vehicle information
- Be enthusiastic about our car selection
- Guide customers toward scheduling in-person visits
- Use emojis appropriately (🚗, �, 🏢, etc.)
- Keep responses focused on the 4 main services

LANGUAGE EXAMPLES:
- Spanish: "hola, tenéis BMW disponibles?" → Respond in Spanish
- English: "hello, do you have BMW cars?" → Respond in English

Always be helpful and guide customers to visit our dealership for personalized service."""
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
    
    def detect_user_language(self, user_message: str) -> str:
        """Detecta el idioma del mensaje del usuario usando GPT - Soporta múltiples idiomas"""
        try:
            if not self.client:
                # Fallback básico para idiomas principales
                spanish_words = ["hola", "tengo", "quiero", "necesito", "gracias", "coches", "vehículos"]
                french_words = ["bonjour", "salut", "voiture", "merci", "voudrais"]
                german_words = ["hallo", "guten", "auto", "danke", "möchte"]
                italian_words = ["ciao", "buongiorno", "auto", "grazie", "vorrei"]
                portuguese_words = ["olá", "oi", "carro", "obrigado", "quero"]
                
                message_lower = user_message.lower()
                if any(word in message_lower for word in spanish_words):
                    return "español"
                elif any(word in message_lower for word in french_words):
                    return "français"
                elif any(word in message_lower for word in german_words):
                    return "deutsch"
                elif any(word in message_lower for word in italian_words):
                    return "italiano"
                elif any(word in message_lower for word in portuguese_words):
                    return "português"
                return "english"
            
            detection_prompt = {
                "role": "system",
                "content": """Detect the language of the user message and respond with ONLY the language name in its native form.

Supported languages and how to respond:
- Spanish: respond "español"
- English: respond "english" 
- French: respond "français"
- German: respond "deutsch"
- Italian: respond "italiano"
- Portuguese: respond "português"
- Dutch: respond "nederlands"
- Russian: respond "русский"
- Chinese: respond "中文"
- Japanese: respond "日本語"
- Korean: respond "한국어"
- Arabic: respond "العربية"

Examples:
- "hola, tenéis coches azules?" -> español
- "hello, do you have blue cars?" -> english
- "bonjour, avez-vous des voitures?" -> français
- "hallo, haben Sie Autos?" -> deutsch
- "ciao, avete auto?" -> italiano
- "olá, têm carros?" -> português

If you cannot determine the language clearly, default to "english".
Respond with just the language name, nothing else."""
            }
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    detection_prompt,
                    {"role": "user", "content": user_message}
                ],
                max_tokens=15,
                temperature=0
            )
            
            detected_language = response.choices[0].message.content.strip().lower()
            
            # Lista de idiomas soportados
            supported_languages = [
                "español", "english", "français", "deutsch", "italiano", "português",
                "nederlands", "русский", "中文", "日本語", "한국어", "العربية"
            ]
            
            return detected_language if detected_language in supported_languages else "english"
            
        except Exception as e:
            print(f"Error detectando idioma: {e}")
            return "english"  # Fallback seguro
    
    def translate_response(self, response_text: str, target_language: str) -> str:
        """Traduce la respuesta al idioma objetivo usando GPT - Soporta múltiples idiomas"""
        try:
            if not self.client:
                return response_text  # Sin traducción si no hay cliente
                
            # Mapeo de nombres de idioma a códigos para verificación rápida
            language_indicators = {
                "español": ["hola", "vehículos", "cita", "información", "disponible"],
                "english": ["hello", "vehicles", "appointment", "information", "available"],
                "français": ["bonjour", "véhicules", "rendez-vous", "information", "disponible"],
                "deutsch": ["hallo", "fahrzeuge", "termin", "information", "verfügbar"],
                "italiano": ["ciao", "veicoli", "appuntamento", "informazioni", "disponibile"],
                "português": ["olá", "veículos", "consulta", "informação", "disponível"]
            }
            
            # Verificar si ya está en el idioma correcto (optimización)
            if target_language in language_indicators:
                response_lower = response_text.lower()
                if any(word in response_lower for word in language_indicators[target_language]):
                    return response_text  # Ya está en el idioma correcto
            
            # Configurar el prompt de traducción para múltiples idiomas
            language_names = {
                "español": "Spanish",
                "english": "English", 
                "français": "French",
                "deutsch": "German",
                "italiano": "Italian",
                "português": "Portuguese",
                "nederlands": "Dutch",
                "русский": "Russian",
                "中文": "Chinese (Simplified)",
                "日本語": "Japanese",
                "한국어": "Korean",
                "العربية": "Arabic"
            }
            
            target_lang_english = language_names.get(target_language, "English")
            
            translation_prompt = f"""Translate the following car dealership response to {target_lang_english} ({target_language}).

CRITICAL TRANSLATION RULES:
1. Maintain ALL emojis and formatting exactly as they appear
2. Preserve technical specifications and numbers exactly (€45,000, 184 CV, 2.0L, etc.)
3. Keep brand names unchanged (BMW, Mercedes-Benz, Audi, Ford, etc.)
4. Translate car-related terms appropriately for the automotive industry
5. Keep contact information as-is (phone numbers, emails, addresses)
6. Preserve line breaks, bullet points, and special characters
7. Return ONLY a JSON object with this exact format: {{"translated_response": "your translation here"}}

Text to translate:
{response_text}

Remember: Respond with ONLY the JSON object containing the translated text, no additional text or explanations."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": translation_prompt}],
                max_tokens=1200,  # Aumentado para idiomas que requieren más caracteres
                temperature=0.1   # Muy baja para traducciones consistentes
            )
            
            translation_result = response.choices[0].message.content.strip()
            
            # Intentar parsear el JSON con múltiples estrategias
            try:
                import json
                
                # Estrategia 1: JSON directo
                json_result = json.loads(translation_result)
                translated_text = json_result.get("translated_response", response_text)
                
            except json.JSONDecodeError:
                # Estrategia 2: Buscar JSON en el texto
                print(f"⚠️ Estrategia 2: Buscando JSON en texto para {target_language}")
                
                # Buscar el patrón {"translated_response": "..."}
                import re
                json_pattern = r'\{"translated_response":\s*"([^"]*(?:\\"[^"]*)*)"'
                match = re.search(json_pattern, translation_result)
                
                if match:
                    translated_text = match.group(1).replace('\\"', '"')
                else:
                    # Estrategia 3: Buscar contenido entre comillas después de translated_response
                    if '"translated_response":' in translation_result:
                        start = translation_result.find('"translated_response":') + len('"translated_response":')
                        start = translation_result.find('"', start) + 1
                        
                        # Buscar el final considerando comillas escapadas
                        end = start
                        while end < len(translation_result):
                            if translation_result[end] == '"' and translation_result[end-1] != '\\':
                                break
                            end += 1
                        
                        if end > start and (end - start) > 10:
                            translated_text = translation_result[start:end]
                        else:
                            print(f"❌ Estrategia 3 falló, usando original para {target_language}")
                            translated_text = response_text
                    else:
                        print(f"❌ No se encontró patrón JSON, usando original para {target_language}")
                        translated_text = response_text
            
            # Validación final de la traducción
            if len(translated_text) < 10:  # Muy corta, probablemente error
                print(f"⚠️ Traducción sospechosamente corta, usando original")
                return response_text
                
            return translated_text
            
        except Exception as e:
            print(f"❌ Error en traducción a {target_language}: {e}")
            return response_text  # Devolver original si hay error
    
    def detect_specific_vehicle(self, query: str) -> str:
        """Detecta qué vehículo específico quiere el usuario"""
        query_lower = query.lower()
        
        # Mapeo de palabras clave a IDs de vehículos
        vehicle_mapping = {
            # Por modelo específico
            "x3": "BMW_X3_2023_BLU",
            "bmw x3": "BMW_X3_2023_BLU",
            "serie 3": "BMW_3_2023_BLU", 
            "bmw serie 3": "BMW_3_2023_BLU",
            "c-class": "MERCEDES_C_2023_BLK",
            "mercedes": "MERCEDES_C_2023_BLK",
            "a4": "AUDI_A4_2022_WHT",
            "audi": "AUDI_A4_2022_WHT",
            "tiguan": "VW_TIGUAN_2022_RED",
            "volkswagen": "VW_TIGUAN_2022_RED",
            "león": "SEAT_LEON_2023_BLU",
            "leon": "SEAT_LEON_2023_BLU",
            "seat": "SEAT_LEON_2023_BLU",
            "mustang": "FORD_MUSTANG_2023_RED",
            "ford": "FORD_MUSTANG_2023_RED",
            
            # Por características especiales
            "más barato": "SEAT_LEON_2023_BLU",
            "mas barato": "SEAT_LEON_2023_BLU", 
            "barato": "SEAT_LEON_2023_BLU",
            "económico": "SEAT_LEON_2023_BLU",
            "cheapest": "SEAT_LEON_2023_BLU",
            
            "más caro": "FORD_MUSTANG_2023_RED",
            "mas caro": "FORD_MUSTANG_2023_RED",
            "caro": "FORD_MUSTANG_2023_RED", 
            "expensive": "FORD_MUSTANG_2023_RED",
            
            "deportivo": "FORD_MUSTANG_2023_RED",
            "sports": "FORD_MUSTANG_2023_RED",
            
            # Por color
            "azul": "BMW_X3_2023_BLU",  # Primer azul disponible
            "rojo": "VW_TIGUAN_2022_RED",  # Primer rojo disponible
            "negro": "MERCEDES_C_2023_BLK",
            "blanco": "AUDI_A4_2022_WHT"
        }
        
        # Buscar coincidencias en el query
        for keyword, vehicle_id in vehicle_mapping.items():
            if keyword in query_lower:
                return vehicle_id
        
        # Si no encuentra nada específico, devolver el más popular (BMW X3)
        return "BMW_X3_2023_BLU"

    def get_vehicle_details(self, vehicle_id: str) -> str:
        """Obtiene información completa de un vehículo específico"""
        cars = {
            "BMW_X3_2023_BLU": {
                "brand": "BMW", "model": "X3", "year": 2023, 
                "price": "€45,000", "color": "metallic blue", "type": "SUV",
                "engine": "2.0L TwinPower Turbo 4-cylinder",
                "fuel": "Gasoline", "transmission": "8-speed Steptronic Automatic",
                "mileage": "0 km (new vehicle)", "power": "184 HP (135 kW)",
                "consumption": "7.2L/100km (combined)", "emissions": "164 g/km CO2",
                "drivetrain": "xDrive All-Wheel Drive",
                "features": [
                    "BMW Live Cockpit Professional navigation system",
                    "Dakota leather heated seats",
                    "Front and rear parking sensors",
                    "3-zone automatic air conditioning",
                    "Adaptive LED headlights",
                    "Electric tailgate"
                ],
                "dimensions": "4.71m x 1.89m x 1.68m",
                "trunk_capacity": "550 liters",
                "warranty": "2-year factory warranty + 3-year BMW Service Inclusive",
                "image": "images/bmw_x3.png"
            },
            "BMW_3_2023_BLU": {
                "marca": "BMW", "modelo": "Serie 3", "año": 2023,
                "precio": "€40,000", "color": "azul storm bay", "tipo": "sedán",
                "motor": "2.0L TwinPower Turbo de 4 cilindros",
                "combustible": "Gasolina", "transmision": "Automática Steptronic",
                "km": "0 km (vehículo nuevo)", "potencia": "184 CV",
                "consumo": "6.9L/100km", "emisiones": "158 g/km CO2",
                "traccion": "Tracción trasera",
                "caracteristicas": [
                    "Sistema iDrive 7.0 con pantalla táctil",
                    "Harman Kardon sistema de sonido premium",
                    "Asientos deportivos con ajuste eléctrico",
                    "Conectividad BMW ConnectedDrive",
                    "Control de crucero adaptativo"
                ],
                "dimensiones": "4.71m x 1.83m x 1.44m",
                "capacidad_maletero": "480 litros",
                "garantia": "2 años garantía de fábrica + 3 años BMW Service Inclusive",
                "imagen": "images/bmw_serie_3.webp"
            },
            "SEAT_LEON_2023_BLU": {
                "marca": "SEAT", "modelo": "León", "año": 2023,
                "precio": "€25,000", "color": "azul Desire", "tipo": "hatchback",
                "motor": "1.5L TSI de 4 cilindros",
                "combustible": "Gasolina", "transmision": "Manual 6 velocidades",
                "km": "0 km (vehículo nuevo)", "potencia": "130 CV",
                "consumo": "5.8L/100km", "emisiones": "132 g/km CO2",
                "traccion": "Tracción delantera",
                "caracteristicas": [
                    "SEAT Connect con conectividad total",
                    "Faros Full LED de serie",
                    "Cargador inalámbrico para smartphone",
                    "Control de crucero",
                    "Sistema de infoentretenimiento de 8.25 pulgadas"
                ],
                "dimensiones": "4.37m x 1.80m x 1.46m",
                "capacidad_maletero": "380 litros",
                "garantia": "2 años garantía de fábrica",
                "imagen": "images/seat_leon.webp"
            },
            "MERCEDES_C_2023_BLK": {
                "marca": "Mercedes-Benz", "modelo": "C-Class", "año": 2023,
                "precio": "€42,000", "color": "negro obsidiana", "tipo": "sedán", 
                "motor": "1.5L Turbo de 4 cilindros",
                "combustible": "Gasolina", "transmision": "Automática 9G-TRONIC",
                "km": "0 km (vehículo nuevo)", "potencia": "170 CV",
                "consumo": "6.8L/100km", "emisiones": "155 g/km CO2",
                "traccion": "Tracción trasera",
                "caracteristicas": [
                    "MBUX con inteligencia artificial",
                    "Asientos deportivos AMG",
                    "LED High Performance", 
                    "Sistema de sonido Burmester",
                    "Ambient lighting 64 colores"
                ],
                "dimensiones": "4.75m x 1.82m x 1.44m",
                "capacidad_maletero": "455 litros",
                "garantia": "2 años garantía Mercedes-Benz",
                "imagen": "images/mercedes_c_class.png"
            },
            "AUDI_A4_2022_WHT": {
                "marca": "Audi", "modelo": "A4", "año": 2022,
                "precio": "€38,000", "color": "blanco glaciar", "tipo": "sedán",
                "motor": "2.0L TFSI de 4 cilindros",
                "combustible": "Gasolina", "transmision": "S tronic 7 velocidades",
                "km": "15,000 km", "potencia": "190 CV",
                "consumo": "6.5L/100km", "emisiones": "148 g/km CO2",
                "traccion": "quattro",
                "caracteristicas": [
                    "Virtual Cockpit Plus",
                    "quattro tracción integral",
                    "Bang & Olufsen Premium Sound",
                    "MMI Navigation plus",
                    "Asientos deportivos"
                ],
                "dimensiones": "4.76m x 1.84m x 1.43m",
                "capacidad_maletero": "460 litros",
                "garantia": "1 año garantía restante",
                "imagen": "images/audi_a4.png"
            },
            "VW_TIGUAN_2022_RED": {
                "marca": "Volkswagen", "modelo": "Tiguan", "año": 2022,
                "precio": "€32,000", "color": "rojo tornado", "tipo": "SUV",
                "motor": "1.5L TSI de 4 cilindros",
                "combustible": "Gasolina", "transmision": "DSG automático",
                "km": "22,000 km", "potencia": "150 CV",
                "consumo": "7.0L/100km", "emisiones": "160 g/km CO2",
                "traccion": "4MOTION",
                "caracteristicas": [
                    "Digital Cockpit Pro",
                    "4MOTION tracción integral",
                    "App-Connect",
                    "Park Assist",
                    "Climatronic"
                ],
                "dimensiones": "4.49m x 1.84m x 1.67m",
                "capacidad_maletero": "520 litros",
                "garantia": "1 año garantía restante",
                "imagen": "images/volkswagen_tiguan.webp"
            },
            "FORD_MUSTANG_2023_RED": {
                "marca": "Ford", "modelo": "Mustang", "año": 2023,
                "precio": "€55,000", "color": "rojo racing", "tipo": "deportivo",
                "motor": "5.0L V8",
                "combustible": "Gasolina", "transmision": "Manual 6 velocidades",
                "km": "0 km (vehículo nuevo)", "potencia": "450 CV",
                "consumo": "12.4L/100km", "emisiones": "290 g/km CO2",
                "traccion": "Tracción trasera",
                "caracteristicas": [
                    "SYNC 3 con pantalla táctil",
                    "Brembo frenos deportivos",
                    "Recaro asientos deportivos",
                    "Escape deportivo",
                    "Launch Control"
                ],
                "dimensiones": "4.79m x 1.92m x 1.38m",
                "capacidad_maletero": "408 litros",
                "garantia": "2 años garantía Ford",
                "imagen": "images/ford_mustang.jpeg"
            }
        }
        
        if vehicle_id in cars:
            car = cars[vehicle_id]
            
            # Formato visual mejorado sin asteriscos - EN INGLÉS
            result = f"🚗 {car['brand']} {car['model']} ({car['year']})\n"
            result += "═══════════════════════════════\n\n"
            
            # Información básica con diseño limpio
            result += f"💰 Price: {car['price']}\n"
            result += f"🎨 Color: {car['color']}\n"
            result += f"📊 Mileage: {car['mileage']}\n"
            result += f"🚙 Type: {car['type']}\n\n"
            
            # Especificaciones técnicas con emojis organizados
            result += "🔧 TECHNICAL SPECIFICATIONS\n"
            result += "───────────────────────────────\n"
            result += f"⚡ Engine: {car['engine']}\n"
            result += f"🏎️ Power: {car['power']}\n"
            result += f"⚙️ Transmission: {car['transmission']}\n"
            result += f"🚗 Drivetrain: {car['drivetrain']}\n"
            result += f"⛽ Consumption: {car['consumption']}\n"
            result += f"🌱 Emissions: {car['emissions']}\n\n"
            
            # Dimensiones con presentación clara
            result += "📏 DIMENSIONS\n"
            result += "───────────────────────────────\n"
            result += f"📐 Exterior: {car['dimensions']}\n"
            result += f"🧳 Trunk: {car['trunk_capacity']}\n\n"
            
            # Características con formato atractivo
            result += "✨ FEATURED CHARACTERISTICS\n"
            result += "───────────────────────────────\n"
            for i, feature in enumerate(car['features'], 1):
                result += f"🔹 {feature}\n"
            
            # Garantía con formato especial
            result += f"\n🛡️ WARRANTY\n"
            result += "───────────────────────────────\n"
            result += f"📋 {car['warranty']}\n\n"
            
            # Call to action final
            result += "🏢 Would you like to schedule an appointment to see it at our dealership?\n"
            result += "📞 We're ready to help you!"
            
            # Almacenar la ruta de la imagen para uso posterior
            self._last_vehicle_image = car.get("image")
            
            return result
        else:
            self._last_vehicle_image = None
            return "I couldn't find that specific vehicle. Can you tell me which model interests you? I have detailed information on all our vehicles."

    def get_last_vehicle_image(self) -> str:
        """Obtiene la ruta de la imagen del último vehículo consultado"""
        return getattr(self, '_last_vehicle_image', None)

    def schedule_appointment(self, details: str) -> str:
        """Programa cita presencial en el concesionario"""
        details_lower = details.lower()
        
        # Horarios disponibles
        horarios = [
            "Lunes a Viernes: 9:00 - 19:00",
            "Sábados: 9:00 - 14:00", 
            "Domingos: Cerrado"
        ]
        
        servicios_cita = [
            "Ver vehículos en persona",
            "Consulta personalizada con nuestros asesores",
            "Inspección detallada del vehículo",
            "Documentación y trámites"
        ]
        
        result = "📅 **Programar Cita Presencial**\n\n"
        result += "🏢 **AutoMax - Concesionario Premium**\n"
        result += "📍 Dirección: Av. Principal 123, Madrid\n\n"
        
        result += "🕐 **Horarios disponibles:**\n"
        for horario in horarios:
            result += f"• {horario}\n"
        
        result += "\n🎯 **¿Qué podemos hacer en tu cita?**\n"
        for servicio in servicios_cita:
            result += f"• {servicio}\n"
        
        result += "\n📞 **Para confirmar tu cita:**\n"
        result += "• Teléfono: +34 91 XXX XX XX\n"
        result += "• Email: citas@automax.es\n"
        result += "• WhatsApp: Este mismo número\n\n"
        
        result += "💡 **Información para tu cita:**\n"
        result += "• Trae tu DNI/NIE\n"
        result += "• Si tienes vehículo para tasación, trae documentación\n"
        result += "• Duración aproximada: 30-60 minutos\n\n"
        
        result += "¿Qué día y hora te conviene mejor? Nuestros asesores están listos para atenderte."
        
        return result

    def get_company_info(self, query: str = "") -> str:
        """Información de la empresa AutoMax"""
        query_lower = query.lower()
        
        if "direccion" in query_lower or "ubicacion" in query_lower:
            return ("📍 **AutoMax - Ubicación**\n\n"
                   "🏢 Dirección: Av. Principal 123, 28001 Madrid\n"
                   "🚇 Metro: Línea 1 - Estación Centro (5 min caminando)\n"
                   "🅿️ Aparcamiento gratuito disponible\n"
                   "🚗 Fácil acceso desde M-30 y A-1\n\n"
                   "¿Necesitas indicaciones específicas para llegar?")
        
        elif "horario" in query_lower or "hora" in query_lower:
            return ("🕐 **AutoMax - Horarios de Atención**\n\n"
                   "📅 Lunes a Viernes: 9:00 - 19:00\n"
                   "📅 Sábados: 9:00 - 14:00\n"
                   "📅 Domingos: Cerrado\n\n"
                   "🎯 Servicio al cliente siempre disponible vía WhatsApp\n"
                   "📞 Emergencias: +34 91 XXX XX XX")
        
        elif "contacto" in query_lower or "telefono" in query_lower:
            return ("📞 **AutoMax - Contacto**\n\n"
                   "📱 WhatsApp: Este mismo número\n"
                   "☎️ Teléfono: +34 91 XXX XX XX\n"
                   "📧 Email: info@automax.es\n"
                   "📧 Citas: citas@automax.es\n"
                   "🌐 Web: www.automax.es\n\n"
                   "💬 ¿Prefieres que te contactemos por algún medio específico?")
        
        else:
            return ("🏢 **AutoMax - Concesionario Premium**\n\n"
                   "🎯 **Especialistas en vehículos de calidad**\n"
                   "• Marcas premium: BMW, Mercedes-Benz, Audi, y más\n"
                   "• Vehículos nuevos y seminuevos\n"
                   "• Garantía en todos nuestros vehículos\n"
                   "• Servicio postventa especializado\n\n"
                   
                   "📍 **Ubicación:** Av. Principal 123, Madrid\n"
                   "🕐 **Horarios:** Lun-Vie 9-19h | Sáb 9-14h\n"
                   "📞 **Contacto:** +34 91 XXX XX XX\n\n"
                   
                   "✨ **¿Por qué elegir AutoMax?**\n"
                   "• +15 años de experiencia\n"
                   "• Asesoramiento personalizado\n"
                   "• Proceso transparente y honesto\n"
                   "• Atención al cliente excepcional\n\n"
                   
                   "¿Qué más te gustaría saber sobre nosotros?")

    def search_inventory(self, query: str) -> str:
        """Smart inventory search with detailed information - ENGLISH VERSION"""
        query_lower = query.lower()
        
        # Simplified inventory for English system
        cars = [
            {
                "id": "BMW_X3_2023_BLU", "brand": "BMW", "model": "X3", "year": 2023, 
                "price": "€45,000", "color": "metallic blue", "type": "SUV",
                "engine": "2.0L TwinPower Turbo", "fuel": "Gasoline", 
                "transmission": "8-speed Automatic", "mileage": "0 km (new)",
                "power": "184 HP", "consumption": "7.2L/100km", 
                "features": ["BMW Navigation", "Leather seats", "xDrive AWD"]
            },
            {
                "id": "BMW_3_2023_BLU", "brand": "BMW", "model": "Serie 3", "year": 2023,
                "price": "€40,000", "color": "storm bay blue", "type": "sedan",
                "engine": "2.0L TwinPower", "fuel": "Gasoline",
                "transmission": "Steptronic Automatic", "mileage": "0 km (new)",
                "power": "184 HP", "consumption": "6.9L/100km",
                "features": ["iDrive 7.0", "Harman Kardon", "Sport seats"]
            },
            {
                "id": "MERCEDES_C_2023_BLK", "brand": "Mercedes-Benz", "model": "C-Class", "year": 2023,
                "price": "€42,000", "color": "obsidian black", "type": "sedan", 
                "engine": "1.5L Turbo", "fuel": "Gasoline", 
                "transmission": "9G-TRONIC Automatic", "mileage": "0 km (new)",
                "power": "170 HP", "consumption": "6.8L/100km",
                "features": ["MBUX", "Sport seats", "LED High Performance"]
            },
            {
                "id": "AUDI_A4_2022_WHT", "brand": "Audi", "model": "A4", "year": 2022,
                "price": "€38,000", "color": "glacier white", "type": "sedan",
                "engine": "2.0L TFSI", "fuel": "Gasoline",
                "transmission": "S tronic 7-speed", "mileage": "15,000 km",
                "power": "190 HP", "consumption": "6.5L/100km", 
                "features": ["Virtual Cockpit", "quattro", "Bang & Olufsen"]
            },
            {
                "id": "SEAT_LEON_2023_BLU", "brand": "SEAT", "model": "León", "year": 2023,
                "price": "€25,000", "color": "Desire blue", "type": "hatchback",
                "engine": "1.5L TSI", "fuel": "Gasoline",
                "transmission": "6-speed Manual", "mileage": "0 km (new)",
                "power": "130 HP", "consumption": "5.8L/100km",
                "features": ["SEAT Connect", "Full LED", "Wireless Charger"]
            },
            {
                "id": "FORD_MUSTANG_2023_RED", "brand": "Ford", "model": "Mustang", "year": 2023,
                "price": "€55,000", "color": "racing red", "type": "sports car",
                "engine": "5.0L V8", "fuel": "Gasoline",
                "transmission": "6-speed Manual", "mileage": "0 km (new)",
                "power": "450 HP", "consumption": "12.4L/100km",
                "features": ["SYNC 3", "Brembo brakes", "Recaro seats"]
            }
        ]
        
        # Simple filtering for English system
        filtered_cars = cars.copy()
        
        # Filter by brand
        if any(brand in query_lower for brand in ["bmw", "mercedes", "audi", "seat", "ford"]):
            for brand in ["bmw", "mercedes", "audi", "seat", "ford"]:
                if brand in query_lower:
                    brand_map = {"bmw": "BMW", "mercedes": "Mercedes-Benz", "audi": "Audi", "seat": "SEAT", "ford": "Ford"}
                    filtered_cars = [car for car in filtered_cars if car["brand"] == brand_map[brand]]
                    break
        
        # Filter by color
        if any(color in query_lower for color in ["blue", "black", "white", "red"]):
            for color in ["blue", "black", "white", "red"]:
                if color in query_lower:
                    filtered_cars = [car for car in filtered_cars if color in car["color"].lower()]
                    break
        
        # Filter by type
        if any(vtype in query_lower for vtype in ["suv", "sedan", "sports", "hatchback"]):
            for vtype in ["suv", "sedan", "sports", "hatchback"]:
                if vtype in query_lower:
                    filtered_cars = [car for car in filtered_cars if vtype in car["type"].lower()]
                    break
        
        # Generate response
        if filtered_cars:
            result = "🚗 Available vehicles:\n\n"
            
            for i, car in enumerate(filtered_cars, 1):
                result += f"{i}. {car['brand']} {car['model']} ({car['year']})\n"
                result += f"   💰 Price: {car['price']}\n"
                result += f"   🎨 Color: {car['color']}\n"
                result += f"   ⚡ Engine: {car['engine']} - {car['power']}\n"
                result += f"   📊 Mileage: {car['mileage']}\n\n"
            
            total_vehicles = len(filtered_cars)
            if total_vehicles == 1:
                result += f"✅ This is the only vehicle that matches your search.\n\n"
            else:
                result += f"✅ Total: {total_vehicles} vehicles matching your search.\n\n"
            
            result += "💡 For complete information about any vehicle, ask me about the specific model.\n"
            result += "📅 Would you like to schedule an appointment to see them in person?"
            return result
        else:
            return "❌ Sorry, we currently don't have vehicles matching your search criteria.\n\n🚗 Our current inventory includes gasoline vehicles from brands like BMW, Mercedes-Benz, Audi, SEAT, and Ford.\n\nWould you like to see any of these available options? Or would you prefer that I notify you when we have vehicles that match your search?"
    
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
    
    def interpret_user_intent(self, user_message: str, messages: List[Dict[str, str]]) -> str:
        """
        Usa GPT para interpretar la intención del usuario y llamar la función apropiada
        """
        try:
            # Crear prompt para determinar la intención
            intent_prompt = {
                "role": "system",
                "content": """You are an assistant specialized in determining user intent at a car dealership.

Analyze the user's message and determine which of these 5 actions should be executed:

1. SEARCH_INVENTORY - General vehicle search (by brand, color, type, price, availability)
   Examples: "what cars do you have?", "blue cars", "available BMW", "something cheap"

2. VEHICLE_DETAILS - Specific and detailed information about ONE particular vehicle
   Examples: "more information about the BMW X3", "Serie 3 specifications", "complete details of the Mercedes"

3. SCHEDULE_APPOINTMENT - Schedule appointment to visit the dealership (NO test drives)
   Examples: "I want to make an appointment", "visit the dealership", "see the cars in person"

4. COMPANY_INFO - Information about AutoMax (hours, location, contact)
   Examples: "where are you located", "your hours", "AutoMax phone number"

5. GENERAL_CHAT - General conversation, greetings, or queries that don't require specific function
   Examples: "hello", "thanks", "how are you", questions about financing/test drives (which we don't offer)

Respond ONLY with one of these options: SEARCH_INVENTORY, VEHICLE_DETAILS, SCHEDULE_APPOINTMENT, COMPANY_INFO, or GENERAL_CHAT

If the user asks for specific information about a concrete model (like "more information about the BMW X3"), it's VEHICLE_DETAILS.
If they search for general options (like "what BMW do you have?"), it's SEARCH_INVENTORY."""
            }
            
            if self.client:
                # Determinar intención
                intent_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        intent_prompt,
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=20,
                    temperature=0
                )
                
                intent = intent_response.choices[0].message.content.strip()
                print(f"🎯 Intención detectada: {intent}")
                
                # Ejecutar la función apropiada basándose en la intención
                if intent == "SEARCH_INVENTORY":
                    self._last_vehicle_image = None  # Limpiar imagen anterior
                    return self.search_inventory(user_message)
                elif intent == "VEHICLE_DETAILS":
                    vehicle_id = self.detect_specific_vehicle(user_message)
                    return self.get_vehicle_details(vehicle_id)  # La imagen se almacena internamente
                elif intent == "SCHEDULE_APPOINTMENT":
                    self._last_vehicle_image = None  # Limpiar imagen anterior
                    return self.schedule_appointment(user_message)
                elif intent == "COMPANY_INFO":
                    self._last_vehicle_image = None  # Limpiar imagen anterior
                    return self.get_company_info(user_message)
                else:  # GENERAL_CHAT
                    self._last_vehicle_image = None  # Limpiar imagen anterior
                    # Usar conversación normal con GPT
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    return response.choices[0].message.content.strip()
            else:
                # Fallback sin cliente
                return "Hello! 👋 Welcome to AutoMax. How can I help you today?"
                
        except Exception as e:
            print(f"❌ Error interpretando intención: {e}")
            # Fallback a conversación general
            try:
                if self.client:
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    return response.choices[0].message.content.strip()
                else:
                    return "Hello! 👋 Welcome to AutoMax. How can I help you today?"
            except:
                return "Hello! 👋 Welcome to AutoMax. How can I help you today?"
    
    def get_response(self, user_message: str, user_id: str = "default") -> str:
        """
        Genera una respuesta del agente de chat en inglés únicamente
        """
        try:
            # Añadir mensaje del usuario al historial
            self.add_to_history(user_id, "user", user_message)
            
            # Preparar mensajes para OpenAI
            messages = [self.system_message]
            
            # Añadir historial de conversación
            history = self.get_conversation_history(user_id)
            messages.extend(history)
            
            # Usar GPT para determinar la intención del usuario e invocar la función apropiada
            response_text = self.interpret_user_intent(user_message, messages)
            
            # Añadir respuesta al historial
            self.add_to_history(user_id, "assistant", response_text)
            
            return response_text
            
        except Exception as e:
            print(f"❌ Error en get_response: {e}")
            return "Sorry, there was a problem processing your message. Could you please try again?"

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
