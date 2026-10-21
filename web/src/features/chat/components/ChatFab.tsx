import { Badge, Fab } from '@mui/material';
import { ChatBubbleOutlined as ChatIcon } from '@mui/icons-material';

type Props = {
  onClick: () => void;
  showBadge?: boolean;
};

const ChatFab = ({ onClick, showBadge = true }: Props) => (
  <Badge
    color="error"
    badgeContent={showBadge ? 1 : 0}
    overlap="circular"
    sx={{
      position: 'fixed',
      right: { xs: 16, sm: 24 },
      bottom: { xs: 16, sm: 24 },
      zIndex: (theme) => theme.zIndex.modal - 1,
      '& .MuiBadge-badge': {
        top: 8,
        right: 8,
      },
    }}
  >
    <Fab
      color="primary"
      aria-label="Open AI Product Advisor chat"
      onClick={onClick}
      sx={{
        width: 56,
        height: 56,
        boxShadow: '0 8px 24px rgba(34, 197, 94, 0.35)',
      }}
    >
      <ChatIcon />
    </Fab>
  </Badge>
);

export default ChatFab;
