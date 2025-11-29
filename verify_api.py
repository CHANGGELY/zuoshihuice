import urllib.request
import json
import sys

try:
    # 不带时间范围，默认取最近的
    url = "http://localhost:8001/api/kline/range?limit=5"
    with urllib.request.urlopen(url) as response:
        body = response.read().decode()
        try:
            data = json.loads(body)
            if isinstance(data, list):
                with open("verify_result.txt", "w") as f:
                    f.write(f"SUCCESS: Received {len(data)} records.\n")
                    if len(data) > 0:
                        f.write(f"Sample: {json.dumps(data[0])}\n")
                sys.exit(0)
            else:
                with open("verify_result.txt", "w") as f:
                    f.write(f"WARNING: Unexpected format: {type(data)}\n")
                sys.exit(1)
        except json.JSONDecodeError:
             with open("verify_result.txt", "w") as f:
                f.write(f"ERROR: Invalid JSON: {body[:200]}\n")
             sys.exit(1)
except Exception as e:
    with open("verify_result.txt", "w") as f:
        f.write(f"ERROR: {e}\n")
        try:
            if hasattr(e, 'read'):
                 f.write(f"Server Response: {e.read().decode()}\n")
        except:
            pass
    sys.exit(1)
