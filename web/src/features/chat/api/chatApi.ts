import { baseApi, API_TAGS } from '@/app/api';
import type { ChatRequest, ChatResponse } from '../types/chat';

export const chatApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    sendChat: build.mutation<ChatResponse, ChatRequest>({
      query: (body) => ({
        url: '/chat',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: API_TAGS.Chat, id: 'SESSION' }],
    }),
  }),
});

export const { useSendChatMutation } = chatApi;
