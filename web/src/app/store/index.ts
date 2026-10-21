import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux';
import { baseApi } from '@/app/api';
import { initAuthSync } from '@/features/auth/authSync';
import { authListenerMiddleware } from '@/features/auth/listeners/authListener';
import authReducer from '@/features/auth/slices/authSlice';
import '@/features/auth/api/authApi';
import '@/features/product/api/productApi';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    [baseApi.reducerPath]: baseApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .prepend(authListenerMiddleware.middleware)
      .concat(baseApi.middleware),
});

setupListeners(store.dispatch);
initAuthSync(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
