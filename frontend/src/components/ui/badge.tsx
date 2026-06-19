import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500/20",
  {
    variants: {
      variant: {
        default: "bg-primary-50 text-primary-700 ring-1 ring-inset ring-primary-600/20",
        secondary: "bg-gray-50 text-gray-700 ring-1 ring-inset ring-gray-600/20",
        success: "bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20",
        warning: "bg-yellow-50 text-yellow-700 ring-1 ring-inset ring-yellow-600/20",
        danger: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20",
        info: "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20",
        accent: "bg-accent-50 text-accent-700 ring-1 ring-inset ring-accent-600/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
