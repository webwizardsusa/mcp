import { Box } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type Props = {
  text: string;
};

/** Renders assistant markdown (bold, lists, code) inside chat bubbles. */
const ChatMarkdown = ({ text }: Props) => (
  <Box
    sx={{
      color: 'text.primary',
      fontSize: '0.875rem',
      lineHeight: 1.55,
      '& p': { m: 0, mb: 1 },
      '& p:last-child': { mb: 0 },
      '& strong': { fontWeight: 700 },
      '& em': { fontStyle: 'italic' },
      '& ul, & ol': { m: 0, mb: 1, pl: 2.25 },
      '& li': { mb: 0.5 },
      '& li:last-child': { mb: 0 },
      '& code': {
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
        fontSize: '0.8em',
        px: 0.5,
        py: 0.15,
        borderRadius: 0.75,
        bgcolor: 'grey.100',
      },
      '& pre': {
        m: 0,
        mb: 1,
        p: 1,
        borderRadius: 1,
        bgcolor: 'grey.100',
        overflowX: 'auto',
      },
      '& pre code': {
        p: 0,
        bgcolor: 'transparent',
      },
      '& a': {
        color: 'primary.main',
        textDecoration: 'underline',
      },
    }}
  >
    <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
  </Box>
);

export default ChatMarkdown;
