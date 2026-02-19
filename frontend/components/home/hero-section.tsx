'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import AnimatedButton from '@/components/ui/animated-button';

const HeroSection: React.FC = () => {
  const router = useRouter();

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-5xl text-center"
      aria-labelledby="hero-title"
    >
      <header className="relative mb-12">
        {/* Title separator */}
        <div className="inline-block mb-8">
          <div className="w-32 h-1.5 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
        </div>

        {/* Main headline */}
        <div className="mb-8">
          <h1
            id="hero-title"
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold mb-6 leading-tight"
          >
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent inline-block font-extrabold">
              STREAMLINE
            </span>
            <br />
            <span className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent inline-block mt-2 font-extrabold">
              YOUR TASKS
            </span>
          </h1>
        </div>

        {/* Subtitle */}
        <div className="flex justify-center px-4 mb-8">
          <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-3xl text-center">
            A powerful, intuitive todo application designed to boost your productivity and help you achieve your goals.
          </p>
        </div>

        {/* Call to action buttons */}
        <div
          className="flex flex-col sm:flex-row gap-6 justify-center items-center px-4"
          role="group"
          aria-label="Authentication options"
        >
          <AnimatedButton
            variant="primary"
            size="lg"
            onClick={() => router.push('/register')}
            className="px-10 py-5 text-lg font-semibold rounded-xl min-w-[200px]"
            aria-label="Get started with registration"
          >
            Get Started
          </AnimatedButton>

          <AnimatedButton
            variant="secondary"
            size="lg"
            onClick={() => router.push('/login')}
            className="px-10 py-5 text-lg font-semibold rounded-xl min-w-[200px]"
            aria-label="Sign in to your account"
          >
            Sign In
          </AnimatedButton>
        </div>
      </header>
    </motion.section>
  );
};

export default HeroSection;