export {};

declare module '@config/default.js' {
  export const DEFAULT_CONFIG: {
    backtest: {
      defaultEndMonthsBack: number;
      maxConcurrentBacktests: number;
      timeoutMinutes: number;
    };
    data: {
      h5FilePath: string;
      h5BackupPath: string;
      cacheSize: number;
      expectedColumns: string[];
    };
    server: {
      port: number;
      cors: {
        origin: string[];
        credentials: boolean;
      };
    };
  };
}

declare module '*.js' {
  export const DEFAULT_CONFIG: {
    backtest: {
      defaultEndMonthsBack: number;
      maxConcurrentBacktests: number;
      timeoutMinutes: number;
    };
    data: {
      h5FilePath: string;
      h5BackupPath: string;
      cacheSize: number;
      expectedColumns: string[];
    };
    server: {
      port: number;
      cors: {
        origin: string[];
        credentials: boolean;
      };
    };
  };
}