export type ProductSort = 'popular' | 'price_asc' | 'price_desc' | 'rating_desc' | 'name_asc';

export type Product = {
  id: string;
  name: string;
  brand: string;
  category: string;
  description: string;
  price: number | string;
  unit: string;
  rating: number | string;
  review_count: number;
  badge: 'Premium' | 'Standard' | string;
  image_url: string;
  vehicle_make?: string | null;
  vehicle_model?: string | null;
  vehicle_year_from?: number | null;
  vehicle_year_to?: number | null;
  use_case?: string | null;
};

export type ProductListResult = {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export type ProductListParams = {
  q?: string;
  page?: number;
  page_size?: number;
  sort?: ProductSort;
};
