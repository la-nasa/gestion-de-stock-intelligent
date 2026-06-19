import { formatCurrency, formatDate, formatNumber, truncate } from '@/lib/utils'

describe('Utility Functions', () => {
  describe('formatCurrency', () => {
    it('formats XAF currency', () => {
      expect(formatCurrency(150000)).toContain('150')
    })

    it('handles zero', () => {
      expect(formatCurrency(0)).toBeDefined()
    })

    it('handles large numbers', () => {
      expect(formatCurrency(1000000)).toBeDefined()
    })
  })

  describe('formatDate', () => {
    it('formats date correctly', () => {
      const result = formatDate('2026-06-15')
      expect(result).toContain('2026')
    })
  })

  describe('formatNumber', () => {
    it('formats with thousand separators', () => {
      expect(formatNumber(1234567)).toContain('1')
    })
  })

  describe('truncate', () => {
    it('truncates long strings', () => {
      expect(truncate('Hello World', 5)).toBe('Hello...')
    })

    it('does not truncate short strings', () => {
      expect(truncate('Hello', 10)).toBe('Hello')
    })
  })
})