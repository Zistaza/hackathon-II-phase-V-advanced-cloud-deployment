'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
  loading?: boolean;
  error?: string | null;
  emptyMessage?: string;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  children,
  loading = false,
  error = null,
  emptyMessage = 'No data available',
  className = '',
}) => {
  return (
    <Card className={`transition-shadow duration-200 hover:shadow-lg ${className}`}>
      <CardHeader className="p-6 pb-4">
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-6 pt-2">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="h-8 w-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
        ) : error ? (
          <div className="flex flex-col justify-center items-center h-64 text-center">
            <p className="text-destructive text-sm mb-2">Error loading chart</p>
            <p className="text-muted-foreground text-xs">{error}</p>
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
};
