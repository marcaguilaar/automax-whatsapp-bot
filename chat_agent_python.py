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

IMPORTANT: ALWAYS respond in the SAME LANGUAGE the customer writes to you. Support multiple languages including:
- Spanish (español) - If they write in Spanish, respond in Spanish
- English - If they write in English, respond in English  
- French (français) - If they write in French, respond in French
- German (deutsch) - If they write in German, respond in German
- Italian (italiano) - If they write in Italian, respond in Italian
- Portuguese (português) - If they write in Portuguese, respond in Portuguese
- And other major languages as needed

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
    
    def get_vehicle_details(self, vehicle_id: str) -> str:
        """Obtiene información completa de un vehículo específico"""
        cars = {
            "BMW_X3_2023_BLU": {
                "marca": "BMW", "modelo": "X3", "año": 2023, 
                "precio": "€45,000", "color": "azul metalizado", "tipo": "SUV",
                "motor": "2.0L TwinPower Turbo de 4 cilindros",
                "combustible": "Gasolina", "transmision": "Automática Steptronic de 8 velocidades",
                "km": "0 km (vehículo nuevo)", "potencia": "184 CV (135 kW)",
                "consumo": "7.2L/100km (mixto)", "emisiones": "164 g/km CO2",
                "traccion": "Tracción total xDrive",
                "caracteristicas": [
                    "Sistema de navegación BMW Live Cockpit Professional",
                    "Asientos de cuero Dakota con calefacción",
                    "Sensor de aparcamiento delantero y trasero",
                    "Control automático de climatización de 3 zonas",
                    "Faros LED adaptativos",
                    "Portón trasero eléctrico"
                ],
                "dimensiones": "4.71m x 1.89m x 1.68m",
                "capacidad_maletero": "550 litros",
                "garantia": "2 años garantía de fábrica + 3 años BMW Service Inclusive"
            }
        }
        
        if vehicle_id in cars:
            car = cars[vehicle_id]
            
            # Formato visual mejorado sin asteriscos
            result = f"🚗 {car['marca']} {car['modelo']} ({car['año']})\n"
            result += "═══════════════════════════════\n\n"
            
            # Información básica con diseño limpio
            result += f"💰 Precio: {car['precio']}\n"
            result += f"🎨 Color: {car['color']}\n"
            result += f"📊 Kilometraje: {car['km']}\n"
            result += f"🚙 Tipo: {car['tipo']}\n\n"
            
            # Especificaciones técnicas con emojis organizados
            result += "🔧 ESPECIFICACIONES TÉCNICAS\n"
            result += "───────────────────────────────\n"
            result += f"⚡ Motor: {car['motor']}\n"
            result += f"🏎️ Potencia: {car['potencia']}\n"
            result += f"⚙️ Transmisión: {car['transmision']}\n"
            result += f"🚗 Tracción: {car['traccion']}\n"
            result += f"⛽ Consumo: {car['consumo']}\n"
            result += f"🌱 Emisiones: {car['emisiones']}\n\n"
            
            # Dimensiones con presentación clara
            result += "📏 DIMENSIONES\n"
            result += "───────────────────────────────\n"
            result += f"📐 Exterior: {car['dimensiones']}\n"
            result += f"🧳 Maletero: {car['capacidad_maletero']}\n\n"
            
            # Características con formato atractivo
            result += "✨ CARACTERÍSTICAS DESTACADAS\n"
            result += "───────────────────────────────\n"
            for i, feature in enumerate(car['caracteristicas'], 1):
                result += f"🔹 {feature}\n"
            
            # Garantía con formato especial
            result += f"\n🛡️ GARANTÍA\n"
            result += "───────────────────────────────\n"
            result += f"📋 {car['garantia']}\n\n"
            
            # Call to action final
            result += "🏢 ¿Te gustaría agendar una cita para verlo en nuestro concesionario?\n"
            result += "📞 ¡Estamos listos para atenderte!"
            
            return result
        else:
            return "No encontré ese vehículo específico. ¿Puedes decirme qué modelo te interesa? Tengo información detallada de todos nuestros vehículos."

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
        """Búsqueda inteligente en inventario con información detallada"""
        query_lower = query.lower()
        
        # Inventario detallado con especificaciones completas
        cars = [
            {
                "id": "BMW_X3_2023_BLU", "marca": "BMW", "modelo": "X3", "año": 2023, 
                "precio": "€45,000", "color": "azul metalizado", "tipo": "SUV",
                "motor": "2.0L TwinPower Turbo", "combustible": "Gasolina", 
                "transmision": "Automática 8 velocidades", "km": "0 km (nuevo)",
                "potencia": "184 CV", "consumo": "7.2L/100km", 
                "caracteristicas": ["Navegación BMW", "Asientos de cuero", "Tracción total xDrive"]
            },
            {
                "id": "MERCEDES_C_2023_BLK", "marca": "Mercedes-Benz", "modelo": "C-Class", "año": 2023,
                "precio": "€42,000", "color": "negro obsidiana", "tipo": "sedán", 
                "motor": "1.5L Turbo", "combustible": "Gasolina", 
                "transmision": "Automática 9G-TRONIC", "km": "0 km (nuevo)",
                "potencia": "170 CV", "consumo": "6.8L/100km",
                "caracteristicas": ["MBUX", "Asientos deportivos", "LED High Performance"]
            },
            {
                "id": "AUDI_A4_2022_WHT", "marca": "Audi", "modelo": "A4", "año": 2022,
                "precio": "€38,000", "color": "blanco glaciar", "tipo": "sedán",
                "motor": "2.0L TFSI", "combustible": "Gasolina",
                "transmision": "S tronic 7 velocidades", "km": "15,000 km",
                "potencia": "190 CV", "consumo": "6.5L/100km", 
                "caracteristicas": ["Virtual Cockpit", "quattro", "Bang & Olufsen"]
            },
            {
                "id": "BMW_3_2023_BLU", "marca": "BMW", "modelo": "Serie 3", "año": 2023,
                "precio": "€40,000", "color": "azul storm bay", "tipo": "sedán",
                "motor": "2.0L TwinPower", "combustible": "Gasolina",
                "transmision": "Automática Steptronic", "km": "0 km (nuevo)",
                "potencia": "184 CV", "consumo": "6.9L/100km",
                "caracteristicas": ["iDrive 7.0", "Harman Kardon", "Asientos deportivos"]
            },
            {
                "id": "VW_TIGUAN_2022_RED", "marca": "Volkswagen", "modelo": "Tiguan", "año": 2022,
                "precio": "€32,000", "color": "rojo tornado", "tipo": "SUV",
                "motor": "1.5L TSI", "combustible": "Gasolina",
                "transmision": "DSG automático", "km": "22,000 km",
                "potencia": "150 CV", "consumo": "7.0L/100km",
                "caracteristicas": ["Digital Cockpit", "4MOTION", "App-Connect"]
            },
            {
                "id": "SEAT_LEON_2023_BLU", "marca": "SEAT", "modelo": "León", "año": 2023,
                "precio": "€25,000", "color": "azul Desire", "tipo": "hatchback",
                "motor": "1.5L TSI", "combustible": "Gasolina",
                "transmision": "Manual 6 velocidades", "km": "0 km (nuevo)",
                "potencia": "130 CV", "consumo": "5.8L/100km",
                "caracteristicas": ["SEAT Connect", "Full LED", "Wireless Charger"]
            },
            {
                "id": "FORD_MUSTANG_2023_RED", "marca": "Ford", "modelo": "Mustang", "año": 2023,
                "precio": "€55,000", "color": "rojo racing", "tipo": "deportivo",
                "motor": "5.0L V8", "combustible": "Gasolina",
                "transmision": "Manual 6 velocidades", "km": "0 km (nuevo)",
                "potencia": "450 CV", "consumo": "12.4L/100km",
                "caracteristicas": ["SYNC 3", "Brembo", "Recaro asientos"]
            }
        ]
        
        # Filtros de búsqueda MEJORADOS Y ESPECÍFICOS
        filtered_cars = cars.copy()
        applied_filters = []  # Para rastrear qué filtros se aplicaron
        
        # Filtrar por COMBUSTIBLE (nuevo filtro crítico)
        combustible_keywords = {
            "eléctrico": "Eléctrico", "electrico": "Eléctrico", "electric": "Eléctrico",
            "híbrido": "Híbrido", "hibrido": "Híbrido", "hybrid": "Híbrido",
            "gasolina": "Gasolina", "gasoline": "Gasolina", "petrol": "Gasolina",
            "diesel": "Diesel", "diésel": "Diesel"
        }
        
        for fuel_key, fuel_value in combustible_keywords.items():
            if fuel_key in query_lower:
                original_count = len(filtered_cars)
                filtered_cars = [car for car in filtered_cars if car["combustible"] == fuel_value]
                applied_filters.append(f"combustible: {fuel_value}")
                if len(filtered_cars) != original_count:
                    break
        
        # Filtrar por color (mejorado)
        colors = {
            "azul": "azul", "blue": "azul", "bleu": "azul",
            "rojo": "rojo", "red": "rojo", "rouge": "rojo", 
            "negro": "negro", "black": "negro", "noir": "negro",
            "blanco": "blanco", "white": "blanco", "blanc": "blanco",
            "gris": "gris", "gray": "gris", "grey": "gris"
        }
        
        for color_key, color_value in colors.items():
            if color_key in query_lower:
                original_count = len(filtered_cars)
                filtered_cars = [car for car in filtered_cars if color_value in car["color"].lower()]
                if len(filtered_cars) != original_count:
                    applied_filters.append(f"color: {color_value}")
                    break
        
        # Filtrar por tipo (mejorado)
        types = {
            "suv": "SUV", "sedan": "sedán", "sedán": "sedán", 
            "deportivo": "deportivo", "sports": "deportivo", "sport": "deportivo",
            "hatchback": "hatchback", "compacto": "hatchback"
        }
        
        for type_key, type_value in types.items():
            if type_key in query_lower:
                original_count = len(filtered_cars)
                filtered_cars = [car for car in filtered_cars if car["tipo"] == type_value]
                if len(filtered_cars) != original_count:
                    applied_filters.append(f"tipo: {type_value}")
                    break
        
        # Filtrar por marca (mejorado)
        brands = {
            "bmw": "BMW", "mercedes": "Mercedes-Benz", "audi": "Audi", 
            "volkswagen": "Volkswagen", "vw": "Volkswagen", "seat": "SEAT", "ford": "Ford"
        }
        
        for brand_key, brand_value in brands.items():
            if brand_key in query_lower:
                original_count = len(filtered_cars)
                filtered_cars = [car for car in filtered_cars if car["marca"] == brand_value]
                if len(filtered_cars) != original_count:
                    applied_filters.append(f"marca: {brand_value}")
                    break
        
        # RESPUESTA INTELIGENTE BASADA EN RESULTADOS
        if filtered_cars:
            result = "🚗 Vehículos disponibles:\n\n"
            
            # Mostrar TODOS los vehículos filtrados
            for i, car in enumerate(filtered_cars, 1):
                result += f"{i}. {car['marca']} {car['modelo']} ({car['año']})\n"
                result += f"   💰 Precio: {car['precio']}\n"
                result += f"   🎨 Color: {car['color']}\n"
                result += f"   ⚡ Motor: {car['motor']} - {car['potencia']}\n"
                result += f"   📊 Kilometraje: {car['km']}\n\n"
            
            # Información del filtrado aplicado
            total_vehicles = len(filtered_cars)
            if total_vehicles == 1:
                result += f"✅ Este es el único vehículo que coincide con tu búsqueda.\n\n"
            else:
                result += f"✅ Total: {total_vehicles} vehículos que coinciden con tu búsqueda.\n\n"
            
            result += "💡 Para información completa de cualquier vehículo, pregúntame por el modelo específico.\n"
            result += "📅 ¿Te gustaría programar una cita para verlos en persona?"
            return result
            
        else:
            # RESPUESTA ESPECÍFICA CUANDO NO HAY RESULTADOS
            if applied_filters:
                # Sabemos exactamente qué filtros se aplicaron y no dieron resultados
                filter_text = ", ".join(applied_filters)
                return f"❌ Lo siento, actualmente no tenemos vehículos con las características que buscas ({filter_text}).\n\n🚗 Nuestro inventario actual incluye vehículos de gasolina de marcas como BMW, Mercedes-Benz, Audi, Volkswagen, SEAT y Ford.\n\n¿Te gustaría ver alguna de estas opciones disponibles? ¿O prefieres que te notifique cuando tengamos vehículos que coincidan con tu búsqueda?"
            else:
                # Búsqueda general sin filtros específicos detectados
                return "No encontré vehículos con esas características específicas, pero tengo otras opciones excelentes. ¿Quieres ver todo nuestro inventario disponible?"
    
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
        Genera una respuesta del agente de chat con traducción automática
        """
        try:
            # Detectar idioma del usuario
            user_language = self.detect_user_language(user_message)
            
            # Añadir mensaje del usuario al historial
            self.add_to_history(user_id, "user", user_message)
            
            # Preparar mensajes para OpenAI
            messages = [self.system_message]
            
            # Añadir historial de conversación
            history = self.get_conversation_history(user_id)
            messages.extend(history)
            
            # Verificar funciones específicas (respuesta directa sin llamar a OpenAI)
            message_lower = user_message.lower()
            response_text = None
            
            # Función específica: Búsqueda de inventario
            search_keywords = [
                "coche", "auto", "vehículo", "disponible", "inventario", "busco", "color", 
                "azul", "rojo", "suv", "sedán", "bmw", "mercedes", "audi", "teneis", "hay",
                "car", "vehicle", "available", "inventory", "looking", "search", "color",
                "blue", "red", "sedan", "do you have", "show me"
            ]
            
            if any(keyword in message_lower for keyword in search_keywords):
                response_text = self.search_inventory(user_message)
            
            # Función específica: Detalles de vehículo
            elif any(keyword in message_lower for keyword in [
                "detalles", "especificaciones", "información completa", "características",
                "motor", "potencia", "consumo", "dimensiones", "garantía", "completa",
                "details", "specifications", "complete information", "features",
                "engine", "power", "consumption", "dimensions", "warranty", "complete"
            ]):
                response_text = self.get_vehicle_details("BMW_X3_2023_BLU")
            
            # Función específica: Programar cita presencial (NO pruebas de manejo)
            elif any(keyword in message_lower for keyword in [
                "cita", "visita", "ver", "programar", "concesionario", "presencial", "agendar",
                "appointment", "visit", "see", "schedule", "dealership", "in-person", "book"
            ]):
                # Excluir pruebas de manejo
                if not any(test_word in message_lower for test_word in ["prueba", "probar", "conducir", "test", "drive", "driving"]):
                    response_text = self.schedule_appointment(user_message)
            
            # Función específica: Información de empresa
            elif any(keyword in message_lower for keyword in [
                "empresa", "automax", "dirección", "ubicación", "horario", "contacto", "teléfono",
                "company", "automax", "address", "location", "hours", "contact", "phone"
            ]):
                response_text = self.get_company_info(user_message)
            
            # Si no es función específica, usar IA
            if response_text is None:
                try:
                    if self.client:
                        # Usar nuevo cliente
                        response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                        response_text = response.choices[0].message.content.strip()
                    else:
                        # Usar API antigua para compatibilidad
                        import openai
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                        response_text = response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"❌ Error en llamada OpenAI: {e}")
                    # Respuesta de fallback básica
                    response_text = "¡Hola! 👋 Bienvenido a AutoMax, tu concesionario de confianza. 🚗 Estoy aquí para ayudarte a encontrar el auto perfecto. ¿En qué puedo ayudarte hoy?"
            
            # TRADUCIR AUTOMÁTICAMENTE LA RESPUESTA AL IDIOMA DEL USUARIO
            final_response = self.translate_response(response_text, user_language)
            
            # Añadir respuesta al historial
            self.add_to_history(user_id, "assistant", final_response)
            
            return final_response
            
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
