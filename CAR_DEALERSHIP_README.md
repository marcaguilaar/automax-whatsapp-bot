# 🚗 Car Dealership AI Agent

Sistema de agente inteligente para concesionario de automóviles basado en la arquitectura de OpenAI Realtime Agents.

## 📋 Descripción

Un agente conversacional que ayuda a los clientes del concesionario "Premier Auto Dealership" con:

- **Búsqueda de inventario** inteligente basada en necesidades del cliente
- **Información detallada** de vehículos específicos
- **Agendamiento de citas** para pruebas de manejo y consultas
- **Opciones de financiamiento** personalizadas
- **Información general** del concesionario

## 🧠 Características Principales

### Interpretación Natural del Lenguaje
- **NO utiliza palabras clave hardcodeadas**
- Interpreta intenciones del cliente de forma contextual
- Entiende consultas naturales como:
  - "Busco algo económico para ir al trabajo"
  - "Necesito un SUV familiar y seguro"
  - "¿Tienen algo en color azul por menos de 30.000?"

### Búsqueda Inteligente
- Filtros flexibles por múltiples criterios
- Recomendaciones basadas en uso previsto
- Priorización automática según necesidades expresadas

### Gestión de Citas Sin Formularios
- Solo pide información esencial (nombre y teléfono)
- Proceso conversacional natural
- Verificación automática de disponibilidad

## 🛠️ Herramientas Disponibles

### `searchInventory`
Busca vehículos por criterios flexibles:
- Marca, modelo, año, precio
- Tipo de combustible, carrocería
- Uso previsto ("trabajo", "familia", "lujo")
- Prioridades del cliente

### `getCarDetails`
Información completa de un vehículo específico:
- Especificaciones técnicas
- Características y equipamiento
- Precios y ubicación en el lote

### `scheduleAppointment`
Agenda citas para:
- Pruebas de manejo
- Consultas generales
- Inspecciones
- Entregas

### `getFinancingOptions`
Opciones de financiamiento:
- Préstamos tradicionales
- Leasing
- Programas para compradores primerizos
- Cálculos de pagos mensuales

### `getBusinessInfo`
Información del concesionario:
- Horarios de atención
- Ubicación y contacto
- Servicios disponibles

## 📊 Inventario Actual

### Vehículos Disponibles:
1. **2024 BMW X5** - $65,000 (SUV de lujo)
2. **2023 Toyota Camry** - $28,500 (Sedán confiable)
3. **2024 Tesla Model 3** - $42,000 (Eléctrico)
4. **2023 Ford F-150** - $45,000 (Pickup)
5. **2024 Honda Civic** - $24,000 (Compacto deportivo)
6. **2023 Audi A4** - $38,000 (Sedán premium)

## 🏢 Información del Concesionario

**Premier Auto Dealership**
- 📍 123 Main Street, Cityville, ST 12345
- ☎️ (555) 123-4567
- 📧 info@premierauto.com

### Horarios:
- Lunes a Viernes: 9:00 AM - 8:00 PM
- Sábado: 9:00 AM - 6:00 PM
- Domingo: 12:00 PM - 5:00 PM

## 🚀 Instalación y Uso

### Requisitos
- Node.js 18.18.0 o superior
- OpenAI API Key

### Instalación
```bash
npm install
```

### Configuración
1. Crear archivo `.env.local`:
```bash
OPENAI_API_KEY=tu_api_key_aqui
```

2. El agente está configurado como escenario por defecto en `src/app/agentConfigs/index.ts`

### Ejecución
```bash
npm run dev
```

## 💬 Ejemplos de Conversación

### Búsqueda por Necesidades
```
Cliente: "Busco algo económico para ir al trabajo que no gaste mucha gasolina"
Agente: [Busca vehículos económicos con buena eficiencia de combustible]
       Sugiere: Honda Civic, Toyota Camry
```

### Consulta Específica
```
Cliente: "¿Qué BMW tienen disponibles?"
Agente: [Busca por marca BMW]
       Muestra: 2024 BMW X5 con detalles completos
```

### Agendar Cita
```
Cliente: "Me gustaría probar el Tesla mañana por la tarde"
Agente: [Verifica disponibilidad]
       "Tengo disponibles slots a las 2:00 PM, 3:00 PM y 4:00 PM. 
        ¿Cuál te conviene? Solo necesito tu nombre y teléfono para confirmar."
```

## 🔧 Arquitectura

```
src/app/agentConfigs/carDealership/
├── index.ts          # Agente principal
├── tools.ts          # Herramientas disponibles
└── sampleData.ts     # Datos de inventario y negocio
```

### Flujo de Procesamiento:
1. **Cliente envía mensaje** natural
2. **LLM interpreta intención** sin palabras clave
3. **Selecciona herramientas** apropiadas
4. **Ejecuta búsquedas/acciones** según necesidad
5. **Responde de forma conversacional**

## 🎯 Próximas Funcionalidades

### Fase 2: Información Avanzada
- [ ] Comparación entre vehículos
- [ ] Historial de mantenimiento
- [ ] Galería de imágenes

### Fase 3: Ventas Completas
- [ ] Generación de cotizaciones
- [ ] Procesamiento de facturas
- [ ] Gestión de trade-ins

### Fase 4: Integración Externa
- [ ] Sistema de inventario real
- [ ] Calendario de citas
- [ ] CRM integration

## 🧪 Testing

```bash
# Probar datos básicos
node test-data.js

# Verificar herramientas (cuando esté disponible)
npm test
```

## 📝 Notas de Desarrollo

- **Basado en OpenAI Realtime Agents**: Aprovecha la arquitectura robusta existente
- **Chat únicamente**: No incluye funcionalidad de voz
- **Datos simulados**: Para desarrollo y testing inicial
- **Escalable**: Fácil agregar nuevas herramientas y funcionalidades

---

**Desarrollado con ❤️ para una experiencia de concesionario moderna y natural**
