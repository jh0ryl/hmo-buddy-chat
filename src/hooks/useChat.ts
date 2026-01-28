import { useState, useCallback } from 'react';
import { Message } from '@/types/chat';

// Configure your Python backend endpoint here
const API_ENDPOINT = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/chat`
  : 'http://localhost:8000/api/chat';

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
          use_context: true, // Enable RAG
          stream: false,
          conversation_history: messages.map((m) => ({
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

      // Add error message as assistant response
      const errorResponse: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `⚠️ Could not connect to the backend at ${endpoint}\n\nPlease ensure:\n1. Your Python backend is running: \`cd backend && start_backend.bat\`\n2. Ollama is running with models: \`ollama list\`\n3. Backend is accessible at: http://localhost:8000\n\nCheck backend/README.md for full setup instructions.`,
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
