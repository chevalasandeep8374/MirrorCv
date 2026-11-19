'use client';

import React from 'react';
import Link from 'next/link';

interface MirrorCvLogoProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  variant?: 'dark' | 'light';
  asLink?: boolean;
  href?: string;
  className?: string;
}

export const MirrorCvSymbol: React.FC<{
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'dark' | 'light';
  className?: string;
}> = ({ size = 'sm', variant = 'dark', className = '' }) => {
  const sizeMap = {
    xs: { width: 14, height: 17 },
    sm: { width: 18, height: 21 },
    md: { width: 24, height: 28 },
    lg: { width: 30, height: 36 },
    xl: { width: 40, height: 48 },
  };

  const dim = sizeMap[size] || sizeMap.sm;
  const silhouetteColor = variant === 'light' ? '#FFFFFF' : '#1D0F3A';
  const reflectionColor = '#E8456B';

  return (
    <svg
      width={dim.width}
      height={dim.height}
      viewBox="0 0 74 88"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`shrink-0 transition-transform duration-200 ${className}`}
      aria-hidden="true"
    >
      <g id="MirrorCV symbol">
        <path
          id="Folded mirror silhouette"
          d="M8.75 0H43.75L73.5 29.75V78.75C73.5 84.5833 70.5833 87.5 64.75 87.5H8.75C2.91667 87.5 0 84.5833 0 78.75V8.75C0 2.91667 2.91667 0 8.75 0ZM49 11.375V24.5H62.125L49 11.375Z"
          fill={silhouetteColor}
          fillRule="evenodd"
          clipRule="evenodd"
        />
        <path
          id="Coral reflection"
          d="M20.125 51.1875L33.25 38.0625"
          stroke={reflectionColor}
          strokeWidth="8.75"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
};

export const MirrorCvLogo: React.FC<MirrorCvLogoProps> = ({
  size = 'sm',
  showText = true,
  variant = 'dark',
  asLink = false,
  href = '/',
  className = '',
}) => {
  const textClasses = {
    xs: 'text-xs tracking-[-0.3px]',
    sm: 'text-sm sm:text-[15px] tracking-[-0.45px]',
    md: 'text-base sm:text-lg tracking-[-0.6px]',
    lg: 'text-xl sm:text-2xl tracking-[-0.8px]',
    xl: 'text-2xl sm:text-3xl tracking-[-1.2px]',
  };

  const textColor = variant === 'light' ? 'text-white' : 'text-[#1D0F3A]';

  const content = (
    <div className={`inline-flex items-center gap-2 select-none group ${className}`}>
      <MirrorCvSymbol
        size={size}
        variant={variant}
        className="group-hover:scale-105 transition-transform"
      />
      {showText && (
        <span
          className={`font-bold font-sans ${textClasses[size]} ${textColor} leading-none`}
        >
          MirrorCv
        </span>
      )}
    </div>
  );

  if (asLink) {
    return (
      <Link href={href} className="inline-flex items-center focus:outline-none">
        {content}
      </Link>
    );
  }

  return content;
};
