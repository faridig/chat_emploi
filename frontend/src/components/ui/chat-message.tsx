import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Card } from "./card"

const chatMessageVariants = cva(
  "flex w-full gap-4 p-4",
  {
    variants: {
      role: {
        user: "flex-row-reverse",
        agent: "flex-row",
      },
    },
    defaultVariants: {
      role: "agent",
    },
  }
)

const bubbleVariants = cva(
  "rounded-2xl px-4 py-3 text-sm shadow-sm",
  {
    variants: {
      role: {
        user: "bg-primary text-primary-foreground rounded-tr-sm",
        agent: "bg-white border border-[#E2E8F0] text-foreground rounded-tl-sm",
      },
    },
    defaultVariants: {
      role: "agent",
    },
  }
)

export interface ChatMessageProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof chatMessageVariants> {
  avatar?: React.ReactNode
  content: string | React.ReactNode
  timestamp?: string
}

const ChatMessage = React.forwardRef<HTMLDivElement, ChatMessageProps>(
  ({ className, role, avatar, content, timestamp, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(chatMessageVariants({ role, className }))}
        {...props}
      >
        {avatar && (
          <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full bg-muted">
            {avatar}
          </div>
        )}
        <div className={cn("flex max-w-[80%] flex-col gap-1")}>
          <div className={cn(bubbleVariants({ role }))}>
            {content}
          </div>
          {timestamp && (
            <span className="px-1 text-[10px] text-muted-foreground">
              {timestamp}
            </span>
          )}
        </div>
      </div>
    )
  }
)
ChatMessage.displayName = "ChatMessage"

export { ChatMessage, chatMessageVariants }
