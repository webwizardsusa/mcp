import {
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from '@mui/material';
import { PageContainer, Spinner } from '@/shared/components';
import ProductCard from '../components/ProductCard';
import ProductPagination from '../components/ProductPagination';
import { useProductList } from '../hooks';
import type { ProductSort } from '../types/product';

const ProductListPage = () => {
  const {
    page,
    sort,
    sortOptions,
    items,
    total,
    totalPages,
    rangeLabel,
    isLoading,
    isFetching,
    isError,
    refetch,
    setPage,
    setSort,
  } = useProductList();

  return (
    <PageContainer title="Products" description="Browse automotive spare parts">
      <Box sx={{ px: { xs: 2, md: 3 }, py: 2.5, flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: { xs: 'stretch', sm: 'center' },
            justifyContent: 'space-between',
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 1.5,
            mb: 2.5,
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            All Products ({total.toLocaleString()} results)
          </Typography>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel id="product-sort-label">Sort by</InputLabel>
            <Select
              labelId="product-sort-label"
              label="Sort by"
              value={sort}
              onChange={(e) => setSort(e.target.value as ProductSort)}
            >
              {sortOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {isLoading ? (
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Spinner />
          </Box>
        ) : isError ? (
          <Stack spacing={2} sx={{ py: 8, alignItems: 'center' }}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Couldn’t load products
            </Typography>
            <Typography color="textSecondary">Check your connection and try again.</Typography>
            <Button variant="contained" onClick={() => void refetch()}>
              Retry
            </Button>
          </Stack>
        ) : items.length === 0 ? (
          <Stack spacing={1} sx={{ py: 8, alignItems: 'center' }}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              No products found
            </Typography>
            <Typography color="textSecondary">Try a different search or clear filters.</Typography>
          </Stack>
        ) : (
          <>
            <Grid container spacing={2.5} sx={{ opacity: isFetching ? 0.7 : 1, transition: 'opacity 0.2s' }}>
              {items.map((product) => (
                <Grid key={product.id} size={{ xs: 12, sm: 6, md: 4, lg: 4, xl: 3 }}>
                  <ProductCard product={product} />
                </Grid>
              ))}
            </Grid>
            <Box sx={{ mt: 3 }}>
              <ProductPagination
                page={page}
                totalPages={totalPages}
                rangeLabel={rangeLabel}
                onPageChange={setPage}
              />
            </Box>
          </>
        )}
      </Box>
    </PageContainer>
  );
};

export default ProductListPage;
