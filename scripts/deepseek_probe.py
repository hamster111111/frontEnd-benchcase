import argparse
import json
import sys

from glm5v_smoke import ROOT, load_env, post_chat


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe the DeepSeek OpenAI-compatible chat API.")
    parser.add_argument("--model", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--prompt", default="请用一句中文回答：DeepSeek API 连通了吗？")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    env = load_env(ROOT / ".env")
    api_key = env.get("DEEPSEEK_API_KEY", "")
    base_url = args.base_url or env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = args.model or env.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
    thinking = env.get("DEEPSEEK_THINKING", "").strip()
    reasoning_effort = env.get("DEEPSEEK_REASONING_EFFORT", "").strip()

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个简洁的中文助手。"},
            {"role": "user", "content": args.prompt},
        ],
        "stream": False,
        "max_tokens": args.max_tokens,
    }
    if thinking:
        body["thinking"] = {"type": thinking}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort

    if args.dry_run:
        print(json.dumps({"base_url": base_url, "model": model, "has_key": bool(api_key)}, ensure_ascii=False, indent=2))
        return 0

    if not api_key:
        print("DEEPSEEK_API_KEY is empty. Fill .env first.", file=sys.stderr)
        return 2

    status, response = post_chat(base_url, api_key, body, args.timeout)
    output = {"http_status": status, "base_url": base_url, "model": model}
    if status == 200 and isinstance(response, dict):
        output["content"] = response["choices"][0]["message"]["content"]
        output["usage"] = response.get("usage")
    else:
        output["error"] = response
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
