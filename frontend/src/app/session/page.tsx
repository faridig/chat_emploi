import { ChatPanel } from "@/components/feature/chat-panel";
import { ContextPanel } from "@/components/feature/context-panel";

export default function SessionPage() {
  return (
    <div className="grid h-full grid-cols-1 md:grid-cols-3">
      <div className="col-span-2 h-full">
        <ChatPanel />
      </div>
      <div className="hidden h-full md:block">
        <ContextPanel />
      </div>
    </div>
  )
}
