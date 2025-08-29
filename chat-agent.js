const OpenAI = require('openai');
const { 
  searchInventory, 
  getCarDetails, 
  getAvailableAppointmentSlots, 
  scheduleAppointment, 
  getBusinessInfo, 
  getFinancingOptions 
} = require('./tools-chat');

class CarDealershipChatAgent {
  constructor() {
    // Initialize OpenAI client
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });

    // Initialize with system message
    this.conversationHistory = [{
      role: 'system',
      content: `
Eres un asistente experto de ventas de un concesionario de automóviles llamado "AutoMax". Tu trabajo es ayudar a los clientes de manera natural y eficiente con:

1. CONSULTAS DE INVENTARIO: Buscar y recomendar vehículos basándose en sus necesidades
2. INFORMACIÓN DETALLADA: Proporcionar especificaciones completas de vehículos específicos
3. AGENDAR CITAS: Programar citas para pruebas de manejo, consultas o inspecciones
4. INFORMACIÓN DE FINANCIAMIENTO: Explicar opciones de financiamiento y calcular pagos
5. INFORMACIÓN GENERAL: Horarios, ubicación, servicios del concesionario

# INSTRUCCIONES CRÍTICAS:

## REGLA FUNDAMENTAL - NO ALUCINAR
- NUNCA inventes información que no esté en las herramientas disponibles
- SOLO responde con información que obtienes de las funciones del sistema
- Si no tienes información específica, di claramente "No tengo esa información disponible en nuestro sistema" 
- NO hagas suposiciones sobre precios, características, disponibilidad o especificaciones
- NUNCA uses conocimiento general sobre marcas, garantías, o mercado automotriz
- SIEMPRE usa las herramientas para obtener datos antes de responder sobre vehículos
- Si una herramienta no devuelve resultados, informa al cliente honestamente
- PROHIBIDO mencionar información "general" o "típica" de la industria
- SOLO habla de lo que específicamente tienes en tu inventario y servicios

## Interpretación Natural
- Interpreta las necesidades del cliente de forma natural, NO uses palabras clave hardcodeadas
- Analiza el contexto completo del mensaje para entender la intención
- Sé proactivo sugiriendo opciones relevantes SOLO basándose en datos reales obtenidos de las herramientas

## Recopilación de Información
- NUNCA pidas información innecesaria del cliente
- Solo solicita datos cuando sean absolutamente esenciales:
  - Para AGENDAR CITAS: nombre completo y teléfono (obligatorio), email (opcional)
  - Para CREAR FACTURA: información completa del cliente y vehículo seleccionado
- En todos los demás casos, trabaja con la información que el cliente proporciona voluntariamente

## Uso de Herramientas - OBLIGATORIO
- SIEMPRE utiliza las herramientas disponibles para obtener información
- NUNCA respondas sobre vehículos sin consultar primero el inventario
- NUNCA menciones características o precios sin verificarlos con las herramientas
- Combina múltiples herramientas cuando sea necesario para dar una respuesta completa
- Si una búsqueda no devuelve resultados, explica claramente que no hay vehículos que coincidan

## Límites Estrictos
- SOLO conoces la información que obtienes de las 6 herramientas disponibles
- NO tienes conocimiento sobre otros concesionarios, marcas no disponibles, o vehículos fuera del inventario
- NO inventes horarios, precios, promociones o características
- NUNCA menciones garantías, seguros, o condiciones que no estén en los datos del sistema
- NO uses frases como "generalmente", "típicamente", "usualmente", "normalmente"
- Si te preguntan algo fuera de tu alcance, di: "No tengo esa información en nuestro sistema. Te recomiendo contactar directamente al concesionario para más detalles"

## Tono y Estilo:
- Profesional pero amigable
- Directo y eficiente
- Honesto sobre limitaciones
- Enfocado en soluciones basadas en datos reales
- Evita ser demasiado formal o robótico

Recuerda: Tu credibilidad depende de ser preciso y honesto. Es mejor decir "no tengo esa información" que inventar datos incorrectos.
`
    }];
  }

  // Available tools for function calling
  get tools() {
    return [
      {
        type: 'function',
        function: {
          name: 'searchInventory',
          description: 'Search for cars in the dealership inventory based on various criteria. The LLM can flexibly interpret user needs and apply appropriate filters.',
          parameters: {
            type: 'object',
            properties: {
              brand: {
                type: 'string',
                description: 'Car brand (e.g., BMW, Toyota, Tesla, Ford, Honda, Audi)'
              },
              model: {
                type: 'string',
                description: 'Specific car model'
              },
              priceMin: {
                type: 'number',
                description: 'Minimum price range'
              },
              priceMax: {
                type: 'number',
                description: 'Maximum price range'
              },
              year: {
                type: 'number',
                description: 'Specific year or minimum year'
              },
              fuelType: {
                type: 'string',
                enum: ['gasoline', 'diesel', 'hybrid', 'electric'],
                description: 'Type of fuel/power source'
              },
              bodyStyle: {
                type: 'string',
                enum: ['sedan', 'suv', 'hatchback', 'coupe', 'wagon', 'pickup'],
                description: 'Vehicle body style'
              },
              transmission: {
                type: 'string',
                enum: ['manual', 'automatic'],
                description: 'Transmission type'
              },
              maxMileage: {
                type: 'number',
                description: 'Maximum acceptable mileage'
              },
              usage: {
                type: 'string',
                description: 'Intended use (e.g., "commuting", "family", "work", "luxury", "sport")'
              },
              budget: {
                type: 'string',
                description: 'Budget category (e.g., "economico", "mid-range", "luxury")'
              },
              priorities: {
                type: 'array',
                items: { type: 'string' },
                description: 'Customer priorities (e.g., "fuel efficiency", "reliability", "luxury", "performance")'
              }
            }
          }
        }
      },
      {
        type: 'function',
        function: {
          name: 'getCarDetails',
          description: 'Get detailed information about a specific car by ID',
          parameters: {
            type: 'object',
            properties: {
              carId: {
                type: 'string',
                description: 'The unique ID of the car'
              }
            },
            required: ['carId']
          }
        }
      },
      {
        type: 'function',
        function: {
          name: 'getAvailableAppointmentSlots',
          description: 'Get available appointment slots for a specific date and type',
          parameters: {
            type: 'object',
            properties: {
              date: {
                type: 'string',
                description: 'Preferred date in YYYY-MM-DD format'
              },
              appointmentType: {
                type: 'string',
                enum: ['test_drive', 'consultation', 'inspection', 'delivery'],
                description: 'Type of appointment needed'
              }
            }
          }
        }
      },
      {
        type: 'function',
        function: {
          name: 'scheduleAppointment',
          description: 'Schedule an appointment for the customer. Requires customer contact information.',
          parameters: {
            type: 'object',
            properties: {
              date: {
                type: 'string',
                description: 'Appointment date in YYYY-MM-DD format'
              },
              time: {
                type: 'string',
                description: 'Appointment time (e.g., "10:00 AM")'
              },
              appointmentType: {
                type: 'string',
                enum: ['test_drive', 'consultation', 'inspection', 'delivery'],
                description: 'Type of appointment'
              },
              customerName: {
                type: 'string',
                description: 'Customer full name'
              },
              customerPhone: {
                type: 'string',
                description: 'Customer phone number'
              },
              customerEmail: {
                type: 'string',
                description: 'Customer email address'
              },
              carId: {
                type: 'string',
                description: 'ID of the car if appointment is related to a specific vehicle'
              },
              notes: {
                type: 'string',
                description: 'Additional notes or special requests'
              }
            },
            required: ['date', 'time', 'appointmentType', 'customerName', 'customerPhone']
          }
        }
      },
      {
        type: 'function',
        function: {
          name: 'getBusinessInfo',
          description: 'Get general business information like hours, location, contact details, and services',
          parameters: {
            type: 'object',
            properties: {
              infoType: {
                type: 'string',
                enum: ['hours', 'location', 'contact', 'services', 'all'],
                description: 'Type of information requested'
              }
            }
          }
        }
      },
      {
        type: 'function',
        function: {
          name: 'getFinancingOptions',
          description: 'Get available financing and leasing options',
          parameters: {
            type: 'object',
            properties: {
              carPrice: {
                type: 'number',
                description: 'Price of the car to calculate monthly payments'
              },
              downPayment: {
                type: 'number',
                description: 'Down payment amount'
              },
              creditProfile: {
                type: 'string',
                enum: ['excellent', 'good', 'fair', 'limited'],
                description: 'Customer credit profile'
              }
            }
          }
        }
      }
    ];
  }

  // Handle tool calls
  async handleToolCall(toolCall) {
    const { name, arguments: args } = toolCall.function;
    const parsedArgs = JSON.parse(args);

    switch (name) {
      case 'searchInventory':
        return await searchInventory.execute(parsedArgs);
      case 'getCarDetails':
        return await getCarDetails.execute(parsedArgs);
      case 'getAvailableAppointmentSlots':
        return await getAvailableAppointmentSlots.execute(parsedArgs);
      case 'scheduleAppointment':
        return await scheduleAppointment.execute(parsedArgs);
      case 'getBusinessInfo':
        return await getBusinessInfo.execute(parsedArgs);
      case 'getFinancingOptions':
        return await getFinancingOptions.execute(parsedArgs);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  // Main chat method
  async chat(userMessage, externalHistory = null) {
    try {
      // Use external history if provided, otherwise use internal history
      const currentHistory = externalHistory || this.conversationHistory;
      
      // Add user message to history
      currentHistory.push({
        role: 'user',
        content: userMessage
      });

      // Limit history after adding user message (only if using internal history)
      if (!externalHistory) {
        this.limitHistory();
      }

      // Get completion from OpenAI
      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4o-mini', // Much cheaper than GPT-4
        messages: currentHistory,
        tools: this.tools,
        tool_choice: 'auto',
        temperature: 0.7,
        max_tokens: 1000
      });

      const response = completion.choices[0].message;

      // Handle tool calls if any
      if (response.tool_calls && response.tool_calls.length > 0) {
        // Add assistant message with tool calls
        currentHistory.push(response);

        // Execute each tool call
        for (const toolCall of response.tool_calls) {
          const toolResult = await this.handleToolCall(toolCall);
          
          // Add tool result to conversation
          currentHistory.push({
            role: 'tool',
            tool_call_id: toolCall.id,
            content: JSON.stringify(toolResult)
          });
        }

        // Get final response after tool execution
        const finalCompletion = await this.openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: currentHistory,
          temperature: 0.7,
          max_tokens: 1000
        });

        const finalResponse = finalCompletion.choices[0].message.content || '';
        
        // Add final response to history
        currentHistory.push({
          role: 'assistant',
          content: finalResponse
        });

        // Limit history after adding assistant response (only if using internal history)
        if (!externalHistory) {
          this.limitHistory();
        }

        return finalResponse;
      } else {
        // No tool calls, just return the response
        const assistantResponse = response.content || '';
        
        // Add response to history
        currentHistory.push({
          role: 'assistant',
          content: assistantResponse
        });

        // Limit history after adding assistant response (only if using internal history)
        if (!externalHistory) {
          this.limitHistory();
        }

        return assistantResponse;
      }
    } catch (error) {
      console.error('Error in chat:', error);
      return 'Lo siento, ha ocurrido un error. ¿Podrías intentar de nuevo?';
    }
  }

  // Limit conversation history to last 20 messages (plus system message)
  limitHistory() {
    const MAX_MESSAGES = 20; // 20 mensajes entre usuario y bot
    if (this.conversationHistory.length > MAX_MESSAGES + 1) { // +1 for system message
      // Keep system message (first) + last 20 messages
      const systemMessage = this.conversationHistory[0];
      const recentMessages = this.conversationHistory.slice(-MAX_MESSAGES);
      this.conversationHistory = [systemMessage, ...recentMessages];
    }
  }

  // Clear conversation history
  clearHistory() {
    this.conversationHistory = [this.conversationHistory[0]]; // Keep system message
  }

  // Get conversation history
  getHistory() {
    return [...this.conversationHistory];
  }
}

module.exports = { CarDealershipChatAgent };
