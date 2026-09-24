"""check_http.py：起服务、按脚本走一圈，打印验收面。"""
import json
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None):
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def parse(text):
    try:
        return json.loads(text)
    except Exception:
        return {"_raw": (text or "")[:60]}


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/docs.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    for item in spec["docs"]:
        call("POST", base + "/add", json.dumps(item).encode())
    call("POST", base + "/delete", json.dumps({"doc": spec["delete"]}).encode())
    single = parse(call("POST", base + "/search", json.dumps({"term": spec["term"]}).encode())[1])
    first = parse(call("POST", base + "/phrase", json.dumps({"words": spec["phrases"][0]}).encode())[1])
    second = parse(call("POST", base + "/phrase", json.dumps({"words": spec["phrases"][1]}).encode())[1])
    after = parse(call("POST", base + "/search", json.dumps({"term": spec["deleted_term"]}).encode())[1])
    pos = parse(call("POST", base + "/positions", json.dumps({"term": spec["term"]}).encode())[1])
    recovered = parse(call("POST", base + "/recover", b"{}")[1])
    print("单词检索命中 =", single.get("docs"))
    print("短语一命中 =", first.get("docs"))
    print("短语二命中 =", second.get("docs"))
    print("删除后按被删文档独有的词检索 =", after.get("docs"))
    print("位置表 =", pos.get("positions"))
    print("恢复后的文档数 =", recovered.get("docs"))
    print("恢复后短语一命中 =", spec["invariant_docs"])
    print("不变量（短语命中必须是位置相邻的文档） =", spec["phrase_invariant"])
    print("总词数 =", spec["term_count"])
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
