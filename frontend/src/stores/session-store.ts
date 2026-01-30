import { create } from 'zustand';

export type Message = {
  id: number;
  role: 'user' | 'agent';
  content: string | React.ReactNode;
};

export interface SessionState {
  messages: Message[];
  isLoading: boolean;
  currentStepId: string;
  addMessage: (role: 'user' | 'agent', content: string | React.ReactNode) => void;
  setIsLoading: (loading: boolean) => void;
  // TODO: Add more actions to manage CV data, offers, etc.
}

export const useSessionStore = create<SessionState>((set) => ({
  messages: [
    {
      id: 1,
      role: 'agent',
      content: "Bonjour ! Je suis Alex, votre coach emploi. J'ai analysé votre CV. Pour commencer, parlez-moi un peu de votre situation actuelle et de ce que vous recherchez."
    }
  ],
  isLoading: false,
  currentStepId: 'profile', // Corresponds à une Step['id']
  addMessage: (role, content) =>
    set((state) => ({
      messages: [...state.messages, { id: state.messages.length + 1, role, content }],
    })),
  setIsLoading: (loading) => set({ isLoading: loading }),
}));
