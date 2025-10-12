import { describe, it, expect } from 'vitest';
import {
  formatPrice,
  formatTime,
  formatTimeLocale,
  formatVolume,
  formatStrength,
  formatPercentageChange,
  formatNumberWithCommas,
  safeNumber,
} from '../src/utils/format';

describe('utils/format', () => {
  describe('formatPrice', () => {
    it('handles undefined/null/NaN', () => {
      expect(formatPrice(undefined)).toBe('0.0000');
      expect(formatPrice(null as any)).toBe('0.0000');
      expect(formatPrice('abc' as any)).toBe('0.0000');
      expect(formatPrice(NaN as any)).toBe('0.0000');
    });

    it('applies precision by magnitude', () => {
      expect(formatPrice(0.1234567)).toBe('0.123457');
      expect(formatPrice(1.234567)).toBe('1.2346');
      expect(formatPrice(1234.567)).toBe('1234.57');
    });

    it('rejects negative as 0.0000', () => {
      expect(formatPrice(-1)).toBe('0.0000');
    });
  });

  describe('formatTime', () => {
    it('handles invalid inputs', () => {
      expect(formatTime(undefined as any)).toBe('--:--');
      expect(formatTime(null as any)).toBe('--:--');
      expect(formatTime('abc' as any)).toBe('--:--');
      expect(formatTime(-1 as any)).toBe('--:--');
    });

    it('formats by mode', () => {
      const ts = Date.UTC(2020, 0, 2, 3, 4); // Jan 2 2020 03:04 UTC
      expect(formatTime(ts, 'time')).toMatch(/03:04|\d{2}:\d{2}/);
      expect(formatTime(ts, 'date')).toMatch(/01\/02|\d{2}\/\d{2}/);
      expect(formatTime(ts, 'datetime')).toMatch(/01\/02 .*\d{2}:\d{2}/);
    });
  });

  describe('formatTimeLocale', () => {
    it('handles invalid', () => {
      expect(formatTimeLocale(undefined as any)).toBe('--:--');
    });
  });

  describe('formatVolume', () => {
    it('handles invalid and negative', () => {
      expect(formatVolume(undefined as any)).toBe('0');
      expect(formatVolume(null as any)).toBe('0');
      expect(formatVolume('abc' as any)).toBe('0');
      expect(formatVolume(-1 as any)).toBe('0');
    });

    it('scales units', () => {
      expect(formatVolume(999)).toBe('999');
      expect(formatVolume(1500)).toBe('1.5K');
      expect(formatVolume(2_500_000)).toBe('2.5M');
      expect(formatVolume(3_400_000_000)).toBe('3.4B');
    });
  });

  describe('formatStrength', () => {
    it('handles invalid and clamps 0..1', () => {
      expect(formatStrength(undefined as any)).toBe('0.0%');
      expect(formatStrength(null as any)).toBe('0.0%');
      expect(formatStrength('abc' as any)).toBe('0.0%');
      expect(formatStrength(-2)).toBe('100.0%');
      expect(formatStrength(2)).toBe('100.0%');
      expect(formatStrength(0.4567)).toBe('45.7%');
    });
  });

  describe('formatPercentageChange', () => {
    it('handles invalid and zero base', () => {
      expect(formatPercentageChange(undefined as any, 1)).toBe('0.00%');
      expect(formatPercentageChange(1, undefined as any)).toBe('0.00%');
      expect(formatPercentageChange('abc' as any, 1)).toBe('0.00%');
      expect(formatPercentageChange(1, 'abc' as any)).toBe('0.00%');
      expect(formatPercentageChange(1, 0)).toBe('0.00%');
    });

    it('computes percent with sign', () => {
      expect(formatPercentageChange(2, 4)).toBe('+50.00%');
      expect(formatPercentageChange(-1, 2)).toBe('-50.00%');
    });
  });

  describe('formatNumberWithCommas', () => {
    it('handles invalid', () => {
      expect(formatNumberWithCommas(undefined as any)).toBe('0');
      expect(formatNumberWithCommas('abc' as any)).toBe('0');
    });

    it('respects decimals bounds [0,10]', () => {
      expect(formatNumberWithCommas(1234.567, 0)).toBe('1,235');
      expect(formatNumberWithCommas(1234.567, 2)).toBe('1,234.57');
      expect(formatNumberWithCommas(1234.567, 20)).toBe('1,234.5670000000');
    });
  });

  describe('safeNumber', () => {
    it('converts safely', () => {
      expect(safeNumber('123.45')).toBeCloseTo(123.45);
      expect(safeNumber('abc', 7)).toBe(7);
      expect(safeNumber(undefined, 9)).toBe(9);
    });
  });
});