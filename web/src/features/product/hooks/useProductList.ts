import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router';
import { useListProductsQuery } from '../api/productApi';
import type { ProductSort } from '../types/product';

const PAGE_SIZE = 12;

const SORT_OPTIONS: { value: ProductSort; label: string }[] = [
  { value: 'popular', label: 'Popular' },
  { value: 'rating_desc', label: 'Top rated' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
  { value: 'name_asc', label: 'Name A–Z' },
];

const parseSort = (value: string | null): ProductSort => {
  const allowed: ProductSort[] = [
    'popular',
    'price_asc',
    'price_desc',
    'rating_desc',
    'name_asc',
  ];
  if (value && allowed.includes(value as ProductSort)) {
    return value as ProductSort;
  }
  return 'popular';
};

export const useProductList = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const q = searchParams.get('q') ?? '';
  const page = Math.max(1, Number(searchParams.get('page') || 1) || 1);
  const sort = parseSort(searchParams.get('sort'));

  const { data, isLoading, isFetching, isError, refetch } = useListProductsQuery({
    q: q.trim() || undefined,
    page,
    page_size: PAGE_SIZE,
    sort,
  });

  const setQuery = useCallback(
    (next: string) => {
      const params = new URLSearchParams(searchParams);
      const trimmed = next.trim();
      if (trimmed) params.set('q', trimmed);
      else params.delete('q');
      params.set('page', '1');
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const setPage = useCallback(
    (nextPage: number) => {
      const params = new URLSearchParams(searchParams);
      params.set('page', String(Math.max(1, nextPage)));
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const setSort = useCallback(
    (nextSort: ProductSort) => {
      const params = new URLSearchParams(searchParams);
      params.set('sort', nextSort);
      params.set('page', '1');
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const rangeLabel = useMemo(() => {
    const total = data?.total ?? 0;
    if (!total) return 'Showing 0 products';
    const from = (page - 1) * PAGE_SIZE + 1;
    const to = Math.min(page * PAGE_SIZE, total);
    return `Showing ${from} to ${to} of ${total.toLocaleString()} products`;
  }, [data?.total, page]);

  return {
    q,
    page,
    sort,
    sortOptions: SORT_OPTIONS,
    pageSize: PAGE_SIZE,
    items: data?.items ?? [],
    total: data?.total ?? 0,
    totalPages: data?.total_pages ?? 0,
    rangeLabel,
    isLoading,
    isFetching,
    isError,
    refetch,
    setQuery,
    setPage,
    setSort,
  };
};
