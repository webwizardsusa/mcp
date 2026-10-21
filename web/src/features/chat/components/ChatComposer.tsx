import { Box, IconButton, TextField } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
};

const ChatComposer = ({ value, onChange, onSend, disabled = false }: Props) => {
  const canSend = value.trim().length > 0 && !disabled;

  return (
    <Box
      sx={{
        px: 2,
        py: 1.5,
        borderTop: '1px solid',
        borderColor: 'grey.200',
        bgcolor: 'background.paper',
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
    >
      <TextField
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (canSend) onSend();
          }
        }}
        placeholder="Type your message..."
        size="small"
        fullWidth
        multiline
        maxRows={3}
        disabled={disabled}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
            bgcolor: 'grey.100',
          },
        }}
      />
      <IconButton
        color="primary"
        aria-label="Send message"
        onClick={onSend}
        disabled={!canSend}
        sx={{
          bgcolor: 'primary.main',
          color: 'common.white',
          width: 40,
          height: 40,
          '&:hover': { bgcolor: 'primary.dark' },
          '&.Mui-disabled': {
            bgcolor: 'grey.300',
            color: 'grey.500',
          },
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>
    </Box>
  );
};

export default ChatComposer;
