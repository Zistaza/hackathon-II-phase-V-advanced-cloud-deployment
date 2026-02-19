'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../contexts/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '../ui/button';
import ThemeToggle from '../ui/theme-toggle';
import { MobileMenu } from './mobile-menu';

export const Header: React.FC = () => {
  const { state, logout } = useAuth();
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/login');
    router.refresh();
  };

  return (
    <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm border-border/40">
      <div className="container mx-auto px-4 sm:px-6 py-4">
        <div className="flex justify-between items-center">
          <Link
            href="/"
            className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-primary to-indigo-500 bg-clip-text text-transparent hover:opacity-90 transition-opacity duration-200"
            onClick={() => setIsMenuOpen(false)}
          >
            Todo App
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <ThemeToggle />
            <div className="h-8 w-px bg-border"></div>
            {state.isAuthenticated ? (
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-4">
                  <Link href="/dashboard">
                    <Button variant="ghost" size="md" className="hover:bg-primary/10 hover:text-primary transition-colors duration-200 rounded-lg">
                      Dashboard
                    </Button>
                  </Link>
                  <Link href="/tasks">
                    <Button variant="ghost" size="md" className="hover:bg-primary/10 hover:text-primary transition-colors duration-200 rounded-lg">
                      Tasks
                    </Button>
                  </Link>
                </div>
                <div className="h-8 w-px bg-border"></div>
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  size="md"
                  className="border-destructive/30 hover:bg-destructive/10 hover:border-destructive text-destructive transition-colors duration-200 rounded-lg"
                >
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link href="/login">
                  <Button variant="ghost" size="md" className="hover:bg-primary/10 hover:text-primary transition-colors duration-200 rounded-lg">
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button variant="primary" size="md" className="bg-gradient-to-r from-primary to-indigo-500 hover:from-primary/90 hover:to-indigo-500/90 text-white transition-all duration-200 rounded-lg shadow-md">
                    Register
                  </Button>
                </Link>
              </div>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg hover:bg-accent transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6 text-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <MobileMenu
          isOpen={isMenuOpen}
          isAuthenticated={state.isAuthenticated}
          onClose={() => setIsMenuOpen(false)}
          onLogout={handleLogout}
        />
      </div>
    </header>
  );
};
