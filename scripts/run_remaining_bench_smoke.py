import argparse
import datetime as dt
import io
import json
import random
import re
import shutil
import sys
import tarfile
import time
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from datasets import load_dataset, load_from_disk
from huggingface_hub import HfApi, hf_hub_download
from PIL import Image

from glm5v_smoke import (
    ROOT,
    extract_html,
    html_looks_complete,
    image_to_data_url,
    load_env,
    parse_optional_int,
    post_chat,
    resolve_provider,
    safe_write_jsonl,
)


OUT_RUN_DIR = ROOT / "experiments" / "random10_bench_smoke" / "mimo_random10_20260604"
MAX_FIELD_CHARS = 16000
VISUALWEBBENCH_CONFIGS = [
    "web_caption",
    "webqa",
    "heading_ocr",
    "element_ocr",
    "element_ground",
    "action_prediction",
    "action_ground",
]


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_") or "sample"


def truncate_text(value: str | None, limit: int = MAX_FIELD_CHARS) -> str:
    if value is None:
        return ""
    text = str(value)
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n[TRUNCATED: original length={len(text)} chars]"


def json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "tolist"):
        return json_safe(value.tolist())
    if hasattr(value, "size") and value.__class__.__module__.startswith("PIL"):
        return f"<PIL.Image size={value.size}>"
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]
    return str(value)


def extract_code_block(text: str, language: str = "python") -> str:
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
    match = re.search(rf"```{language}\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned.strip()


def make_html_prompt(sample: dict) -> str:
    extra = sample.get("prompt", "")
    return f"""你是一个严谨的前端工程师。请根据输入材料生成一个完整、可直接运行的单文件 HTML。

要求：
1. 输出必须包含 <!DOCTYPE html>、<html>、<head>、<style>、<body>。
2. CSS 写在 <style> 中，不要依赖外部 CSS、JS、图片、字体或网络资源。
3. 尽可能还原截图或描述中的布局、颜色、字号、间距、组件层级和视觉密度。
4. 如果截图中有真实图片、头像、图标或复杂素材，无法复用原图时用 CSS 色块/渐变/简化图形占位，但尺寸和位置要对齐。
5. 如果任务涉及交互，请在单文件内写必要的 JavaScript。
6. 只输出一个 fenced code block，格式为 ```html ... ```，不要输出额外解释。

Benchmark：{sample["bench"]}
任务类型：{sample["task_type"]}
原始任务提示：
{extra}
"""


def image_cell_to_bytes(value) -> bytes | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    if isinstance(value, dict):
        if value.get("bytes"):
            return value["bytes"]
        path = value.get("path")
        if path:
            return Path(path).read_bytes()
    if hasattr(value, "save"):
        buffer = io.BytesIO()
        value.save(buffer, format="PNG")
        return buffer.getvalue()
    return None


def path_image(path: Path) -> dict:
    return {"kind": "path", "path": path, "name": path.name}


def bytes_image(data: bytes, name: str) -> dict:
    return {"kind": "bytes", "bytes": data, "name": name}


def pil_image(image, name: str) -> dict:
    return {"kind": "pil", "image": image, "name": name}


def zip_image(zip_path: Path, member: str) -> dict:
    return {"kind": "zip", "zip_path": zip_path, "member": member, "name": Path(member).name}


def tar_image(tar_path: Path, member: str) -> dict:
    return {"kind": "tar", "tar_path": tar_path, "member": member, "name": Path(member).name}


def materialize_image(source: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    kind = source["kind"]
    if kind == "path":
        shutil.copy2(source["path"], dest)
    elif kind == "bytes":
        dest.write_bytes(source["bytes"])
    elif kind == "pil":
        source["image"].save(dest)
    elif kind == "zip":
        with ZipFile(source["zip_path"]) as zf:
            dest.write_bytes(zf.read(source["member"]))
    elif kind == "tar":
        with tarfile.open(source["tar_path"], "r:gz") as tf:
            extracted = tf.extractfile(source["member"])
            if extracted is None:
                raise FileNotFoundError(source["member"])
            dest.write_bytes(extracted.read())
    else:
        raise ValueError(f"Unsupported image source kind: {kind}")


def sample_list(items: list, rng: random.Random, limit: int) -> list:
    if len(items) <= limit:
        return list(items)
    return rng.sample(items, limit)


def build_designbench_samples(rng: random.Random, limit: int) -> dict:
    repo = "whale99/DesignBench"
    api = HfApi()
    files = api.list_repo_files(repo_id=repo, repo_type="dataset")
    by_id: dict[str, set[str]] = {}
    pattern = re.compile(r"^generation/vanilla/([^/]+)/\1\.(json|png)$")
    for file_name in files:
        match = pattern.match(file_name)
        if match:
            by_id.setdefault(match.group(1), set()).add(match.group(2))
    ids = sorted(sample_id for sample_id, exts in by_id.items() if {"json", "png"} <= exts)
    selected = sample_list(ids, rng, limit)

    samples = []
    for sample_id in selected:
        json_file = f"generation/vanilla/{sample_id}/{sample_id}.json"
        png_file = f"generation/vanilla/{sample_id}/{sample_id}.png"
        meta_path = hf_hub_download(repo_id=repo, repo_type="dataset", filename=json_file)
        image_path = hf_hub_download(repo_id=repo, repo_type="dataset", filename=png_file)
        meta = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        prompt = (
            "DesignBench Generation / Vanilla HTML 任务。请根据目标网页截图生成单文件 HTML。\n"
            f"网页 URL：{meta.get('url', '')}\n"
            f"主题：{meta.get('topic', '')}\n"
            f"来源类型：{meta.get('type', '')}\n"
            f"框架字段：{meta.get('framework', '')}"
        )
        samples.append(
            {
                "bench": "designbench",
                "sample_id": f"generation_vanilla_{sample_id}",
                "task_type": "image_to_html_generation",
                "source": "HF whale99/DesignBench/generation/vanilla",
                "prompt": prompt,
                "image_sources": [path_image(Path(image_path))],
                "metadata": meta,
                "output_kind": "html",
            }
        )
    return {"available": len(ids), "samples": samples, "warnings": []}


def read_fullfront_rows(repo: str, filename: str, category: str) -> list[dict]:
    local = hf_hub_download(repo_id=repo, repo_type="dataset", filename=filename)
    df = pd.read_parquet(local)
    rows = df.to_dict("records")
    for row in rows:
        row["_category_source"] = category
    return rows


def build_fullfront_prompt(row: dict) -> tuple[str, list[dict], dict]:
    category = row.get("Category") or row.get("_category_source")
    image_sources = []
    extra = ""

    if category == "Image_to_code":
        image_bytes = image_cell_to_bytes(row.get("Image"))
        if image_bytes:
            image_sources.append(bytes_image(image_bytes, f"{row.get('Png_id', row.get('Id'))}.png"))
        extra = row.get("Prompt", "")
    elif category == "Text_to_code":
        image_bytes = image_cell_to_bytes(row.get("Image"))
        if image_bytes:
            image_sources.append(bytes_image(image_bytes, f"reference_{row.get('Png_id', row.get('Id'))}.png"))
        extra = f"{row.get('Prompt', '')}\n\nDescription:\n{truncate_text(row.get('Input_text'))}"
    elif category == "Code_Refinement":
        image_bytes = image_cell_to_bytes(row.get("Image"))
        if image_bytes:
            image_sources.append(bytes_image(image_bytes, f"{row.get('Png_id', row.get('Id'))}.png"))
        extra = (
            f"{row.get('Prompt', '')}\n\n"
            f"Initial front-end code:\n```html\n{truncate_text(row.get('Input_html'))}\n```"
        )
    elif category == "Interaction_Authoring":
        before_bytes = image_cell_to_bytes(row.get("Before_image"))
        after_bytes = image_cell_to_bytes(row.get("After_image"))
        if before_bytes:
            image_sources.append(bytes_image(before_bytes, f"before_{row.get('Png_id', row.get('Id'))}.png"))
        if after_bytes:
            image_sources.append(bytes_image(after_bytes, f"after_{row.get('Png_id', row.get('Id'))}.png"))
        extra = (
            f"{row.get('Prompt', '')}\n\n"
            f"Interaction type: {row.get('Interaction_type', '')}\n\n"
            f"Current HTML:\n```html\n{truncate_text(row.get('Label_html'))}\n```"
        )
    else:
        extra = row.get("Prompt", "")

    meta = {
        "Id": row.get("Id"),
        "Png_id": row.get("Png_id"),
        "Category": category,
        "Interaction_type": row.get("Interaction_type"),
    }
    return extra, image_sources, meta


def build_fullfront_samples(rng: random.Random, limit: int) -> dict:
    repo = "Mikivis/FullFront-mini"
    parquet_files = {
        "Image_to_code": "data/Image_to_code-00000-of-00001-df3fe9ce9056f83b.parquet",
        "Text_to_code": "data/Text_to_code-00000-of-00001-d64170adf8d2ce8a.parquet",
        "Code_Refinement": "data/Code_Refinement-00000-of-00001-18fb1796fe4c8a98.parquet",
        "Interaction_Authoring": "data/Interaction_Authoring-00000-of-00001-495aff62f8362387.parquet",
    }
    rows = []
    for category, filename in parquet_files.items():
        rows.extend(read_fullfront_rows(repo, filename, category))
    selected = sample_list(rows, rng, limit)
    samples = []
    for row in selected:
        prompt, image_sources, meta = build_fullfront_prompt(row)
        category = meta["Category"]
        samples.append(
            {
                "bench": "fullfront",
                "sample_id": f"{category}_{row.get('Id')}_{safe_name(row.get('Png_id', ''))}",
                "task_type": category,
                "source": f"HF {repo}",
                "prompt": prompt,
                "image_sources": image_sources,
                "metadata": meta,
                "reference_html": row.get("Label_html"),
                "output_kind": "html",
                "notes": "使用 FullFront-mini 的代码生成/修复/交互任务做 smoke run；不是完整 FullFront 全量评测。",
            }
        )
    return {"available": len(rows), "samples": samples, "warnings": []}


def build_screenbench_samples(rng: random.Random, limit: int) -> dict:
    repo = "Leigest/ScreenCoder"
    image_zip = Path(hf_hub_download(repo_id=repo, repo_type="dataset", filename="image.zip"))
    html_zip = Path(hf_hub_download(repo_id=repo, repo_type="dataset", filename="HTML.zip"))
    with ZipFile(image_zip) as iz, ZipFile(html_zip) as hz:
        image_members = {
            Path(name).stem: name
            for name in iz.namelist()
            if name.lower().endswith(".png") and "__macosx" not in name.lower()
        }
        html_members = {
            Path(name).stem: name
            for name in hz.namelist()
            if name.lower().endswith(".html") and "__macosx" not in name.lower()
        }
    ids = sorted(set(image_members) & set(html_members))
    selected = sample_list(ids, rng, limit)
    samples = []
    for sample_id in selected:
        prompt = "ScreenBench / ScreenCoder 任务。请根据真实网页截图生成一个结构清晰、可编辑的单文件 HTML/CSS。"
        with ZipFile(html_zip) as hz:
            reference_html = hz.read(html_members[sample_id]).decode("utf-8", errors="replace")
        samples.append(
            {
                "bench": "screencoder_screenbench",
                "sample_id": sample_id,
                "task_type": "screenshot_to_html",
                "source": "HF Leigest/ScreenCoder image.zip + HTML.zip",
                "prompt": prompt,
                "image_sources": [zip_image(image_zip, image_members[sample_id])],
                "reference_html": reference_html,
                "output_kind": "html",
            }
        )
    return {"available": len(ids), "samples": samples, "warnings": []}


def build_vision2web_samples(rng: random.Random, limit: int) -> dict:
    ds = load_dataset("zai-org/Vision2Web", "webpage", split="test")
    rows = [dict(row) for row in ds]
    selected = sample_list(rows, rng, limit)
    archive = Path(hf_hub_download(repo_id="zai-org/Vision2Web", repo_type="dataset", filename="archives/webpage.tar.gz"))

    samples = []
    for row in selected:
        task_name = row["task_name"]
        prototypes = row.get("prototypes") or []
        image_sources = [tar_image(archive, f"webpage/{task_name}/prototypes/{proto}") for proto in prototypes]
        prompt = (
            "Vision2Web Level 1 静态网页任务。输入包含同一网页的 desktop/tablet/mobile 原型图。"
            "请生成一个响应式单文件 HTML，使页面在不同宽度下尽可能匹配这些原型。\n"
            f"Task name: {task_name}\n"
            f"Prototype files: {', '.join(prototypes)}\n"
            f"Workflow steps: {row.get('workflow_steps')}; resources_count: {row.get('resources_count')}."
        )
        samples.append(
            {
                "bench": "vision2web",
                "sample_id": task_name,
                "task_type": "level1_static_webpage",
                "source": "HF zai-org/Vision2Web webpage archive",
                "prompt": prompt,
                "image_sources": image_sources,
                "metadata": json_safe(row),
                "output_kind": "html",
                "notes": "本轮只跑 Level 1 webpage 原型图到单文件 HTML；未使用官方 agent sandbox 和资源文件。",
            }
        )
    return {"available": len(rows), "samples": samples, "warnings": []}


def visualwebbench_prompt(row: dict) -> str:
    task_type = row["task_type"]
    if task_type == "web_caption":
        return (
            "你会看到一张网页截图。请生成该网页的 meta description 内容，"
            "只输出描述文本，不要解释。"
        )
    if task_type == "webqa":
        return f"{row['question']}\n请结合网页截图直接回答，尽量少词，不要解释。"
    if task_type == "heading_ocr":
        return "你会看到一张网页截图。请输出截图中的主标题文字，只输出答案，不要解释。"
    if task_type == "element_ocr":
        return (
            "你会看到一张带红色矩形框的网页截图。"
            f"红框坐标比例为 {row.get('bbox')}。请输出红框内的文字内容，只输出答案。"
        )
    if task_type == "element_ground":
        return (
            "你会看到一张网页截图，里面给候选 HTML 元素标了 ID。"
            f"请判断哪个 ID 最符合描述：{row.get('elem_desc')}。只输出 ID。"
        )
    if task_type == "action_prediction":
        return (
            "你会看到一张带红色矩形框的网页截图。"
            f"红框坐标比例为 {row.get('bbox')}，元素描述为：{row.get('elem_desc')}。\n"
            f"候选操作/目标如下：{row.get('options')}。\n"
            "请选择最可能的选项编号，只输出编号。"
        )
    if task_type == "action_ground":
        return (
            "你会看到一张网页截图，候选可点击元素已标注 ID。"
            f"请判断为了完成任务“{row.get('instruction')}”应该点击哪个 ID。只输出 ID。"
        )
    return "请根据网页截图回答问题，只输出答案。"


def build_visualwebbench_samples(rng: random.Random, limit: int) -> dict:
    rows = []
    warnings = []
    for config in VISUALWEBBENCH_CONFIGS:
        try:
            ds = load_dataset("visualwebbench/VisualWebBench", config, split="test")
        except Exception as exc:
            warnings.append(f"{config}: {type(exc).__name__}: {exc}")
            continue
        rows.extend(dict(row) for row in ds)
    selected = sample_list(rows, rng, limit)
    samples = []
    for row in selected:
        metadata = {k: json_safe(v) for k, v in row.items() if k not in {"image", "raw_image"}}
        samples.append(
            {
                "bench": "visualwebbench",
                "sample_id": row.get("id", f"{row.get('task_type')}_{len(samples)}"),
                "task_type": row.get("task_type", "web_understanding"),
                "source": "HF visualwebbench/VisualWebBench",
                "prompt": visualwebbench_prompt(row),
                "image_sources": [pil_image(row["image"], f"{row.get('id', len(samples))}.png")],
                "metadata": metadata,
                "reference_answer": row.get("answer"),
                "output_kind": "text",
                "notes": "网页理解/grounding QA smoke run，不抽取 HTML。",
            }
        )
    return {"available": len(rows), "samples": samples, "warnings": warnings}


def build_humaneval_v_samples(rng: random.Random, limit: int) -> dict:
    ds = load_from_disk(str(ROOT / "benchmarks" / "humaneval_v" / "humaneval_v_test_hf"))
    rows = [dict(row) for row in ds]
    selected = sample_list(rows, rng, limit)
    samples = []
    for row in selected:
        prompt = f"""你会看到一张编码题相关的图。请结合图像和函数签名，补全 Python 解法。

要求：
1. 只输出一个 fenced code block，格式为 ```python ... ```。
2. 必须实现给定的 `solution` 函数签名。
3. 不要输出解释。

函数签名：
```python
{row["function_signature"]}
```

任务类型：{row.get("task_type", "")}
能力标签：{json.dumps(json_safe(row.get("capability_aspects")), ensure_ascii=False)}
"""
        samples.append(
            {
                "bench": "humaneval_v",
                "sample_id": row["qid"],
                "task_type": "diagram_to_python_code",
                "source": "local benchmarks/humaneval_v/humaneval_v_test_hf",
                "prompt": prompt,
                "image_sources": [pil_image(row["diagram"], f"{row['qid']}.png")],
                "metadata": {
                    "qid": row["qid"],
                    "task_type": row.get("task_type"),
                    "capability_aspects": json_safe(row.get("capability_aspects")),
                    "function_signature": row.get("function_signature"),
                },
                "reference_solution": row.get("ground_truth_solution"),
                "reference_answer": row.get("test_script"),
                "output_kind": "python_code",
                "notes": "偏视觉推理到 Python 代码，不是前端 UI；用于补齐其他bench.jpg里的候选。",
            }
        )
    return {"available": len(rows), "samples": samples, "warnings": []}


BUILDERS = {
    "designbench": build_designbench_samples,
    "fullfront": build_fullfront_samples,
    "screencoder_screenbench": build_screenbench_samples,
    "vision2web": build_vision2web_samples,
    "visualwebbench": build_visualwebbench_samples,
    "humaneval_v": build_humaneval_v_samples,
}


def ensure_bench_dirs(bench_dir: Path) -> None:
    for sub in [
        "inputs",
        "inputs/images",
        "inputs/prompts",
        "inputs/references",
        "raw",
        "texts",
        "html",
        "code",
    ]:
        (bench_dir / sub).mkdir(parents=True, exist_ok=True)


def prepare_sample(sample: dict, bench_dir: Path) -> dict:
    sample_name = safe_name(sample["sample_id"])
    local_image_paths = []
    for idx, source in enumerate(sample.get("image_sources", [])):
        suffix = Path(source.get("name", f"{idx}.png")).suffix.lower() or ".png"
        local_path = bench_dir / "inputs" / "images" / f"{sample_name}_{idx}{suffix}"
        if not local_path.exists():
            materialize_image(source, local_path)
        local_image_paths.append(str(local_path.relative_to(ROOT)))

    prompt_text = make_html_prompt(sample) if sample.get("output_kind") == "html" else sample["prompt"]
    prompt_path = bench_dir / "inputs" / "prompts" / f"{sample_name}.txt"
    prompt_path.write_text(prompt_text, encoding="utf-8")

    item = {
        "bench": sample["bench"],
        "sample_id": sample["sample_id"],
        "task_type": sample["task_type"],
        "source": sample.get("source", ""),
        "notes": sample.get("notes", ""),
        "metadata": json_safe(sample.get("metadata", {})),
        "local_image_paths": local_image_paths,
        "local_prompt_path": str(prompt_path.relative_to(ROOT)),
        "output_kind": sample.get("output_kind", "text"),
    }

    if sample.get("reference_html"):
        ref_path = bench_dir / "inputs" / "references" / f"{sample_name}_reference.html"
        ref_path.write_text(str(sample["reference_html"]), encoding="utf-8", errors="replace")
        item["reference_html_path"] = str(ref_path.relative_to(ROOT))
    if sample.get("reference_solution"):
        ref_path = bench_dir / "inputs" / "references" / f"{sample_name}_reference.py"
        ref_path.write_text(str(sample["reference_solution"]), encoding="utf-8", errors="replace")
        item["reference_solution_path"] = str(ref_path.relative_to(ROOT))
    if "reference_answer" in sample and sample.get("reference_answer") is not None:
        ref_path = bench_dir / "inputs" / "references" / f"{sample_name}_answer.json"
        ref_path.write_text(json.dumps(json_safe(sample["reference_answer"]), ensure_ascii=False, indent=2), encoding="utf-8")
        item["reference_answer_path"] = str(ref_path.relative_to(ROOT))
    return item


def run_one_sample(sample: dict, item: dict, provider: dict, model: str, max_tokens: int, timeout: int, retries: int, retry_delay: int) -> tuple[dict, dict]:
    prompt_path = ROOT / item["local_prompt_path"]
    content = [{"type": "text", "text": prompt_path.read_text(encoding="utf-8")}]
    for rel_path in item.get("local_image_paths", []):
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(ROOT / rel_path)}})

    body = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
    }
    if max_tokens > 0:
        body["max_tokens"] = max_tokens

    final_record = None
    for attempt in range(retries + 1):
        status, response = post_chat(
            provider["base_url"],
            provider["api_key"],
            body,
            timeout,
            provider["bypass_proxy"],
        )
        final_record = {
            "bench": sample["bench"],
            "sample_id": sample["sample_id"],
            "attempt": attempt,
            "http_status": status,
            "response": response,
        }
        if status == 200:
            break
        if status in {429, 500, 502, 503, 504} and attempt < retries:
            time.sleep(retry_delay)
            continue
        break
    return final_record, {"http_status": final_record["http_status"]}


def save_response_outputs(sample: dict, item: dict, final_record: dict, bench_dir: Path) -> dict:
    result = {**item, "http_status": final_record["http_status"]}
    sample_name = safe_name(sample["sample_id"])
    response = final_record["response"]
    if final_record["http_status"] != 200 or not isinstance(response, dict):
        result["error"] = json_safe(response)
        return result

    message = response["choices"][0]["message"]["content"]
    text_path = bench_dir / "texts" / f"{sample_name}.txt"
    text_path.write_text(message, encoding="utf-8", errors="replace")
    result["text_path"] = str(text_path.relative_to(ROOT))
    result["usage"] = response.get("usage")

    output_kind = sample.get("output_kind")
    if output_kind == "html":
        html = extract_html(message)
        result["html_extracted"] = bool(html)
        if html:
            result["html_complete"] = html_looks_complete(html)
            html_path = bench_dir / "html" / f"{sample_name}.html"
            html_path.write_text(html, encoding="utf-8", errors="replace")
            result["html_path"] = str(html_path.relative_to(ROOT))
    elif output_kind == "python_code":
        code = extract_code_block(message, "python")
        code_path = bench_dir / "code" / f"{sample_name}.py"
        code_path.write_text(code, encoding="utf-8", errors="replace")
        result["code_path"] = str(code_path.relative_to(ROOT))
        result["code_extracted"] = bool(code.strip())
    else:
        result["text_extracted"] = bool(message.strip())
    return result


def run_bench(bench: str, build_info: dict, run_dir: Path, provider: dict, max_tokens: int, timeout: int, retries: int, retry_delay: int, dry_run: bool) -> dict:
    bench_dir = run_dir / bench
    ensure_bench_dirs(bench_dir)
    raw_path = bench_dir / "raw" / "responses.jsonl"
    selected_path = bench_dir / "inputs" / "selected_samples.jsonl"

    results = []
    for sample in build_info["samples"]:
        item = prepare_sample(sample, bench_dir)
        safe_write_jsonl(selected_path, item)
        if dry_run:
            result = {**item, "status": "dry_run"}
            results.append(result)
            print(json.dumps({"bench": bench, "sample_id": sample["sample_id"], "status": "dry_run"}, ensure_ascii=False), flush=True)
            continue
        final_record, _ = run_one_sample(sample, item, provider, provider["model"], max_tokens, timeout, retries, retry_delay)
        safe_write_jsonl(raw_path, final_record)
        result = save_response_outputs(sample, item, final_record, bench_dir)
        results.append(result)
        print(
            json.dumps(
                {
                    "bench": bench,
                    "sample_id": sample["sample_id"],
                    "http_status": result.get("http_status"),
                    "html": result.get("html_extracted"),
                    "code": result.get("code_extracted"),
                    "text": result.get("text_extracted"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if result.get("http_status") == 429:
            break

    return {
        "available": build_info.get("available", len(build_info["samples"])),
        "selected": len(build_info["samples"]),
        "warnings": build_info.get("warnings", []),
        "results": results,
    }


def summarize_bench(info: dict) -> dict:
    results = info.get("results", [])
    return {
        "available": info.get("available", 0),
        "selected": info.get("selected", 0),
        "ok": sum(1 for item in results if item.get("http_status") == 200),
        "html": sum(1 for item in results if item.get("html_extracted")),
        "complete": sum(1 for item in results if item.get("html_complete")),
        "code": sum(1 for item in results if item.get("code_extracted")),
        "text": sum(1 for item in results if item.get("text_extracted")),
        "failed": sum(1 for item in results if item.get("http_status") not in {200, None}),
    }


def write_summary_md(run_dir: Path, summary: dict) -> None:
    lines = [
        "# Random 10 Benchmark Smoke Summary",
        "",
        f"- run_dir: `{summary.get('run_dir')}`",
        f"- provider/model: `{summary.get('provider')}` / `{summary.get('model')}`",
        f"- max_tokens: `{'omitted' if not summary.get('max_tokens') else summary.get('max_tokens')}`",
        f"- bypass_proxy: `{summary.get('bypass_proxy')}`",
        f"- sample_size_per_bench: `{summary.get('sample_size_per_bench')}`",
        f"- seed: `{summary.get('seed')}`",
        f"- dry_run: `{summary.get('dry_run')}`",
        "",
        "| bench | available | selected | ok | html | complete | code | text | failed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for bench, info in summary.get("benches", {}).items():
        stat = summarize_bench(info)
        lines.append(
            f"| {bench} | {stat['available']} | {stat['selected']} | {stat['ok']} | "
            f"{stat['html']} | {stat['complete']} | {stat['code']} | {stat['text']} | {stat['failed']} |"
        )
    skipped = summary.get("skipped") or []
    if skipped:
        lines.extend(["", "## Skipped", "", "| bench | reason |", "|---|---|"])
        for item in skipped:
            reason = str(item.get("reason", "")).replace("|", "\\|")
            lines.append(f"| {item.get('bench')} | {reason} |")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def merge_summary(run_dir: Path, provider: dict, args, new_benches: dict, skipped: list[dict]) -> None:
    summary_path = run_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        backup = run_dir / "summary.before_remaining.json"
        if not backup.exists():
            shutil.copy2(summary_path, backup)
    else:
        summary = {
            "run_dir": str(run_dir.relative_to(ROOT)),
            "benches": {},
        }
    summary["provider"] = provider["name"]
    summary["model"] = provider["model"]
    summary["base_url"] = provider["base_url"].rstrip("/") if provider["base_url"] else ""
    summary["bypass_proxy"] = provider["bypass_proxy"]
    summary["max_tokens"] = args.max_tokens if args.max_tokens > 0 else None
    summary["sample_size_per_bench"] = args.limit
    summary["seed"] = args.seed
    summary["dry_run"] = args.dry_run
    summary.setdefault("benches", {}).update(new_benches)

    completed = set(new_benches)
    old_skipped = [item for item in summary.get("skipped", []) if item.get("bench") not in completed]
    skipped_by_bench = {item["bench"]: item for item in old_skipped if item.get("bench")}
    for item in skipped:
        skipped_by_bench[item["bench"]] = item
    summary["skipped"] = list(skipped_by_bench.values())
    summary["remaining_benches_run_at"] = dt.datetime.now().isoformat(timespec="seconds")
    summary["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary_md(run_dir, summary)


def write_skipped_status(run_dir: Path, skipped: list[dict]) -> None:
    for item in skipped:
        bench_dir = run_dir / item["bench"]
        bench_dir.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {item['bench']} status",
            "",
            f"- status: skipped",
            f"- reason: {item['reason']}",
        ]
        if item.get("source"):
            lines.append(f"- source: {item['source']}")
        (bench_dir / "status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run remaining benchmark smoke samples into the existing random10 run directory.")
    parser.add_argument("--run-dir", type=Path, default=OUT_RUN_DIR)
    parser.add_argument("--provider", choices=["zhipu", "qwen", "mimo"], default="mimo")
    parser.add_argument("--benches", nargs="*", default=list(BUILDERS))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260604)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=int, default=20)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    env = load_env(ROOT / ".env")
    provider = resolve_provider(env, args.provider)
    env_max_tokens = parse_optional_int(env.get("EXPERIMENT_MAX_TOKENS"), 0)
    max_tokens = env_max_tokens if args.max_tokens is None else args.max_tokens
    provider["model"] = provider["model"]

    if not args.dry_run and (not provider["api_key"] or not provider["base_url"]):
        print(f"{args.provider} API key or base URL is empty. Fill .env first.", file=sys.stderr)
        return 2
    if not args.dry_run and not provider["supports_image"]:
        print(f"{args.provider} is text-only; remaining smoke benches require images.", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    selected_benches = [bench for bench in args.benches if bench in BUILDERS]
    new_benches = {}
    skipped = [
        {
            "bench": "vab_css",
            "reason": "本地缺少官方 `data/css_dataset`，README 只给 VAB-CSS 配置说明，没有可直接抽样的测试数据；该任务还依赖 CSS edit agent 环境，不适合用单轮截图到 HTML smoke 代替。",
            "source": "benchmarks/vab_css_visualagentbench/configs/tasks/css.yaml",
        },
        {
            "bench": "frontendbench",
            "reason": "论文页此前说明 data/code will be released soon；当前本地没有官方数据或仓库，暂不能补跑。",
        },
    ]

    for bench in selected_benches:
        print(json.dumps({"event": "build_samples", "bench": bench}, ensure_ascii=False), flush=True)
        try:
            build_info = BUILDERS[bench](rng, args.limit)
            if not build_info["samples"]:
                skipped.append({"bench": bench, "reason": "未能构建可运行样本。"})
                continue
            print(
                json.dumps(
                    {"event": "run_bench", "bench": bench, "available": build_info.get("available"), "selected": len(build_info["samples"])},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            new_benches[bench] = run_bench(
                bench,
                build_info,
                run_dir,
                provider,
                max_tokens,
                args.timeout,
                args.retries,
                args.retry_delay,
                args.dry_run,
            )
        except Exception as exc:
            reason = f"{type(exc).__name__}: {exc}"
            print(json.dumps({"event": "bench_error", "bench": bench, "reason": reason}, ensure_ascii=False), flush=True)
            skipped.append({"bench": bench, "reason": reason})

    write_skipped_status(run_dir, skipped)
    args.max_tokens = max_tokens
    merge_summary(run_dir, provider, args, new_benches, skipped)
    print(json.dumps({"run_dir": str(run_dir), "benches": list(new_benches), "skipped": skipped}, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
