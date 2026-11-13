export type ChatRole = 'user' | 'assistant' | 'error';

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
};

export type ChatHistoryRole = 'user' | 'assistant';

export type ChatRequest = {
  message: string;
  history: { role: ChatHistoryRole; content: string }[];
};

export type ChatResponse = {
  reply: string;
  tools_used: string[];
};
