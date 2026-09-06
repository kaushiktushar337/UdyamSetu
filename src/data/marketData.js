export const marketData = {
  population: 25420,
  households: 4240,
  avgMonthlyIncome: 9850,
  potential: 'High',
  existingBusinesses: 12,
  saturation: 48,
  demand: 'High',
  topOpportunities: ['Packaged Milk', 'Paneer & Curd', 'Ghee & Butter', 'Flavoured Milk'],
}

const categoryAdjustments = {
  Dairy: {
    demand: 'High',
    potential: 'High',
    topOpportunities: ['Packaged Milk', 'Paneer & Curd', 'Ghee & Butter', 'Flavoured Milk'],
  },
  Retail: {
    population: 25420,
    avgMonthlyIncome: 9850,
    existingBusinesses: 18,
    saturation: 62,
    demand: 'Medium',
    potential: 'Medium',
    topOpportunities: ['Farm Essentials', 'Mobile Accessories', 'Household Supplies', 'School Goods'],
  },
  'Food Processing': {
    population: 25420,
    avgMonthlyIncome: 9850,
    existingBusinesses: 8,
    saturation: 36,
    demand: 'High',
    potential: 'High',
    topOpportunities: ['Spice Blends', 'Millet Snacks', 'Pickles & Preserves', 'Local Flour'],
  },
  Textiles: {
    population: 25420,
    avgMonthlyIncome: 9850,
    existingBusinesses: 10,
    saturation: 43,
    demand: 'Medium',
    potential: 'Medium',
    topOpportunities: ['School Uniforms', 'Alterations', 'Workwear', 'Home Furnishings'],
  },
  Services: {
    population: 25420,
    avgMonthlyIncome: 9850,
    existingBusinesses: 14,
    saturation: 51,
    demand: 'High',
    potential: 'Medium',
    topOpportunities: ['Digital Services', 'Repair Centre', 'Parcel Point', 'Beauty Services'],
  },
}

export function getMarketData(filters) {
  const adjustment = categoryAdjustments[filters.category] ?? categoryAdjustments.Dairy
  const locationFactor = filters.district === 'Other' || filters.block === 'Other' ? 0.92 : 1

  return {
    ...marketData,
    ...adjustment,
    population: Math.round((adjustment.population ?? marketData.population) * locationFactor),
    households: Math.round(marketData.households * locationFactor),
    avgMonthlyIncome: Math.round((adjustment.avgMonthlyIncome ?? marketData.avgMonthlyIncome) * locationFactor),
  }
}
