/**
 * Ollama Backend API Service
 * Handles communication with the local FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  message: string;
  use_context?: boolean;
  stream?: boolean;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  sources?: Array<{
    source: string;
    similarity: number;
  }>;
}

export interface HealthResponse {
  status: string;
  llm_model: string;
  embedding_model: string;
  documents_count: number;
  ollama_available: boolean;
}

export interface DocumentInfo {
  source: string;
  chunks: number;
  ids: string[];
}

export interface DocumentsResponse {
  documents: DocumentInfo[];
  count: number;
}

/**
 * Check backend health and Ollama availability
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('Failed to check health');
  }
  return response.json();
}

/**
 * Send a chat message (non-streaming)
 */
export async function sendChatMessage(
  message: string,
  useContext: boolean = true,
  conversationHistory?: ChatMessage[]
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      use_context: useContext,
      stream: false,
      conversation_history: conversationHistory,
    } as ChatRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

/**
 * Send a chat message with streaming response
 */
export async function sendChatMessageStream(
  message: string,
  useContext: boolean = true,
  conversationHistory?: ChatMessage[],
  onChunk: (chunk: string) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      use_context: useContext,
      stream: true,
      conversation_history: conversationHistory,
    } as ChatRequest),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Upload a document to the knowledge base
 */
export async function uploadDocument(file: File): Promise<{
  message: string;
  chunks_created: number;
  filename: string;
}> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to upload document');
  }

  return response.json();
}

/**
 * List all indexed documents
 */
export async function listDocuments(): Promise<DocumentsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents`);
  if (!response.ok) {
    throw new Error('Failed to list documents');
  }
  return response.json();
}

/**
 * Delete a document from the knowledge base
 */
export async function deleteDocument(source: string): Promise<{
  message: string;
  chunks_deleted: number;
}> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${encodeURIComponent(source)}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to delete document');
  }

  return response.json();
}

/**
 * Reset/clear all documents
 */
export async function resetDocuments(): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/documents/reset`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to reset documents');
  }

  return response.json();
}
