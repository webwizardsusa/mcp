import { Box } from '@mui/material';
import { Outlet } from 'react-router';
import ProductHeader from './ProductHeader';

const ProductShell = () => (
  <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'grey.100' }}>
    <ProductHeader />
    <Box
      component="main"
      sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}
    >
      <Outlet />
    </Box>
  </Box>
);

export default ProductShell;
