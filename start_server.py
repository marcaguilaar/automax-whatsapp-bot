#!/usr/bin/env python3
"""
Script de inicio para el servidor WhatsApp en producción
"""

import os
import sys
from whatsapp_main import app

if __name__ == "__main__":
    # Obtener el puerto de las variables de entorno (Render usa PORT)
    port = int(os.environ.get("PORT", 8080))
    
    print(f"🚀 Iniciando servidor WhatsApp en puerto {port}")
    
    # En producción, usar 0.0.0.0 para que sea accesible externamente
    app.run(host="0.0.0.0", port=port, debug=False)
