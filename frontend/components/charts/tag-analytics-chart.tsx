'use client';

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTheme } from '../../contexts/theme-context';
import { getChartColors } from '../../lib/chart-utils';
import { TagAnalytics } from '../../lib/chart-utils';

interface TagAnalyticsChartProps {
  data: TagAnalytics[];
}

export const TagAnalyticsChart: React.FC<TagAnalyticsChartProps> = ({ data }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const colors = getChartColors(isDark);

  if (!data || data.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-muted-foreground text-sm">No tag data available</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
        <XAxis
          type="number"
          stroke={colors.muted}
          style={{ fontSize: '12px' }}
        />
        <YAxis
          type="category"
          dataKey="tag"
          stroke={colors.muted}
          style={{ fontSize: '12px' }}
          width={80}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: isDark ? '#1f2937' : '#ffffff',
            border: `1px solid ${colors.grid}`,
            borderRadius: '8px',
            color: colors.text,
          }}
        />
        <Bar
          dataKey="count"
          fill={colors.primary}
          radius={[0, 4, 4, 0]}
          name="Usage Count"
        />
      </BarChart>
    </ResponsiveContainer>
  );
};
