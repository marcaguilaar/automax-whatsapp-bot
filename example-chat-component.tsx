// Simple React component example for the chat interface
// File: src/app/components/CarDealershipChat.tsx

'use client';

import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function CarDealershipChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const sessionId = 'user-session-' + Date.now();

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          sessionId
        }),
      });

      const data = await response.json();

      if (data.response) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Error en la respuesta');
      }
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Lo siento, ha ocurrido un error. ¿Podrías intentar de nuevo?',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await fetch(`/api/chat-agent?sessionId=${sessionId}`, {
        method: 'DELETE',
      });
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="bg-blue-600 text-white p-4 rounded-t-lg">
          <h2 className="text-xl font-bold">🚗 Premier Auto Dealership</h2>
          <p className="text-blue-100">Asistente Virtual de Ventas</p>
        </div>

        {/* Chat Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500">
              <p>¡Hola! Soy tu asistente virtual del concesionario.</p>
              <p>Puedes preguntarme sobre nuestros vehículos, agendar citas, o consultar información general.</p>
              <div className="mt-4 text-sm">
                <p><strong>Ejemplos:</strong></p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>"Busco algo económico para ir al trabajo"</li>
                  <li>"¿Qué SUVs tienen disponibles?"</li>
                  <li>"Quiero agendar una prueba de manejo"</li>
                  <li>"¿A qué hora abren?"</li>
                </ul>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                <p className="text-sm">Escribiendo...</p>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Escribe tu mensaje..."
              className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              Enviar
            </button>
            <button
              onClick={clearChat}
              className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600"
            >
              Limpiar
            </button>
          </div>
        </div>

        {/* Cost Info */}
        <div className="bg-green-50 p-3 rounded-b-lg border-t">
          <p className="text-sm text-green-600">
            💰 <strong>Agente económico:</strong> Chat Completions API - 95% más barato que Realtime
          </p>
        </div>
      </div>
    </div>
  );
}
