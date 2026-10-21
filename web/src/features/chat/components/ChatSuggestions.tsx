import { Box, Button } from '@mui/material';
import {
  CompareArrows as CompareIcon,
  DirectionsCar as CarIcon,
  HelpOutlined as HelpIcon,
  SellOutlined as PriceIcon,
} from '@mui/icons-material';

const SUGGESTIONS = [
  {
    label: 'Recommend brake pad for Hyundai Creta 2022',
    icon: <CarIcon fontSize="small" />,
  },
  {
    label: 'Compare Brembo vs Bosch brake pads',
    icon: <CompareIcon fontSize="small" />,
  },
  {
    label: 'Best brake pad under $50',
    icon: <PriceIcon fontSize="small" />,
  },
  {
    label: 'Is Brembo better than Bosch?',
    icon: <HelpIcon fontSize="small" />,
  },
] as const;

type Props = {
  onSelect: (text: string) => void;
};

const ChatSuggestions = ({ onSelect }: Props) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, px: 2, pb: 1.5 }}>
    {SUGGESTIONS.map((item) => (
      <Button
        key={item.label}
        variant="outlined"
        color="inherit"
        onClick={() => onSelect(item.label)}
        startIcon={item.icon}
        sx={{
          justifyContent: 'flex-start',
          textAlign: 'left',
          textTransform: 'none',
          borderRadius: 2,
          borderColor: 'grey.300',
          bgcolor: 'background.paper',
          color: 'text.primary',
          px: 1.5,
          py: 1,
          fontWeight: 500,
          fontSize: '0.8125rem',
          lineHeight: 1.35,
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'primary.light',
          },
        }}
      >
        {item.label}
      </Button>
    ))}
  </Box>
);

export default ChatSuggestions;
