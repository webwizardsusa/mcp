export type ChatRole = 'user' | 'assistant';

export type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
};

export type ChatRequest = {
  message: string;
  history: { role: ChatRole; content: string }[];
};

export type ChatResponse = {
  reply: string;
  tools_used: string[];
};
