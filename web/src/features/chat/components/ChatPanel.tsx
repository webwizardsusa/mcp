import { useEffect, useId, useRef } from 'react';
import { Box, Dialog, IconButton, Typography } from '@mui/material';
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
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement | null>(null);
  const {
    messages,
    draft,
    setDraft,
    isLoading,
    hasUserMessage,
    send,
  } = useChatConversation();

  useEffect(() => {
    if (!open) return;
    const timer = window.setTimeout(() => closeRef.current?.focus(), 0);
    return () => window.clearTimeout(timer);
  }, [open]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      hideBackdrop
      disableScrollLock
      aria-labelledby={titleId}
      aria-modal="true"
      slotProps={{
        paper: {
          role: 'dialog',
          sx: {
            position: 'fixed',
            m: 0,
            right: { xs: 12, sm: 24 },
            bottom: { xs: 12, sm: 24 },
            left: 'auto',
            top: 'auto',
            width: { xs: 'calc(100vw - 24px)', sm: 380 },
            maxWidth: 420,
            height: { xs: 'min(70vh, 560px)', sm: 560 },
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 2.5,
            overflow: 'hidden',
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'grey.200',
            boxShadow: '0 16px 48px rgba(16, 24, 40, 0.18)',
          },
        },
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
          flexShrink: 0,
        }}
      >
        <Typography id={titleId} variant="subtitle1" sx={{ fontWeight: 700, flex: 1 }}>
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
          ref={closeRef}
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
    </Dialog>
  );
};

export default ChatPanel;
