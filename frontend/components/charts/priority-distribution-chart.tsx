'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useTheme } from '../../contexts/theme-context';
import { getChartColors } from '../../lib/chart-utils';
import { PriorityDistribution } from '../../lib/chart-utils';

interface PriorityDistributionChartProps {
  data: PriorityDistribution[];
}

const PRIORITY_COLORS = {
  Urgent: '#ef4444',
  High: '#f59e0b',
  Medium: '#f59e0b',
  Low: '#10b981',
};

export const PriorityDistributionChart: React.FC<PriorityDistributionChartProps> = ({ data }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const colors = getChartColors(isDark);

  if (!data || data.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-muted-foreground text-sm">No priority data available</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          fill={colors.primary}
          paddingAngle={5}
          dataKey="count"
          label={({ priority, percentage }) => `${priority}: ${percentage}%`}
          labelLine={false}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={PRIORITY_COLORS[entry.priority as keyof typeof PRIORITY_COLORS] || colors.primary}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: isDark ? '#1f2937' : '#ffffff',
            border: `1px solid ${colors.grid}`,
            borderRadius: '8px',
            color: colors.text,
          }}
        />
        <Legend
          verticalAlign="bottom"
          height={36}
          wrapperStyle={{ fontSize: '12px', color: colors.text }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};
