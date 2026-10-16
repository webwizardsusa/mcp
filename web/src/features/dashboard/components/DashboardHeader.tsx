import {
  AppBar,
  Avatar,
  Box,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
} from '@mui/material';
import {
  DescriptionOutlined as BrandIcon,
  KeyboardArrowDown as ArrowDownIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { layoutConfig } from '@/app/providers';
import { useDashboardUserMenu } from '../hooks';

type Props = {
  title?: string;
};

const DashboardHeader = ({ title = 'Dashboard' }: Props) => {
  const {
    user,
    userInitials,
    isLoggingOut,
    menuOpen,
    anchorEl,
    openMenu,
    closeMenu,
    onLogout,
  } = useDashboardUserMenu();

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background: 'linear-gradient(180deg, #F7F9FF 0%, #EEF3FF 100%)',
        color: 'text.primary',
        borderBottom: '1px solid #E2E8F6',
        boxShadow: '0 1px 0 rgba(93, 135, 255, 0.06)',
      }}
    >
      <Toolbar
        sx={{
          minHeight: `${layoutConfig.topbarHeight}px !important`,
          gap: 1.5,
          px: { xs: 1.5, sm: 2.5 },
        }}
      >
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1.5,
            bgcolor: 'primary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <BrandIcon sx={{ color: 'common.white', fontSize: 20 }} />
        </Box>
        <Typography
          variant="h6"
          sx={{ fontWeight: 700, fontSize: '1rem', flex: 1, minWidth: 0, color: '#2A3547' }}
          noWrap
        >
          {title}
        </Typography>

        <Box
          onClick={(e) => openMenu(e.currentTarget)}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            cursor: 'pointer',
            borderRadius: 2,
            px: 1,
            py: 0.5,
            bgcolor: 'rgba(255,255,255,0.85)',
            border: '1px solid #E2E8F6',
            '&:hover': { bgcolor: 'common.white' },
          }}
        >
          <Avatar
            sx={{
              width: 32,
              height: 32,
              bgcolor: 'primary.main',
              fontSize: '0.75rem',
              fontWeight: 700,
            }}
          >
            {userInitials}
          </Avatar>
          <Typography
            variant="subtitle2"
            noWrap
            sx={{
              fontWeight: 600,
              color: '#2A3547',
              display: { xs: 'none', sm: 'block' },
              maxWidth: 160,
            }}
          >
            {user?.name || 'User'}
          </Typography>
          <IconButton size="small" aria-label="Account menu" sx={{ p: 0.25 }}>
            <ArrowDownIcon fontSize="small" />
          </IconButton>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={menuOpen}
          onClose={closeMenu}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <MenuItem onClick={onLogout} disabled={isLoggingOut}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>{isLoggingOut ? 'Signing out...' : 'Sign out'}</ListItemText>
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default DashboardHeader;
