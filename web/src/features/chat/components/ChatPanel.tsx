import { Box, IconButton, Typography } from '@mui/material';
import {
  Close as CloseIcon,
  HorizontalRule as MinimizeIcon,
} from '@mui/icons-material';
import ChatComposer from './ChatComposer';
import ChatMessageList from './ChatMessageList';
import ChatSuggestions from './ChatSuggestions';
import { useChatConversation } from '../hooks';

type Props = {
  open: boolean;
  onClose: () => void;
};

const ChatPanel = ({ open, onClose }: Props) => {
  const {
    messages,
    draft,
    setDraft,
    isLoading,
    hasUserMessage,
    send,
  } = useChatConversation();

  if (!open) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        right: { xs: 12, sm: 24 },
        bottom: { xs: 12, sm: 24 },
        width: { xs: 'calc(100vw - 24px)', sm: 380 },
        maxWidth: 420,
        height: { xs: 'min(70vh, 560px)', sm: 560 },
        zIndex: (theme) => theme.zIndex.modal,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2.5,
        overflow: 'hidden',
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'grey.200',
        boxShadow: '0 16px 48px rgba(16, 24, 40, 0.18)',
      }}
    >
      <Box
        sx={{
          px: 2,
          py: 1.25,
          bgcolor: 'primary.main',
          color: 'common.white',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <Typography variant="subtitle1" sx={{ fontWeight: 700, flex: 1 }}>
          AI Product Advisor
        </Typography>
        <IconButton
          size="small"
          aria-label="Minimize chat"
          onClick={onClose}
          sx={{ color: 'common.white' }}
        >
          <MinimizeIcon fontSize="small" />
        </IconButton>
        <IconButton
          size="small"
          aria-label="Close chat"
          onClick={onClose}
          sx={{ color: 'common.white' }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      </Box>

      <ChatMessageList messages={messages} isLoading={isLoading} />

      {!hasUserMessage ? (
        <ChatSuggestions onSelect={(text) => void send(text)} />
      ) : null}

      <ChatComposer
        value={draft}
        onChange={setDraft}
        onSend={() => void send()}
        disabled={isLoading}
      />
    </Box>
  );
};

export default ChatPanel;
