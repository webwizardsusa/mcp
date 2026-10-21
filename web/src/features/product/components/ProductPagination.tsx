import { Box, Pagination, Typography } from '@mui/material';

type Props = {
  page: number;
  totalPages: number;
  rangeLabel: string;
  onPageChange: (page: number) => void;
};

const ProductPagination = ({ page, totalPages, rangeLabel, onPageChange }: Props) => {
  if (totalPages <= 0) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        alignItems: { xs: 'stretch', sm: 'center' },
        justifyContent: 'space-between',
        gap: 2,
        pt: 1,
        pb: 2,
      }}
    >
      <Typography variant="body2" color="textSecondary">
        {rangeLabel}
      </Typography>
      <Pagination
        page={page}
        count={totalPages}
        onChange={(_e, value) => onPageChange(value)}
        color="primary"
        shape="rounded"
        siblingCount={1}
        boundaryCount={1}
      />
    </Box>
  );
};

export default ProductPagination;
