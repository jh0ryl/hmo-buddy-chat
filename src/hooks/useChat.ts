import { useState, useCallback } from 'react';
import { Message } from '@/types/chat';

// Configure your Python backend endpoint here
const API_ENDPOINT = 'http://localhost:8000/chat'; // Change this to your Python API URL

interface UseChatOptions {
  apiEndpoint?: string;
}

export const useChat = (options?: UseChatOptions) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const endpoint = options?.apiEndpoint || API_ENDPOINT;

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || data.message || 'No response received',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message as assistant response for demo purposes
      const errorResponse: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠️ Could not connect to the backend. Please ensure your Python server is running at ${endpoint}\n\nTo set up your Python backend, create a simple FastAPI server:\n\n\`\`\`python\nfrom fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom pydantic import BaseModel\n\napp = FastAPI()\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])\n\nclass ChatRequest(BaseModel):\n    message: str\n    history: list = []\n\n@app.post("/chat")\nasync def chat(request: ChatRequest):\n    # Add your LLM logic here\n    return {"response": "Hello from your HMO assistant!"}\n\`\`\``,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  }, [endpoint, messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
};
