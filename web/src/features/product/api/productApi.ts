import { baseApi, API_TAGS } from '@/app/api';
import type { ProductListParams, ProductListResult } from '../types/product';

export const productApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    listProducts: build.query<ProductListResult, ProductListParams | void>({
      query: (params) => ({
        url: '/products',
        params: {
          q: params?.q || undefined,
          page: params?.page ?? 1,
          page_size: params?.page_size ?? 12,
          sort: params?.sort ?? 'popular',
        },
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ id }) => ({ type: API_TAGS.Product, id })),
              { type: API_TAGS.Product, id: 'LIST' },
            ]
          : [{ type: API_TAGS.Product, id: 'LIST' }],
    }),
  }),
});

export const { useListProductsQuery } = productApi;
