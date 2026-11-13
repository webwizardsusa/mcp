import { Box, CircularProgress, Typography } from '@mui/material';
import { WavingHand as WaveIcon } from '@mui/icons-material';
import type { ChatMessage } from '@/features/chat/types/chat';
import ChatMarkdown from './ChatMarkdown';

type Props = {
  messages: ChatMessage[];
  isLoading?: boolean;
};

const ChatMessageList = ({ messages, isLoading = false }: Props) => (
  <Box
    sx={{
      flex: 1,
      minHeight: 0,
      overflowY: 'auto',
      px: 2,
      py: 2,
      display: 'flex',
      flexDirection: 'column',
      gap: 1.5,
      bgcolor: '#F7F8FA',
    }}
  >
    {messages.map((message) => {
      const isUser = message.role === 'user';
      return (
        <Box
          key={message.id}
          sx={{
            alignSelf: isUser ? 'flex-end' : 'flex-start',
            maxWidth: '88%',
          }}
        >
          <Box
            sx={{
              px: 1.75,
              py: 1.25,
              borderRadius: 2,
              bgcolor: isUser ? 'primary.light' : 'background.paper',
              border: '1px solid',
              borderColor: isUser ? 'primary.main' : 'grey.200',
              boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)',
            }}
          >
            {!isUser && message.id === 'welcome' ? (
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                <WaveIcon sx={{ color: 'warning.main', fontSize: 20, mt: 0.15 }} />
                <Typography variant="body2" sx={{ color: 'text.primary', lineHeight: 1.5 }}>
                  {message.text}
                </Typography>
              </Box>
            ) : isUser ? (
              <Typography
                variant="body2"
                sx={{
                  color: 'text.primary',
                  lineHeight: 1.5,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {message.text}
              </Typography>
            ) : (
              <ChatMarkdown text={message.text} />
            )}
          </Box>
        </Box>
      );
    })}

    {isLoading ? (
      <Box
        sx={{
          alignSelf: 'flex-start',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          px: 1.5,
          py: 1,
          borderRadius: 2,
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'grey.200',
        }}
      >
        <CircularProgress size={16} />
        <Typography variant="caption" color="textSecondary">
          Thinking…
        </Typography>
      </Box>
    ) : null}
  </Box>
);

export default ChatMessageList;
