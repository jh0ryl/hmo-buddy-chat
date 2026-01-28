export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatConfig {
  apiEndpoint: string;
  headers?: Record<string, string>;
}
