import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency: string = "XAF"): string {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date))
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat("fr-FR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date))
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("fr-FR").format(num)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + "..."
}

export function getInitials(firstName: string, lastName: string): string {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

export function classNames(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ")
}

export const stockStatusConfig = {
  normal: { label: "Normal", color: "bg-green-50 text-green-700 ring-green-600/20" },
  low_stock: { label: "Stock bas", color: "bg-yellow-50 text-yellow-700 ring-yellow-600/20" },
  out_of_stock: { label: "Rupture", color: "bg-red-50 text-red-700 ring-red-600/20" },
  overstocked: { label: "Surstock", color: "bg-blue-50 text-blue-700 ring-blue-600/20" },
}

export const orderStatusConfig = {
  DRAFT: { label: "Brouillon", color: "bg-gray-50 text-gray-700 ring-gray-600/20" },
  PENDING: { label: "En attente", color: "bg-yellow-50 text-yellow-700 ring-yellow-600/20" },
  APPROVED: { label: "Approuvée", color: "bg-green-50 text-green-700 ring-green-600/20" },
  ORDERED: { label: "Commandée", color: "bg-blue-50 text-blue-700 ring-blue-600/20" },
  RECEIVED: { label: "Reçue", color: "bg-emerald-50 text-emerald-700 ring-emerald-600/20" },
  CANCELLED: { label: "Annulée", color: "bg-red-50 text-red-700 ring-red-600/20" },
}
