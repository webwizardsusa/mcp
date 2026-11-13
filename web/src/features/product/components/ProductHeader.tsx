import { useEffect, useState } from 'react';
import {
  AppBar,
  Avatar,
  Box,
  IconButton,
  InputAdornment,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  TextField,
  Toolbar,
  Typography,
} from '@mui/material';
import {
  DirectionsCarFilledOutlined as BrandIcon,
  KeyboardArrowDown as ArrowDownIcon,
  Logout as LogoutIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { useSearchParams } from 'react-router';
import { layoutConfig } from '@/app/providers';
import { useProductList, useProductUserMenu } from '../hooks';

const ProductHeader = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const qFromUrl = searchParams.get('q') ?? '';
  const [searchValue, setSearchValue] = useState(qFromUrl);
  const { total: totalProducts } = useProductList();

  const {
    user,
    userInitials,
    isLoggingOut,
    menuOpen,
    anchorEl,
    openMenu,
    closeMenu,
    onLogout,
  } = useProductUserMenu();

  useEffect(() => {
    setSearchValue(qFromUrl);
  }, [qFromUrl]);

  useEffect(() => {
    const trimmed = searchValue.trim();
    const current = qFromUrl.trim();
    if (trimmed === current) return;

    const timer = window.setTimeout(() => {
      const params = new URLSearchParams(searchParams);
      if (trimmed) params.set('q', trimmed);
      else params.delete('q');
      params.set('page', '1');
      setSearchParams(params, { replace: true });
    }, 350);

    return () => window.clearTimeout(timer);
  }, [searchValue, qFromUrl, searchParams, setSearchParams]);

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        color: 'text.primary',
        borderBottom: '1px solid',
        borderColor: 'grey.200',
        boxShadow: '0 1px 0 rgba(16, 24, 40, 0.04)',
      }}
    >
      <Toolbar
        sx={{
          minHeight: `${layoutConfig.topbarHeight}px !important`,
          gap: { xs: 1, md: 2 },
          px: { xs: 1.5, sm: 2.5 },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: 1.5,
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <BrandIcon sx={{ color: 'common.white', fontSize: 20 }} />
          </Box>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              fontSize: '1rem',
              color: '#2A3547',
              display: { xs: 'none', sm: 'block' },
            }}
            noWrap
          >
            AI Product Advisor
          </Typography>
        </Box>

        <TextField
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          placeholder="Search for products, brands, or categories..."
          size="small"
          fullWidth
          sx={{
            maxWidth: 560,
            mx: { xs: 0, md: 'auto' },
            '& .MuiOutlinedInput-root': {
              borderRadius: 999,
              bgcolor: 'grey.100',
            },
          }}
          slotProps={{
            htmlInput: { 'aria-label': 'Search products' },
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" color="action" />
                </InputAdornment>
              ),
            },
          }}
        />

        <Typography
          variant="body2"
          sx={{
            fontWeight: 600,
            color: 'text.secondary',
            display: { xs: 'none', lg: 'block' },
            whiteSpace: 'nowrap',
          }}
        >
          Total Products: {totalProducts.toLocaleString()}
        </Typography>

        <Box
          component="button"
          type="button"
          onClick={(e) => openMenu(e.currentTarget)}
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          aria-label="Account menu"
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            cursor: 'pointer',
            borderRadius: 2,
            px: 1,
            py: 0.5,
            bgcolor: 'grey.100',
            border: '1px solid',
            borderColor: 'grey.200',
            flexShrink: 0,
            ml: { xs: 0, lg: 1 },
            font: 'inherit',
            color: 'inherit',
            '&:hover': { bgcolor: 'grey.200' },
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
              maxWidth: 140,
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

export default ProductHeader;
