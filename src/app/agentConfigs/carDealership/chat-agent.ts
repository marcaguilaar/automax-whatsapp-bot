import OpenAI from 'openai';
import { 
  searchInventory, 
  getCarDetails, 
  getAvailableAppointmentSlots, 
  scheduleAppointment, 
  getBusinessInfo, 
  getFinancingOptions 
} from './tools-chat';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export class CarDealershipChatAgent {
  private conversationHistory: OpenAI.Chat.ChatCompletionMessageParam[] = [];
  
  constructor() {
    // Initialize with system message
    this.conversationHistory = [{
      role: 'system',
      content: `
Eres un asistente experto de ventas de un concesionario de automóviles llamado "Premier Auto Dealership". Tu trabajo es ayudar a los clientes de manera natural y eficiente con:

1. CONSULTAS DE INVENTARIO: Buscar y recomendar vehículos basándose en sus necesidades
2. INFORMACIÓN DETALLADA: Proporcionar especificaciones completas de vehículos específicos
3. AGENDAR CITAS: Programar citas para pruebas de manejo, consultas o inspecciones
4. INFORMACIÓN DE FINANCIAMIENTO: Explicar opciones de financiamiento y calcular pagos
5. INFORMACIÓN GENERAL: Horarios, ubicación, servicios del concesionario

# INSTRUCCIONES CLAVE:

## Interpretación Natural
- Interpreta las necesidades del cliente de forma natural, NO uses palabras clave hardcodeadas
- Analiza el contexto completo del mensaje para entender la intención
- Sé proactivo sugiriendo opciones relevantes basándose en lo que expresan

## Recopilación de Información
- NUNCA pidas información innecesaria del cliente
- Solo solicita datos cuando sean absolutamente esenciales:
  - Para AGENDAR CITAS: nombre completo y teléfono (obligatorio), email (opcional)
  - Para CREAR FACTURA: información completa del cliente y vehículo seleccionado
- En todos los demás casos, trabaja con la información que el cliente proporciona voluntariamente

## Uso de Herramientas
- Utiliza las herramientas disponibles de forma inteligente basándote en la intención del cliente
- Combina múltiples herramientas cuando sea necesario para dar una respuesta completa
- Siempre verifica disponibilidad antes de recomendar un vehículo específico

## Tono y Estilo:
- Profesional pero amigable
- Directo y eficiente
- Enfocado en soluciones
- Evita ser demasiado formal o robótico
- Haz preguntas de seguimiento relevantes para mejor entender sus necesidades

Recuerda: Tu objetivo es ayudar al cliente a encontrar el vehículo perfecto y facilitar el proceso de compra de manera natural y eficiente.
`
    }];
  }

  // Available tools for function calling
  private tools: OpenAI.Chat.ChatCompletionTool[] = [
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

  // Handle tool calls
  private async handleToolCall(toolCall: OpenAI.Chat.ChatCompletionMessageToolCall): Promise<any> {
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
  async chat(userMessage: string): Promise<string> {
    try {
      // Add user message to history
      this.conversationHistory.push({
        role: 'user',
        content: userMessage
      });

      // Limit history after adding user message
      this.limitHistory();

      // Get completion from OpenAI
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o-mini', // Much cheaper than GPT-4
        messages: this.conversationHistory,
        tools: this.tools,
        tool_choice: 'auto',
        temperature: 0.7,
        max_tokens: 1000
      });

      const response = completion.choices[0].message;

      // Handle tool calls if any
      if (response.tool_calls && response.tool_calls.length > 0) {
        // Add assistant message with tool calls
        this.conversationHistory.push(response);

        // Execute each tool call
        for (const toolCall of response.tool_calls) {
          const toolResult = await this.handleToolCall(toolCall);
          
          // Add tool result to conversation
          this.conversationHistory.push({
            role: 'tool',
            tool_call_id: toolCall.id,
            content: JSON.stringify(toolResult)
          });
        }

        // Get final response after tool execution
        const finalCompletion = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: this.conversationHistory,
          temperature: 0.7,
          max_tokens: 1000
        });

        const finalResponse = finalCompletion.choices[0].message.content || '';
        
        // Add final response to history
        this.conversationHistory.push({
          role: 'assistant',
          content: finalResponse
        });

        // Limit history after adding assistant response
        this.limitHistory();

        return finalResponse;
      } else {
        // No tool calls, just return the response
        const assistantResponse = response.content || '';
        
        // Add response to history
        this.conversationHistory.push({
          role: 'assistant',
          content: assistantResponse
        });

        // Limit history after adding assistant response
        this.limitHistory();

        return assistantResponse;
      }
    } catch (error) {
      console.error('Error in chat:', error);
      return 'Lo siento, ha ocurrido un error. ¿Podrías intentar de nuevo?';
    }
  }

  // Limit conversation history to last 20 messages (plus system message)
  private limitHistory(): void {
    const MAX_MESSAGES = 20; // 20 mensajes entre usuario y bot
    if (this.conversationHistory.length > MAX_MESSAGES + 1) { // +1 for system message
      // Keep system message (first) + last 20 messages
      const systemMessage = this.conversationHistory[0];
      const recentMessages = this.conversationHistory.slice(-MAX_MESSAGES);
      this.conversationHistory = [systemMessage, ...recentMessages];
    }
  }

  // Clear conversation history
  clearHistory(): void {
    this.conversationHistory = [this.conversationHistory[0]]; // Keep system message
  }

  // Get conversation history
  getHistory(): OpenAI.Chat.ChatCompletionMessageParam[] {
    return [...this.conversationHistory];
  }
}
