import * as React from "react"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

export type StepStatus = "pending" | "current" | "completed"

export interface Step {
  id: string
  label: string
  status?: StepStatus
}

export interface TimelineProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  steps: Step[]
  currentStepId?: string
}

const TimelineProgress = React.forwardRef<HTMLDivElement, TimelineProgressProps>(
  ({ className, steps, currentStepId, ...props }, ref) => {
    // Calculate status dynamically if currentStepId is provided
    const derivedSteps = steps.map((step, index) => {
      if (step.status) return step

      const currentIndex = steps.findIndex((s) => s.id === currentStepId)
      let status: StepStatus = "pending"
      if (index < currentIndex) status = "completed"
      else if (index === currentIndex) status = "current"

      return { ...step, status }
    })

    return (
      <div
        ref={ref}
        className={cn("relative flex w-full items-center justify-between", className)}
        {...props}
      >
        {/* Ligne de fond */}
        <div className="absolute left-0 top-1/2 -z-10 h-0.5 w-full bg-border" />

        {/* Ligne de progression (animée plus tard si besoin) */}
        {/* Note: Pour une ligne remplie, il faudrait calculer la width en JS ou utiliser des segments */}

        {derivedSteps.map((step, index) => (
          <div key={step.id} className="group relative flex flex-col items-center">
            {/* Connecteur gauche (sauf premier) */}
            {index > 0 && (
              <div
                className={cn(
                  "absolute right-[50%] top-[10px] -z-10 h-0.5 w-[calc(100vw/6)] -translate-y-1/2",
                  // Simplification visuelle : la ligne est colorée si l'étape est completed ou current
                  step.status === "completed" || step.status === "current"
                    ? "bg-primary"
                    : "bg-border"
                )}
                style={{ width: "100%" }}
              />
            )}

            {/* Cercle */}
            <div
              className={cn(
                "flex h-5 w-5 items-center justify-center rounded-full border-2 bg-background transition-colors duration-300",
                step.status === "completed" && "border-primary bg-primary text-primary-foreground",
                step.status === "current" && "border-primary ring-4 ring-primary/20",
                step.status === "pending" && "border-muted-foreground/30"
              )}
            >
              {step.status === "completed" && <Check className="h-3 w-3" />}
              {step.status === "current" && <div className="h-2 w-2 rounded-full bg-primary" />}
            </div>

            {/* Label */}
            <span
              className={cn(
                "absolute top-7 whitespace-nowrap text-xs font-medium transition-colors",
                step.status === "completed" && "text-primary",
                step.status === "current" && "text-primary font-bold",
                step.status === "pending" && "text-muted-foreground"
              )}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>
    )
  }
)
TimelineProgress.displayName = "TimelineProgress"

export { TimelineProgress }
