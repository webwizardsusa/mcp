import { createListenerMiddleware, isAnyOf } from '@reduxjs/toolkit';
import { baseApi } from '@/app/api/baseApi';
import { broadcastLogout } from '@/features/auth/authSync';
import { clearSession, logout } from '@/features/auth/slices/authSlice';

/**
 * Whenever auth is cleared, drop RTK Query cache so the next user never sees
 * the previous user's data. Broadcast logout only for intentional local logout.
 */
export const authListenerMiddleware = createListenerMiddleware();

authListenerMiddleware.startListening({
  matcher: isAnyOf(logout, clearSession),
  effect: (action, listenerApi) => {
    listenerApi.dispatch(baseApi.util.resetApiState());
    if (logout.match(action)) {
      broadcastLogout();
    }
  },
});
