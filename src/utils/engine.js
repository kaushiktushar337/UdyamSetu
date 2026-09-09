import { schemes } from '../data/schemes'
import { loanPlans } from '../data/loanPlans'

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

const normalizeCategory = (category) => String(category || '').trim().toLowerCase()

const categoryMap = {
  'dairy': 'dairy',
  'retail': 'retail',
  'food processing': 'food-processing',
  'textiles': 'textiles',
  'services': 'services',
  'agriculture-linked activity': 'agriculture',
}

export function normalizeProfile(profile = {}) {
  return {
    category: String(profile.category || 'Dairy'),
    projectCost: Number(profile.projectCost) || 0,
    monthlyIncome: Number(profile.monthlyIncome) || 0,
    loanAmount: Number(profile.loanAmount) || 0,
  }
}

export function calculateMatchScore(item, profile) {
  const base = normalizeProfile(profile)
  const hasAnyInput = base.category || base.projectCost > 0 || base.monthlyIncome > 0 || base.loanAmount > 0

  if (!hasAnyInput) {
    return 0
  }

  const optionType = item.type || 'scheme'
  const optionCategory = normalizeCategory(item.category || item.categoryType || base.category)
  const profileCategory = normalizeCategory(base.category)

  let score = 35

  if (optionCategory === categoryMap[profileCategory]) {
    score += 30
  } else if (optionType === 'loanPlan' && item.category === 'retail' && profileCategory === 'retail') {
    score += 24
  } else if (item.category === 'agriculture' && profileCategory === 'agriculture-linked activity') {
    score += 24
  } else {
    score += 7
  }

  if (base.projectCost > 0 && Number(item.maxProjectCost) >= base.projectCost) {
    score += 18
  } else if (base.projectCost > 0) {
    score += 3
  }

  if (base.loanAmount > 0 && Number(item.maxLoan) >= base.loanAmount) {
    score += 18
  } else if (base.loanAmount > 0) {
    score += 3
  }

  if (base.monthlyIncome > 0 && base.monthlyIncome >= 15000) {
    score += 8
  } else if (base.monthlyIncome > 0) {
    score += 2
  }

  if (base.loanAmount > 0 && base.projectCost > 0) {
    const loanToProject = base.loanAmount / base.projectCost
    if (loanToProject <= 0.9) score += 8
    else if (loanToProject <= 1) score += 4
  }

  if (item.interestRate) {
    if (item.interestRate <= 0.09) score += 4
    else score += 1
  }

  if (item.tenureYears >= 1 && item.tenureYears <= 8) {
    score += 4
  }

  return clamp(Math.round(score), 0, 99)
}

export function getRecommendations(profile, mode = 'scheme') {
  const pool = mode === 'loanPlan' ? loanPlans : schemes
  const normalized = normalizeProfile(profile)

  return pool
    .map((item) => ({
      ...item,
      type: mode === 'loanPlan' ? 'loanPlan' : 'scheme',
      matchScore: calculateMatchScore(item, normalized),
    }))
    .sort((a, b) => b.matchScore - a.matchScore)
}

export function getBestFit(profile, mode = 'scheme') {
  const recommendations = getRecommendations(profile, mode)
  return recommendations[0] || null
}

export function getDecision(profile, mode = 'scheme') {
  const options = getRecommendations(profile, mode)
  const best = options[0] || null

  return {
    mode,
    totalMatches: options.length,
    recommendations: options,
    bestFit: best,
    generatedAt: new Date().toISOString(),
  }
}
