import { PlaywrightTestOptions } from '@playwright/test';

declare module '@playwright/test' {
  interface PlaywrightTestOptions {
    persona?: string;
  }
}
