import requests
import json
import time
from typing import List, Dict, Any, Optional

class WhatsAppSender:
    """
    Clase para enviar mensajes a WhatsApp Business API
    """
    
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una request a la API de WhatsApp
        """
        try:
            response = requests.post(
                url=self.base_url,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mensaje enviado: {result}")
                return result
            else:
                print(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}
                
        except Exception as e:
            print(f"❌ Excepción enviando mensaje: {str(e)}")
            return {"error": "Exception", "details": str(e)}
    
    def send_text(self, to: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto simple
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        print(f"📤 Enviando texto a {to}: {message}")
        return self._send_request(payload)
    
    def send_buttons(self, to: str, header_text: str, body_text: str, 
                     buttons: List[Dict[str, str]], footer_text: str = "AutoMax") -> Dict[str, Any]:
        """
        Envía mensaje con botones interactivos
        
        buttons formato: [{"id": "btn_1", "title": "Opción 1"}, ...]
        """
        
        # WhatsApp solo permite máximo 3 botones
        if len(buttons) > 3:
            buttons = buttons[:3]
            print("⚠️ Solo se pueden enviar máximo 3 botones, truncando lista")
        
        formatted_buttons = []
        for button in buttons:
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": button["id"],
                    "title": button["title"][:20]  # WhatsApp límite de 20 caracteres
                }
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }
        
        print(f"📤 Enviando botones a {to}: {len(buttons)} opciones")
        return self._send_request(payload)
    
    def send_list(self, to: str, header_text: str, body_text: str, 
                  button_text: str, sections: List[Dict[str, Any]], 
                  footer_text: str = "AutoMax") -> Dict[str, Any]:
        """
        Envía mensaje con lista de opciones
        
        sections formato: [{
            "title": "Sección 1",
            "rows": [
                {"id": "opt_1", "title": "Opción 1", "description": "Descripción"},
                ...
            ]
        }]
        """
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        print(f"📤 Enviando lista a {to}: {len(sections)} secciones")
        return self._send_request(payload)
    
    def send_image(self, to: str, image_url: str, caption: str = "") -> Dict[str, Any]:
        """
        Envía una imagen con caption opcional
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }
        
        print(f"📤 Enviando imagen a {to}: {image_url}")
        return self._send_request(payload)
    
    def send_location(self, to: str, latitude: float, longitude: float, 
                      name: str, address: str) -> Dict[str, Any]:
        """
        Envía ubicación del concesionario
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address
            }
        }
        
        print(f"📤 Enviando ubicación a {to}: {name}")
        return self._send_request(payload)
    
    def send_contact(self, to: str, contact_name: str, phone_number: str, 
                     organization: str = "AutoMax") -> Dict[str, Any]:
        """
        Envía información de contacto
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "contacts",
            "contacts": [{
                "name": {
                    "formatted_name": contact_name,
                    "first_name": contact_name.split()[0] if contact_name.split() else contact_name
                },
                "phones": [{
                    "phone": phone_number,
                    "type": "WORK"
                }],
                "org": {
                    "company": organization
                }
            }]
        }
        
        print(f"📤 Enviando contacto a {to}: {contact_name}")
        return self._send_request(payload)
    
    def send_typing_indicator(self, to: str) -> Dict[str, Any]:
        """
        Envía indicador de "escribiendo..." (marca como leído)
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "body": "..."
            }
        }
        
        # Nota: WhatsApp Business API no tiene typing indicator real,
        # esto es una simulación enviando puntos suspensivos
        print(f"⌨️ Simulando typing para {to}")
        return self._send_request(payload)
    
    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marca un mensaje como leído
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        print(f"👁️ Marcando como leído: {message_id}")
        return self._send_request(payload)

# Funciones de utilidad para crear botones y listas comunes

def create_car_type_buttons() -> List[Dict[str, str]]:
    """Botones para tipos de autos"""
    return [
        {"id": "car_type_economic", "title": "🏷️ Económico"},
        {"id": "car_type_family", "title": "👨‍👩‍👧‍👦 Familiar"},
        {"id": "car_type_luxury", "title": "💎 Lujo"}
    ]

def create_main_menu_buttons() -> List[Dict[str, str]]:
    """Botones del menú principal"""
    return [
        {"id": "search_cars", "title": "🚗 Buscar autos"},
        {"id": "schedule_appointment", "title": "📅 Agendar cita"},
        {"id": "contact_info", "title": "📞 Contacto"}
    ]

def create_appointment_buttons() -> List[Dict[str, str]]:
    """Botones para agendar citas"""
    return [
        {"id": "test_drive", "title": "🚗 Prueba de manejo"},
        {"id": "consultation", "title": "💬 Consulta"},
        {"id": "inspection", "title": "🔍 Inspección"}
    ]
