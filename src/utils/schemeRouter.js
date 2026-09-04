import { schemes } from '../data/schemes'

export function routeScheme(projectCost) {
  if (projectCost <= schemes[0].maxProjectCost) return schemes[0]
  if (projectCost <= schemes[1].maxProjectCost) return schemes[1]
  return null
}

export function calculateStructure(margin) {
  const availableMargin = Number(margin) || 0
  const theoreticalProjectCost = availableMargin / 0.10
  const loanBeforeCap = theoreticalProjectCost * 0.90
  const scheme = routeScheme(theoreticalProjectCost)

  if (!scheme) {
    const cappedProjectCost = schemes[1].maxProjectCost
    const loanAmount = schemes[1].maxLoan
    const requiredMargin = cappedProjectCost - loanAmount
    return {
      theoreticalProjectCost,
      loanAmount,
      requiredMargin,
      scheme: schemes[1],
      capped: true,
      loanPercent: 90,
    }
  }

  const loanAmount = Math.min(loanBeforeCap, scheme.maxLoan)

  return {
    theoreticalProjectCost,
    loanAmount,
    requiredMargin: theoreticalProjectCost <= scheme.maxProjectCost ? availableMargin : theoreticalProjectCost - loanAmount,
    scheme,
    capped: loanBeforeCap > scheme.maxLoan,
    loanPercent: Math.round((loanAmount / theoreticalProjectCost) * 100),
  }
}
