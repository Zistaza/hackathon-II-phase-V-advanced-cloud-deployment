'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '../ui/button';

interface MobileMenuProps {
  isOpen: boolean;
  isAuthenticated: boolean;
  onClose: () => void;
  onLogout: () => void;
}

export const MobileMenu: React.FC<MobileMenuProps> = ({
  isOpen,
  isAuthenticated,
  onClose,
  onLogout,
}) => {
  if (!isOpen) return null;

  return (
    <div className="md:hidden mt-4 pb-4 border-t border-border pt-4">
      <nav className="flex flex-col space-y-2">
        {isAuthenticated ? (
          <>
            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-lg hover:bg-accent transition-colors duration-200 text-foreground font-medium"
              onClick={onClose}
            >
              Dashboard
            </Link>
            <Link
              href="/tasks"
              className="px-4 py-2 rounded-lg hover:bg-accent transition-colors duration-200 text-foreground font-medium"
              onClick={onClose}
            >
              Tasks
            </Link>
            <button
              onClick={() => {
                onLogout();
                onClose();
              }}
              className="px-4 py-2 rounded-lg hover:bg-destructive/10 hover:text-destructive text-destructive transition-colors duration-200 text-left font-medium"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="px-4 py-2 rounded-lg hover:bg-accent transition-colors duration-200 text-foreground font-medium"
              onClick={onClose}
            >
              Login
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-primary to-indigo-500 hover:from-primary/90 hover:to-indigo-500/90 text-white transition-all duration-200 font-medium text-center"
              onClick={onClose}
            >
              Register
            </Link>
          </>
        )}
      </nav>
    </div>
  );
};
