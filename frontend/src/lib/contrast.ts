/**
 * WCAG 2.1 Contrast Ratio Calculator
 */

function parseColorToRgb(hex: string): [number, number, number] {
  let cleanHex = hex.replace('#', '').trim();
  if (cleanHex.length === 3) {
    cleanHex = cleanHex
      .split('')
      .map((c) => c + c)
      .join('');
  }
  if (cleanHex.length !== 6) return [0, 0, 0];

  const num = parseInt(cleanHex, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

function getChannelLuminance(channel: number): number {
  const c = channel / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

export function getLuminance(hex: string): number {
  const [r, g, b] = parseColorToRgb(hex);
  return (
    0.2126 * getChannelLuminance(r) +
    0.7152 * getChannelLuminance(g) +
    0.0722 * getChannelLuminance(b)
  );
}

export function getContrastRatio(hex1: string, hex2: string): number {
  const lum1 = getLuminance(hex1);
  const lum2 = getLuminance(hex2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return Number(((lighter + 0.05) / (darker + 0.05)).toFixed(2));
}

export function evaluateWcag(ratio: number): {
  ratio: number;
  normalAa: boolean;
  largeAa: boolean;
  ratingText: string;
} {
  const normalAa = ratio >= 4.5;
  const largeAa = ratio >= 3.0;

  let ratingText = 'Fails WCAG';
  if (ratio >= 7.0) ratingText = 'AAA Compliant (7:1+)';
  else if (ratio >= 4.5) ratingText = 'AA Compliant (4.5:1+)';
  else if (ratio >= 3.0) ratingText = 'Large Text Only (3:1+)';

  return { ratio, normalAa, largeAa, ratingText };
}
