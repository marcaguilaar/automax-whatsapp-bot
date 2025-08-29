// API Route for the Chat Agent
// File: src/app/api/chat-agent/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { CarDealershipChatAgent } from '../../agentConfigs/carDealership/chat-agent';

// Store agent instances per session (in production, use Redis or similar)
const agentSessions = new Map<string, CarDealershipChatAgent>();

export async function POST(request: NextRequest) {
  try {
    const { message, sessionId = 'default' } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Get or create agent for this session
    let agent = agentSessions.get(sessionId);
    if (!agent) {
      agent = new CarDealershipChatAgent();
      agentSessions.set(sessionId, agent);
    }

    // Get response from agent
    const response = await agent.chat(message);

    return NextResponse.json({
      response,
      sessionId,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error in chat agent:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Clear session
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('sessionId') || 'default';

    const agent = agentSessions.get(sessionId);
    if (agent) {
      agent.clearHistory();
      agentSessions.delete(sessionId);
    }

    return NextResponse.json({ message: 'Session cleared' });

  } catch (error) {
    console.error('Error clearing session:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
