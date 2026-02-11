'use client';

import React, { InputHTMLAttributes, TextareaHTMLAttributes } from 'react';

type BaseProps = {
  label?: string;
  error?: string;
  className?: string;
};

// Discriminated union for input vs textarea
type InputProps =
  | (BaseProps & InputHTMLAttributes<HTMLInputElement> & { as?: 'input' })
  | (BaseProps & TextareaHTMLAttributes<HTMLTextAreaElement> & { as: 'textarea'; rows?: number });

export const Input: React.FC<InputProps> = (props) => {
  const { label, error, className = '' } = props;

  // If textarea
  if (props.as === 'textarea') {
    const { rows = 3, ...textareaProps } = props;
    return (
      <div className="flex flex-col space-y-1 w-full">
        {label && (
          <label htmlFor={textareaProps.id} className="text-sm font-medium text-foreground">
            {label}
          </label>
        )}
        <textarea
          {...textareaProps}
          rows={rows}
          className={`flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring
            ${error ? 'border-destructive' : 'border-input'}
            ${className}`}
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
      </div>
    );
  }

  // Default: input
  const { as, ...inputProps } = props; // omit 'as'
  return (
    <div className="flex flex-col space-y-1 w-full">
      {label && (
        <label htmlFor={inputProps.id} className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <input
        {...inputProps}
        className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring
          ${error ? 'border-destructive' : 'border-input'}
          ${className}`}
      />
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
};
