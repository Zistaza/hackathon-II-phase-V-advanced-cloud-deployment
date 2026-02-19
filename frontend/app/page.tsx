'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import HeroSection from '@/components/home/hero-section';
import FeaturesSection from '@/components/home/features-section';
import AuthSection from '@/components/home/auth-section';
import ThemeToggle from '@/components/ui/theme-toggle';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* Simplified background elements */}
      <div className="fixed inset-0 -z-20 overflow-hidden">
        <div className="absolute -top-1/3 left-1/4 w-[1200px] h-[1200px] rounded-full bg-gradient-to-r from-primary/10 to-secondary/10 blur-3xl"></div>
        <div className="absolute top-1/4 right-1/4 w-[1000px] h-[1000px] rounded-full bg-gradient-to-r from-secondary/10 to-accent/10 blur-3xl"></div>
      </div>

      {/* Header with theme toggle */}
      <header className="absolute top-6 right-6 z-20">
        <ThemeToggle />
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="flex flex-col items-center justify-center min-h-screen">
          {/* Hero Section */}
          <section className="w-full max-w-6xl text-center mb-20 sm:mb-28 lg:mb-32">
            <HeroSection />
          </section>

          {/* Features Section */}
          <section className="w-full max-w-7xl mb-20 sm:mb-28 lg:mb-32">
            <FeaturesSection />
          </section>

          {/* Auth Section */}
          <section className="w-full max-w-2xl">
            <AuthSection />
          </section>
        </div>
      </main>
    </div>
  );
}