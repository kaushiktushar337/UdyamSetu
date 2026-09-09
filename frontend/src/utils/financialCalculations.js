export function calculateEMI(principal, annualRate, tenureYears) {
  if (!principal || principal <= 0 || tenureYears <= 0) return 0
  const monthlyRate = annualRate / 12
  const months = tenureYears * 12

  if (monthlyRate === 0) {
    return Math.round(principal / months)
  }

  const emi =
    principal *
    monthlyRate *
    Math.pow(1 + monthlyRate, months) /
    (Math.pow(1 + monthlyRate, months) - 1)

  return Math.round(emi)
}
