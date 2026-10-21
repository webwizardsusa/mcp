import { Box, Chip, Stack, Typography } from '@mui/material';
import { Star as StarIcon } from '@mui/icons-material';
import type { Product } from '../types/product';

type Props = {
  product: Product;
};

const formatPrice = (price: number | string, unit: string) => {
  const value = typeof price === 'string' ? Number(price) : price;
  const formatted = Number.isFinite(value)
    ? value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
    : `$${price}`;
  return `${formatted} / ${unit}`;
};

const ProductCard = ({ product }: Props) => {
  const rating =
    typeof product.rating === 'string' ? Number(product.rating) : product.rating;

  return (
    <Box
      sx={{
        bgcolor: 'background.paper',
        borderRadius: 2,
        border: '1px solid',
        borderColor: 'grey.200',
        boxShadow: '0 2px 8px rgba(16, 24, 40, 0.04)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        transition: 'box-shadow 0.2s ease, transform 0.2s ease',
        '&:hover': {
          boxShadow: '0 8px 24px rgba(16, 24, 40, 0.08)',
          transform: 'translateY(-2px)',
        },
      }}
    >
      <Box
        sx={{
          height: 180,
          bgcolor: '#ffffff',
          borderBottom: '1px solid',
          borderColor: 'grey.200',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2,
        }}
      >
        <Box
          component="img"
          src={product.image_url}
          alt={product.name}
          sx={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
          }}
        />
      </Box>

      <Stack spacing={1} sx={{ p: 2, flex: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.3 }}>
          {product.name}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <StarIcon sx={{ fontSize: 16, color: '#F5B301' }} />
          <Typography variant="body2" color="textSecondary">
            {Number.isFinite(rating) ? rating.toFixed(1) : product.rating} (
            {product.review_count.toLocaleString()})
          </Typography>
        </Box>

        <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary' }}>
          {formatPrice(product.price, product.unit)}
        </Typography>

        <Box sx={{ mt: 'auto', pt: 1 }}>
          <Chip
            label={product.badge}
            size="small"
            sx={{
              fontWeight: 600,
              bgcolor: product.badge === 'Premium' ? 'primary.light' : 'grey.200',
              color: product.badge === 'Premium' ? 'primary.dark' : 'text.secondary',
            }}
          />
        </Box>
      </Stack>
    </Box>
  );
};

export default ProductCard;
