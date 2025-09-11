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
        """Detect which specific vehicle the user wants - ENGLISH VERSION"""
        query_lower = query.lower()
        
        # Mapping of keywords to vehicle IDs
        vehicle_mapping = {
            # By specific model
            "x3": "BMW_X3_2023_BLU",
            "bmw x3": "BMW_X3_2023_BLU",
            "serie 3": "BMW_3_2023_BLU", 
            "series 3": "BMW_3_2023_BLU",
            "bmw serie 3": "BMW_3_2023_BLU",
            "bmw series 3": "BMW_3_2023_BLU",
            "c-class": "MERCEDES_C_2023_BLK",
            "c class": "MERCEDES_C_2023_BLK",
            "mercedes": "MERCEDES_C_2023_BLK",
            "mercedes-benz": "MERCEDES_C_2023_BLK",
            "a4": "AUDI_A4_2022_WHT",
            "audi": "AUDI_A4_2022_WHT",
            "audi a4": "AUDI_A4_2022_WHT",
            "león": "SEAT_LEON_2023_BLU",
            "leon": "SEAT_LEON_2023_BLU",
            "seat": "SEAT_LEON_2023_BLU",
            "seat leon": "SEAT_LEON_2023_BLU",
            "mustang": "FORD_MUSTANG_2023_RED",
            "ford": "FORD_MUSTANG_2023_RED",
            "ford mustang": "FORD_MUSTANG_2023_RED",
            
            # By special characteristics
            "cheapest": "SEAT_LEON_2023_BLU",
            "cheap": "SEAT_LEON_2023_BLU",
            "affordable": "SEAT_LEON_2023_BLU",
            "budget": "SEAT_LEON_2023_BLU",
            "most expensive": "FORD_MUSTANG_2023_RED",
            "expensive": "FORD_MUSTANG_2023_RED",
            "premium": "FORD_MUSTANG_2023_RED",
            "luxury": "MERCEDES_C_2023_BLK",
            
            # By color
            "blue": "BMW_X3_2023_BLU",
            "metallic blue": "BMW_X3_2023_BLU",
            "storm bay blue": "BMW_3_2023_BLU",
            "black": "MERCEDES_C_2023_BLK",
            "obsidian black": "MERCEDES_C_2023_BLK",
            "white": "AUDI_A4_2022_WHT",
            "glacier white": "AUDI_A4_2022_WHT",
            "red": "FORD_MUSTANG_2023_RED",
            "racing red": "FORD_MUSTANG_2023_RED",
            "desire blue": "SEAT_LEON_2023_BLU",
            
            # By type
            "suv": "BMW_X3_2023_BLU",
            "sedan": "MERCEDES_C_2023_BLK",
            "sports car": "FORD_MUSTANG_2023_RED",
            "sport": "FORD_MUSTANG_2023_RED",
            
            # By brand (default to most popular model)
            "bmw": "BMW_X3_2023_BLU"
        }
        
        # Search for matches
        for keyword, vehicle_id in vehicle_mapping.items():
            if keyword in query_lower:
                return vehicle_id
        
        # If no specific vehicle detected, return default
        return "BMW_X3_2023_BLU"

    def get_vehicle_details(self, vehicle_id: str) -> str:
        """Get complete information for a specific vehicle - ENGLISH VERSION"""
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
                "brand": "BMW", "model": "Serie 3", "year": 2023,
                "price": "€40,000", "color": "storm bay blue", "type": "sedan",
                "engine": "2.0L TwinPower Turbo 4-cylinder",
                "fuel": "Gasoline", "transmission": "Steptronic Automatic",
                "mileage": "0 km (new vehicle)", "power": "184 HP",
                "consumption": "6.9L/100km", "emissions": "158 g/km CO2",
                "drivetrain": "Rear-wheel drive",
                "features": [
                    "iDrive 7.0 system with touchscreen",
                    "Harman Kardon premium sound system",
                    "Sport seats with electric adjustment",
                    "BMW ConnectedDrive connectivity",
                    "Adaptive cruise control"
                ],
                "dimensions": "4.71m x 1.83m x 1.44m",
                "trunk_capacity": "480 liters",
                "warranty": "2-year factory warranty + 3-year BMW Service Inclusive",
                "image": "images/bmw_serie_3.webp"
            },
            "SEAT_LEON_2023_BLU": {
                "brand": "SEAT", "model": "León", "year": 2023,
                "price": "€25,000", "color": "Desire blue", "type": "hatchback",
                "engine": "1.5L TSI 4-cylinder",
                "fuel": "Gasoline", "transmission": "6-speed Manual",
                "mileage": "0 km (new vehicle)", "power": "130 HP",
                "consumption": "5.8L/100km", "emissions": "132 g/km CO2",
                "drivetrain": "Front-wheel drive",
                "features": [
                    "SEAT Connect with full connectivity",
                    "Full LED headlights standard",
                    "Wireless smartphone charger",
                    "Cruise control",
                    "8.25-inch infotainment system"
                ],
                "dimensions": "4.37m x 1.80m x 1.46m",
                "trunk_capacity": "380 liters",
                "warranty": "2-year factory warranty",
                "image": "images/seat_leon.webp"
            },
            "MERCEDES_C_2023_BLK": {
                "brand": "Mercedes-Benz", "model": "C-Class", "year": 2023,
                "price": "€42,000", "color": "obsidian black", "type": "sedan", 
                "engine": "1.5L Turbo 4-cylinder",
                "fuel": "Gasoline", "transmission": "9G-TRONIC Automatic",
                "mileage": "0 km (new vehicle)", "power": "170 HP",
                "consumption": "6.8L/100km", "emissions": "155 g/km CO2",
                "drivetrain": "Rear-wheel drive",
                "features": [
                    "MBUX with artificial intelligence",
                    "AMG sport seats",
                    "LED High Performance lights", 
                    "Burmester sound system",
                    "64-color ambient lighting"
                ],
                "dimensions": "4.75m x 1.82m x 1.44m",
                "trunk_capacity": "455 liters",
                "warranty": "2-year Mercedes-Benz warranty",
                "image": "images/mercedes_c_class.png"
            },
            "AUDI_A4_2022_WHT": {
                "brand": "Audi", "model": "A4", "year": 2022,
                "price": "€38,000", "color": "glacier white", "type": "sedan",
                "engine": "2.0L TFSI 4-cylinder",
                "fuel": "Gasoline", "transmission": "S tronic 7-speed",
                "mileage": "15,000 km", "power": "190 HP",
                "consumption": "6.5L/100km", "emissions": "148 g/km CO2",
                "drivetrain": "quattro all-wheel drive",
                "features": [
                    "Virtual Cockpit Plus",
                    "quattro all-wheel drive",
                    "Bang & Olufsen Premium Sound",
                    "MMI Navigation plus",
                    "Sport seats"
                ],
                "dimensions": "4.76m x 1.84m x 1.43m",
                "trunk_capacity": "460 liters",
                "warranty": "1 year remaining warranty",
                "image": "images/audi_a4.png"
            },
            "FORD_MUSTANG_2023_RED": {
                "brand": "Ford", "model": "Mustang", "year": 2023,
                "price": "€55,000", "color": "racing red", "type": "sports car",
                "engine": "5.0L V8",
                "fuel": "Gasoline", "transmission": "6-speed Manual",
                "mileage": "0 km (new vehicle)", "power": "450 HP",
                "consumption": "12.5L/100km", "emissions": "290 g/km CO2",
                "drivetrain": "Rear-wheel drive",
                "features": [
                    "SYNC 3 infotainment system",
                    "Track Apps performance data",
                    "Selectable drive modes",
                    "Performance Package",
                    "Recaro sport seats"
                ],
                "dimensions": "4.79m x 1.92m x 1.38m",
                "trunk_capacity": "382 liters",
                "warranty": "3-year Ford warranty",
                "image": "images/ford_mustang.png"
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
        """Get the path of the last vehicle image consulted"""
        return getattr(self, '_last_vehicle_image', None)
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
        
        # CRITICAL: Filter by fuel type first (electric, hybrid, gasoline)
        fuel_keywords = {
            "electric": "Electric",
            "hybrid": "Hybrid", 
            "gasoline": "Gasoline",
            "petrol": "Gasoline",
            "gas": "Gasoline"
        }
        
        for fuel_key, fuel_value in fuel_keywords.items():
            if fuel_key in query_lower:
                original_count = len(filtered_cars)
                filtered_cars = [car for car in filtered_cars if car["fuel"] == fuel_value]
                # If no cars match this fuel type, return specific message
                if len(filtered_cars) == 0:
                    if fuel_value == "Electric":
                        return "❌ Sorry, we currently don't have any electric vehicles in our inventory.\n\n🚗 Our current inventory consists of gasoline vehicles from premium brands like BMW, Mercedes-Benz, Audi, SEAT, and Ford.\n\n⚡ Would you like me to notify you when electric vehicles become available? Or would you like to see our efficient gasoline options?"
                    elif fuel_value == "Hybrid":
                        return "❌ Sorry, we currently don't have any hybrid vehicles in our inventory.\n\n🚗 Our current inventory consists of gasoline vehicles from premium brands like BMW, Mercedes-Benz, Audi, SEAT, and Ford.\n\n🌱 Would you like me to notify you when hybrid vehicles become available? Or would you like to see our fuel-efficient gasoline options?"
                break
        
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
        """Schedule in-person appointment at the dealership - ENGLISH VERSION"""
        return f"""📅 Perfect! I'd be happy to schedule an appointment for you.

To complete your reservation I need:
• Preferred day and time
• Type of vehicle you want to see
• Your name and contact phone

Available hours:
- Monday to Friday: 9:00 AM - 6:00 PM
- Saturday: 9:00 AM - 2:00 PM
- Sunday: Closed

What day works best for you? 🚗

📍 AutoMax Dealership
Address: Av. Principal 123, Madrid
Phone: +34 91 XXX XX XX"""
    
    def interpret_user_intent(self, user_message: str, messages: List[Dict[str, str]]) -> str:
        """
        Usa GPT para interpretar la intención del usuario y llamar la función apropiada
        """
        try:
            # Crear prompt para determinar la intención con contexto
            context_history = ""
            if len(messages) > 1:
                # Obtener últimos 3 intercambios de conversación para contexto
                recent_messages = messages[-6:] if len(messages) >= 6 else messages[:-1]
                for msg in recent_messages:
                    context_history += f"{msg['role']}: {msg['content'][:100]}...\n"
            
            intent_prompt = {
                "role": "system",
                "content": f"""You are an assistant specialized in determining user intent at a car dealership.

CONVERSATION CONTEXT:
{context_history}

Analyze the user's message and determine which of these 5 actions should be executed:

1. SEARCH_INVENTORY - General vehicle search (by brand, color, type, price, availability)
   Examples: "what cars do you have?", "blue cars", "available BMW", "something cheap"

2. VEHICLE_DETAILS - Specific and detailed information about ONE particular vehicle
   Examples: "more information about the BMW X3", "Serie 3 specifications", "complete details of the Mercedes"

3. SCHEDULE_APPOINTMENT - Schedule appointment to visit the dealership (NO test drives)
   Examples: "I want to make an appointment", "visit the dealership", "see the cars in person", "schedule a visit"
   ONLY use this for NEW appointment requests, NOT for providing appointment details

4. COMPANY_INFO - Information about AutoMax (hours, location, contact)
   Examples: "where are you located", "your hours", "AutoMax phone number"

5. GENERAL_CHAT - General conversation, greetings, or queries that don't require specific function
   Examples: "hello", "thanks", "how are you", questions about financing/test drives (which we don't offer)
   ALSO use for simple questions about price/specific features when context shows a specific car was recently discussed
   ALSO use for providing appointment details after appointment scheduling was already initiated (names, phones, times, etc.)

Respond ONLY with one of these options: SEARCH_INVENTORY, VEHICLE_DETAILS, SCHEDULE_APPOINTMENT, COMPANY_INFO, or GENERAL_CHAT

SPECIAL RULES:
- If user asks "What is the price?" or "How much?" or "What does it cost?" and context shows a specific car was just discussed, use GENERAL_CHAT
- If the user asks for specific information about a concrete model (like "more information about the BMW X3"), it's VEHICLE_DETAILS
- If they search for general options (like "what BMW do you have?"), it's SEARCH_INVENTORY
- If user provides appointment details (name, phone, time, date) after already asking for an appointment, use GENERAL_CHAT
- If context shows appointment scheduling was already initiated and user provides information, use GENERAL_CHAT
- SCHEDULE_APPOINTMENT is ONLY for initial requests, not for follow-up information"""
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
