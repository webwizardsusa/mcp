import { useState } from 'react';
import { useSendChatMutation } from '../api/chatApi';
import type { ChatMessage } from '../types/chat';
import { getErrorMessage } from '@/shared/utils';

const WELCOME: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  text: "Hi! I'm your AI Product Advisor. How can I help you today?",
};

const nextId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `msg-${Date.now()}-${Math.random().toString(16).slice(2)}`;

export const useChatConversation = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [draft, setDraft] = useState('');
  const [sendChat, { isLoading }] = useSendChatMutation();

  const hasUserMessage = messages.some((m) => m.role === 'user');

  const send = async (raw?: string) => {
    const text = (raw ?? draft).trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = { id: nextId(), role: 'user', text };
    const history = [...messages, userMessage]
      .filter((m) => m.id !== 'welcome')
      .map((m) => ({ role: m.role, content: m.text }));

    setMessages((prev) => [...prev, userMessage]);
    setDraft('');

    try {
      const result = await sendChat({
        message: text,
        history: history.slice(0, -1),
      }).unwrap();

      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: 'assistant', text: result.reply },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'assistant',
          text: getErrorMessage(err, 'Chat failed. Please try again.'),
        },
      ]);
    }
  };

  const applySuggestion = (text: string) => {
    setDraft(text);
  };

  return {
    messages,
    draft,
    setDraft,
    isLoading,
    hasUserMessage,
    send,
    applySuggestion,
  };
};
