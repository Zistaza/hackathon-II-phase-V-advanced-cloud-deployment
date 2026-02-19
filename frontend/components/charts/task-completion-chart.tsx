'use client';

import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTheme } from '../../contexts/theme-context';
import { getChartColors } from '../../lib/chart-utils';
import { TaskCompletionData } from '../../lib/chart-utils';

interface TaskCompletionChartProps {
  data: TaskCompletionData[];
}

export const TaskCompletionChart: React.FC<TaskCompletionChartProps> = ({ data }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const colors = getChartColors(isDark);

  if (!data || data.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-muted-foreground text-sm">No completion data available</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={colors.primary} stopOpacity={0.3} />
            <stop offset="95%" stopColor={colors.primary} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
        <XAxis
          dataKey="date"
          stroke={colors.muted}
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke={colors.muted}
          style={{ fontSize: '12px' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: isDark ? '#1f2937' : '#ffffff',
            border: `1px solid ${colors.grid}`,
            borderRadius: '8px',
            color: colors.text,
          }}
        />
        <Area
          type="monotone"
          dataKey="completed"
          stroke={colors.primary}
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorCompleted)"
          name="Completed Tasks"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};
