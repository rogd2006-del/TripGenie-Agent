import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const GlassCard = ({ children, className = '', hover = true, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={twMerge(
        clsx(
          'glass-card rounded-2xl p-6 relative overflow-hidden transition-all duration-300',
          hover && 'glass-card-hover cursor-pointer',
          className
        )
      )}
    >
      {children}
    </div>
  );
};
