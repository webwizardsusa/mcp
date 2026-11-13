import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/app/store';
import { authApi } from '../api/authApi';
import {
  clearSession,
  selectAuthInitialized,
  setCredentials,
  setInitialized,
} from '../slices/authSlice';

/** Restores session from HttpOnly refresh cookie on app start. */
export const useAuthBootstrap = () => {
  const dispatch = useAppDispatch();
  const initialized = useAppSelector(selectAuthInitialized);

  useEffect(() => {
    let cancelled = false;
    // One-time cleanup of pre-rename localStorage key.
    localStorage.removeItem('ai_document_auth');
    localStorage.removeItem('ai_product_advisor_auth');

    const restore = async () => {
      try {
        const result = await dispatch(authApi.endpoints.refresh.initiate()).unwrap();
        if (!cancelled) {
          dispatch(setCredentials(result));
        }
      } catch {
        // No session / failed refresh — clear this tab only; do not force-logout others.
        if (!cancelled) {
          dispatch(clearSession());
        }
      } finally {
        if (!cancelled) {
          dispatch(setInitialized(true));
        }
      }
    };

    void restore();

    return () => {
      cancelled = true;
    };
  }, [dispatch]);

  return { initialized };
};
