/**
 * Theme Tokens Tests
 * 
 * Tests for theme token structure and values.
 * Component rendering tests are skipped due to react-dom dependency issues in Jest.
 */

import * as ThemeExports from '../src/shared/ui/theme';

describe('Theme Tokens', () => {
  describe('exports', () => {
    it('exports colors', () => {
      expect(ThemeExports.colors).toBeDefined();
    });

    it('exports spacing', () => {
      expect(ThemeExports.spacing).toBeDefined();
    });

    it('exports typography', () => {
      expect(ThemeExports.typography).toBeDefined();
    });

    it('exports borderRadius', () => {
      expect(ThemeExports.borderRadius).toBeDefined();
    });

    it('exports opacity', () => {
      expect(ThemeExports.opacity).toBeDefined();
    });

    it('exports theme object', () => {
      expect(ThemeExports.theme).toBeDefined();
    });
  });

  describe('colors', () => {
    it('has primary colors', () => {
      expect(ThemeExports.colors.primary).toBeDefined();
      expect(ThemeExports.colors.primary[500]).toBeDefined();
    });

    it('has secondary colors', () => {
      expect(ThemeExports.colors.secondary).toBeDefined();
      expect(ThemeExports.colors.secondary[500]).toBeDefined();
    });

    it('has error colors', () => {
      expect(ThemeExports.colors.error).toBeDefined();
      expect(ThemeExports.colors.error[500]).toBeDefined();
    });

    it('has success colors', () => {
      expect(ThemeExports.colors.success).toBeDefined();
      expect(ThemeExports.colors.success[500]).toBeDefined();
    });
  });

  describe('spacing', () => {
    it('has zero spacing', () => {
      expect(ThemeExports.spacing[0]).toBe(0);
    });

    it('has base unit of 4px', () => {
      expect(ThemeExports.spacing[1]).toBe(4);
      expect(ThemeExports.spacing[2]).toBe(8);
      expect(ThemeExports.spacing[4]).toBe(16);
    });

    it('has larger spacing values', () => {
      expect(ThemeExports.spacing[8]).toBe(32);
      expect(ThemeExports.spacing[16]).toBe(64);
    });
  });

  describe('typography', () => {
    it('has font families', () => {
      expect(ThemeExports.typography.fontFamily).toBeDefined();
    });

    it('has font sizes', () => {
      expect(ThemeExports.typography.fontSize).toBeDefined();
      expect(ThemeExports.typography.fontSize.md).toBe(16);
      expect(ThemeExports.typography.fontSize.xl).toBe(20);
    });

    it('has font weights', () => {
      expect(ThemeExports.typography.fontWeight).toBeDefined();
      expect(ThemeExports.typography.fontWeight.normal).toBe('400');
      expect(ThemeExports.typography.fontWeight.bold).toBe('700');
    });

    it('has line heights', () => {
      expect(ThemeExports.typography.lineHeight).toBeDefined();
      expect(ThemeExports.typography.lineHeight.md).toBe(22);
    });
  });

  describe('borderRadius', () => {
    it('has radius values', () => {
      expect(ThemeExports.borderRadius.none).toBe(0);
      expect(ThemeExports.borderRadius.sm).toBe(4);
      expect(ThemeExports.borderRadius.md).toBe(6);
      expect(ThemeExports.borderRadius.full).toBe(9999);
    });
  });

  describe('opacity', () => {
    it('has opacity values', () => {
      expect(ThemeExports.opacity[0]).toBe(0);
      expect(ThemeExports.opacity[50]).toBe(0.5);
      expect(ThemeExports.opacity[100]).toBe(1);
    });
  });
});
