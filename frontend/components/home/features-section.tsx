'use client';

import React from 'react';
import { motion } from 'framer-motion';
import FeatureCard from '@/components/ui/feature-card';
import { FiCheckCircle, FiLock, FiCloud, FiZap } from 'react-icons/fi';

const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: 'Task Management',
      description: 'Intuitive interface to create, organize, and track your tasks with due dates and priorities.',
      icon: <FiCheckCircle className="h-8 w-8" aria-hidden="true" />,
    },
    {
      title: 'Secure Login',
      description: 'Enterprise-grade authentication with secure storage of your personal data and privacy protection.',
      icon: <FiLock className="h-8 w-8" aria-hidden="true" />,
    },
    {
      title: 'Cloud Sync',
      description: 'Access your tasks from anywhere, with real-time synchronization across all your devices.',
      icon: <FiCloud className="h-8 w-8" aria-hidden="true" />,
    },
    {
      title: 'Fast & Responsive',
      description: 'Lightning-fast performance with smooth animations and a responsive design that works on all devices.',
      icon: <FiZap className="h-8 w-8" aria-hidden="true" />,
    },
  ];

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-6xl relative"
      aria-labelledby="features-heading"
    >
      <div className="text-center mb-12 relative">
        {/* Title separator */}
        <div className="inline-block mb-6">
          <div className="w-20 h-2 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
        </div>

        <h2
          id="features-heading"
          className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-6"
        >
          Powerful Features
        </h2>

        <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto">
          Everything you need to stay organized and boost your productivity
        </p>
      </div>

      <div
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8"
        role="list"
        aria-label="Application features"
      >
        {features.map((feature, index) => (
          <div key={index}>
            <FeatureCard
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              index={index}
            />
          </div>
        ))}
      </div>
    </motion.section>
  );
};

export default FeaturesSection;