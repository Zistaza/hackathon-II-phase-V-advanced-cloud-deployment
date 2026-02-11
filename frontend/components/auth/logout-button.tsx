'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/auth-context';
import { Button } from '../ui/button';

export const LogoutButton: React.FC = () => {
  const router = useRouter();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
    router.refresh(); // Refresh to update the UI
  };

  return (
    <Button onClick={handleLogout} variant="secondary">
      Logout
    </Button>
  );
};