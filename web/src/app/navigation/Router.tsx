import { lazy, type ComponentType } from 'react';
import { createBrowserRouter, Navigate } from 'react-router';
import { Loadable } from '@/shared/components';
import ProtectedRoute, { GuestRoute } from '@/features/auth/components/ProtectedRoute';

const lazyPage = (loader: () => Promise<{ default: ComponentType }>) => Loadable(lazy(loader));

const BlankLayout = lazyPage(() => import('@/app/layouts/blank/BlankLayout'));
const Login = lazyPage(() => import('@/features/auth/pages/Login'));
const Error = lazyPage(() => import('@/features/auth/pages/Error'));
const ProductShell = lazyPage(
  () => import('@/features/product/components/ProductShell'),
);
const ProductListPage = lazyPage(
  () => import('@/features/product/pages/ProductListPage'),
);

const routes = [
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <BlankLayout />,
        children: [
          {
            element: <ProductShell />,
            children: [
              { path: '/', element: <ProductListPage /> },
              { path: '*', element: <Navigate to="/" replace /> },
            ],
          },
        ],
      },
    ],
  },
  {
    path: '/auth',
    element: <BlankLayout />,
    children: [
      {
        element: <GuestRoute />,
        children: [{ path: 'login', element: <Login /> }],
      },
      { path: '404', element: <Error /> },
      { path: '*', element: <Navigate to="/auth/404" replace /> },
    ],
  },
];

const router = createBrowserRouter(routes);
export default router;
