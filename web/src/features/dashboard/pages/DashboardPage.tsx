import { Box, Stack, Typography } from '@mui/material';
import { DescriptionOutlined as DocIcon } from '@mui/icons-material';
import { PageContainer } from '@/shared/components';

const DashboardPage = () => (
  <PageContainer title="Dashboard" description="Empty dashboard">
    <Box
      sx={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
      }}
    >
      <Stack
        spacing={2}
        sx={{
          maxWidth: 480,
          width: '100%',
          textAlign: 'center',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            width: 64,
            height: 64,
            borderRadius: 2,
            bgcolor: 'primary.light',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <DocIcon color="primary" sx={{ fontSize: 32 }} />
        </Box>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Welcome
        </Typography>
        <Typography color="textSecondary">
          Your dashboard is ready. Modules will appear here next.
        </Typography>
      </Stack>
    </Box>
  </PageContainer>
);

export default DashboardPage;
