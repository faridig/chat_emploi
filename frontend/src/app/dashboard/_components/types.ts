// frontend/src/app/dashboard/_components/types.ts

export interface Application {
    id: string;
    laneId: string;
    company: string;
    role: string;
    date: string;
  }

  export interface Lane {
    id: string;
    title: string;
  }
