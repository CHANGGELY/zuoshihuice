import argparse
import csv
import os
import sys
from typing import Optional

import h5py


def find_2d_dataset(f: h5py.File) -> Optional[str]:
    """
    Recursively find the first 2D dataset with at least 6 columns.
    Returns the dataset path or None.
    """
    found: Optional[str] = None

    def visitor(name, obj):
        nonlocal found
        if found is not None:
            return
        if isinstance(obj, h5py.Dataset):
            try:
                if obj.ndim == 2 and obj.shape[1] >= 6:
                    found = name
            except Exception:
                pass

    f.visititems(visitor)
    return found


def main():
    parser = argparse.ArgumentParser(description="Export first N rows from H5 to CSV")
    parser.add_argument("-i", "--input", required=True, help="Path to input .h5 file")
    parser.add_argument("-o", "--output", required=True, help="Path to output .csv file")
    parser.add_argument("-n", "--rows", type=int, default=100, help="Number of rows to export (default: 100)")
    args = parser.parse_args()

    in_path = os.path.abspath(args.input)
    out_path = os.path.abspath(args.output)

    if not os.path.exists(in_path):
        print(f"Input file not found: {in_path}")
        sys.exit(1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with h5py.File(in_path, "r") as f:
        dset = None
        dset_path = None

        # Prefer '/kline_data' if present and valid
        if "kline_data" in f:
            maybe = f["kline_data"]
            if isinstance(maybe, h5py.Dataset) and getattr(maybe, "ndim", 0) == 2:
                dset = maybe
                dset_path = "/kline_data"

        # Fallback: find any 2D dataset
        if dset is None:
            path = find_2d_dataset(f)
            if path is not None:
                dset = f[path]
                dset_path = f"/{path}" if not path.startswith("/") else path

        if dset is None:
            print("No suitable 2D dataset (>=6 columns) found in the H5 file.")
            sys.exit(2)

        n_rows = min(args.rows, dset.shape[0])
        # Slice the first N rows
        data = dset[:n_rows]

        if data.ndim != 2 or data.shape[1] < 6:
            print(f"Dataset {dset_path} is not 2D with at least 6 columns. Shape: {data.shape}")
            sys.exit(3)

        cols = data.shape[1]
        headers = ["timestamp", "open", "high", "low", "close", "volume"]
        if cols >= 7:
            headers.append("turnover")
        # Any extra columns (if exist)
        if cols > len(headers):
            for c in range(len(headers), cols):
                headers.append(f"col{c+1}")

        with open(out_path, "w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow(headers)
            for i in range(n_rows):
                row = data[i]
                # Convert to native Python types for CSV writer
                writer.writerow([x.item() if hasattr(x, "item") else x for x in row])

    print(f"Exported {n_rows} rows from {dset_path} to CSV: {out_path}")


if __name__ == "__main__":
    main()