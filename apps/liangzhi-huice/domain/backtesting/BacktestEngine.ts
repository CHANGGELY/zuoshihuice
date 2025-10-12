// 回测引擎

export interface Bar {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export class BacktestEngine {
  private _bars: Bar[] = [];
  private _currentIndex: number = 0;

  constructor(bars: Bar[]) {
    this._bars = bars;
  }

  get currentBar(): Bar | undefined {
    return this._bars[this._currentIndex];
  }

  get currentIndex(): number {
    return this._currentIndex;
  }

  get totalBars(): number {
    return this._bars.length;
  }

  next(): boolean {
    if (this._currentIndex < this._bars.length - 1) {
      this._currentIndex++;
      return true;
    }
    return false;
  }

  reset(): void {
    this._currentIndex = 0;
  }

  getBars(count: number): Bar[] {
    const start = Math.max(0, this._currentIndex - count + 1);
    return this._bars.slice(start, this._currentIndex + 1);
  }
}