'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useSessionStore } from '@/stores/session-store';
import { ChatMessage } from '@/components/ui/chat-message';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send } from 'lucide-react';

const QUICK_ACTIONS = [
  "Je suis en reconversion",
  "Je cherche mon premier emploi",
  "Je veux évoluer dans mon domaine"
];

export function ChatPanel() {
  const { messages, isLoading, addMessage } = useSessionStore();
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      addMessage('user', input);
      setInput('');
      // TODO: Trigger backend call
    }
  };

  const handleQuickAction = (text: string) => {
    addMessage('user', text);
    // TODO: Trigger backend call
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full flex-col" data-testid="chat-panel">
      {/* Message List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4">
        <div className="flex flex-col gap-4">
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              // avatar={msg.role === 'agent' ? <Sparkles /> : undefined}
            />
          ))}
          {isLoading && (
            <ChatMessage
              role="agent"
              content={<div className="flex items-center gap-2">Réflexion en cours... <div className="h-2 w-2 animate-pulse rounded-full bg-primary" /></div>}
            />
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="mb-4 flex flex-wrap gap-2">
          {QUICK_ACTIONS.map(action => (
            <Button key={action} variant="outline" size="sm" onClick={() => handleQuickAction(action)}>
              {action}
            </Button>
          ))}
        </div>
        <div className="relative">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Je recherche un poste de..."
            className="pr-12"
            rows={2}
          />
          <Button
            size="icon"
            className="absolute bottom-2 right-2"
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            aria-label="Envoyer"
          >
            <Send />
          </Button>
        </div>
      </div>
    </div>
  );
}
