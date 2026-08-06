#!/usr/bin/env python3
"""
Sync triton-ascend open issues with the "Issue跟踪" sheet in Google Sheets.

功能:
  1. 从 GitHub 获取所有 open issue（含最后评论内容）
  2. 将 issue 数据发送给 Apps Script，由 Apps Script 直接读取表格做增量更新:
     - 已存在 → 更新该行 A-J 列（不动 K/L/M）
     - 不存在 → 末尾追加新行
  3. 第 2 行写入最新执行时间
  4. 分批发送，每批 10 条，带重试
  5. 时间统一使用北京时间 (UTC+8)

环境变量:
  GITHUB_TOKEN     - GitHub token (Actions 自动注入 secrets.GITHUB_TOKEN)
  SHEET_WEBAPP_URL - Apps Script Web App URL (需配置为仓库 Secret)
"""

import os
import sys
import time
import requests
from datetime import datetime, timezone, timedelta

# ===== 时区 =====
BEIJING_TZ = timezone(timedelta(hours=8))

# ===== GitHub 配置 =====
REPO_OWNER = "triton-lang"
REPO_NAME = "triton-ascend"
API_BASE = "https://api.github.com"

# ===== Google Sheets 配置 =====
SHEET_ID = os.environ.get("SHEET_ID", "")
SHEET_NAME = "Issue跟踪"
SHEET_WEBAPP_URL = os.environ.get("SHEET_WEBAPP_URL", "")

STATUS_LABELS = {
    "triage review",
    "triaged",
    "wait feedback",
    "resolved",
    "stale",
    "duplicated",
    "invalid",
    "wontfix",
}
TYPE_LABELS = {
    "feature request",
    "rfc",
    "question",
    "documentation",
    "installation",
    "performance",
    "bug",
    "ssbuffer",
}

# ===== GitHub API 函数 =====


def make_headers(token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def requests_get(url, headers=None, params=None, max_retries=3, timeout=60):
    """带重试的 GET 请求，应对网络超时"""
    for attempt in range(max_retries):
        try:
            return requests.get(url, headers=headers, params=params, timeout=timeout)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f"    Network timeout, retry in {wait}s ({attempt+1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise


def get_remaining_from_response(resp):
    """从响应头中提取剩余 API 调用次数"""
    remaining = resp.headers.get("X-RateLimit-Remaining")
    if remaining is not None:
        return int(remaining)
    return None


def fetch_all_open_issues(token=None):
    """获取仓库所有 open issue（排除 PR）"""
    headers = make_headers(token)
    issues = []
    page = 1
    remaining = None
    while True:
        url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
        params = {
            "state": "open",
            "per_page": 100,
            "page": page,
            "sort": "created",
            "direction": "desc",
        }
        resp = requests_get(url, headers=headers, params=params)
        if resp.status_code == 403:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", 0))
            reset_dt = datetime.fromtimestamp(reset_ts, tz=timezone.utc)
            wait_sec = max(0, (reset_dt - datetime.now(timezone.utc)).total_seconds())
            print(f"\nAPI rate limit! Resets in {wait_sec/60:.1f} min.")
            if not token:
                print("Set GITHUB_TOKEN env var for higher limits (5000/hr).")
            if issues:
                print(f"Got {len(issues)} issues, continuing with partial data.")
                break
            sys.exit(1)
        resp.raise_for_status()
        remaining = get_remaining_from_response(resp)
        data = resp.json()
        if not data:
            break
        count_before = len(issues)
        for item in data:
            if "pull_request" not in item:
                issues.append(item)
        print(f"  Page {page}, total {len(issues)} issues ({len(issues)-count_before} new)")
        if remaining is not None:
            print(f"  API remaining: {remaining}")
        page += 1
    return issues, remaining


def fetch_last_comment(issue_number, token=None):
    """获取 issue 的最后一条评论，返回 dict 或 None"""
    headers = make_headers(token)
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}/comments"
    params = {"per_page": 1, "sort": "created", "direction": "desc"}
    remaining = None
    try:
        resp = requests_get(url, headers=headers, params=params)
        if resp.status_code == 403:
            return None, 0
        resp.raise_for_status()
        remaining = get_remaining_from_response(resp)
        data = resp.json()
        if data:
            return data[0], remaining
    except requests.exceptions.RequestException as e:
        print(f"    Warning: failed to fetch comments for issue #{issue_number}: {e}")
    return None, remaining


def parse_dt(dt_str):
    """解析 GitHub API 时间字符串"""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


# ===== 数据处理函数 =====


def categorize_labels(label_names):
    """将 GitHub labels 分为状态标签和类型标签（各取第一个匹配的）"""
    status = ""
    type_label = ""
    for name in label_names:
        normalized = name.lower().replace("-", " ")
        if not status and normalized in STATUS_LABELS:
            status = name
        elif not type_label and normalized in TYPE_LABELS:
            type_label = name
    return status, type_label


def truncate(text, max_len=200):
    if not text:
        return ""
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def fmt_dt(dt):
    if dt is None:
        return ""
    return dt.astimezone(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")


def build_issue_data(issue, last_comment):
    """构建单条 issue 的数据 (issue编号 + 10列值 A-J)"""
    created_at = parse_dt(issue["created_at"])
    label_names = [l["name"] for l in issue["labels"]]
    status_labels, type_labels = categorize_labels(label_names)

    last_comment_body = ""
    last_comment_time = ""
    if last_comment:
        last_comment_body = truncate(last_comment.get("body", ""))
        last_comment_time = fmt_dt(parse_dt(last_comment["created_at"]))

    return {
        "number":
        issue["number"],
        "values": [
            issue["title"],  # A: Issue Title
            issue["html_url"],  # B: Issue Link
            "否",  # C: 是否关闭
            (issue.get("user") or {}).get("login", "unknown"),  # D: 创建者
            fmt_dt(created_at),  # E: 创建时间
            "",  # F: 关闭时间
            last_comment_body,  # G: 最后评论内容
            last_comment_time,  # H: 最后评论时间
            status_labels,  # I: 状态标签
            type_labels,  # J: 类型标签
        ],
    }


# ===== Google Sheets 同步 =====


def sync_to_sheet(issues_data):
    """分批发送 issue 数据到 Apps Script（每批 10 条）"""
    if not SHEET_ID:
        print("ERROR: SHEET_ID not set. Configure it as a repository secret.")
        return False

    if not SHEET_WEBAPP_URL:
        print("ERROR: SHEET_WEBAPP_URL not set. Configure it as a repository secret.")
        return False

    batch_size = 10
    total_updated = 0
    total_inserted = 0
    total_failed = 0
    num_batches = (len(issues_data) + batch_size - 1) // batch_size

    exec_time = datetime.now(BEIJING_TZ).strftime("Last execution time: %Y-%m-%d %H:%M:%S")

    for batch_idx in range(num_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(issues_data))
        batch = issues_data[start:end]

        payload = {
            "mode": "sync",
            "spreadsheet_id": SHEET_ID,
            "sheet_name": SHEET_NAME,
            "exec_time": exec_time,
            "issues": batch,
        }

        success = False
        for attempt in range(5):
            cache_bust_params = {"v": int(time.time() * 1000)}
            try:
                resp = requests.post(SHEET_WEBAPP_URL, json=payload, params=cache_bust_params, timeout=120)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("status") == "ok":
                        u = result.get("updates", 0)
                        ins = result.get("inserts", 0)
                        total_updated += u
                        total_inserted += ins
                        print(f"  Batch {batch_idx+1}/{num_batches}: {u} updates, {ins} inserts")
                        success = True
                        break
                    else:
                        print(f"  Batch {batch_idx+1}: unexpected response: {resp.text[:200]}")
                elif resp.status_code >= 500:
                    print(f"  Batch {batch_idx+1}: HTTP {resp.status_code} (retryable): {resp.text[:200]}")
                else:
                    print(f"  Batch {batch_idx+1}: HTTP {resp.status_code} (non-retryable): {resp.text[:200]}")
                    break
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"  Error: {e}")
            print(f"  Batch {batch_idx+1} retry ({attempt+1}/5)...")
            time.sleep(3)

        if not success:
            total_failed += 1
            print(f"  Batch {batch_idx+1} failed, skipping")

    if total_failed > 0:
        print(f"\nSync completed with {total_failed} batch(es) failed!")
        print(f"  Total rows updated: {total_updated}")
        print(f"  Total rows inserted: {total_inserted}")
        return False

    print(f"\nSync complete!")
    print(f"  Total rows updated: {total_updated}")
    print(f"  Total rows inserted: {total_inserted}")
    return True


# ===== 主流程 =====


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        print("GITHUB_TOKEN set, authenticated mode (5000/hr)")
    else:
        print("No GITHUB_TOKEN, anonymous mode (60/hr)")

    print(f"\nFetching open issues from {REPO_OWNER}/{REPO_NAME}...")
    for attempt in range(5):
        try:
            issues, remaining = fetch_all_open_issues(token)
            break
        except Exception as e:
            if attempt < 4:
                print(f"\nFetch failed: {e}. Retrying in 10s ({attempt+2}/5)...")
                time.sleep(10)
            else:
                print(f"\nFetch failed after 5 attempts: {e}")
                sys.exit(1)
    print(f"\nFound {len(issues)} open issues on GitHub")

    if not issues:
        print("No open issues found.")
        return

    issues_data = []
    for i, issue in enumerate(issues, 1):
        number = issue["number"]
        comment_count = issue.get("comments", 0)

        last_comment = None
        if comment_count > 0 and remaining is not None and remaining >= 1:
            last_comment, new_remaining = fetch_last_comment(number, token)
            if new_remaining is not None:
                remaining = new_remaining
        elif comment_count > 0:
            print(f"  Warning: skipping comment fetch for issue #{number} (rate limit remaining: {remaining})")

        issues_data.append(build_issue_data(issue, last_comment))

        if i % 50 == 0 or i == len(issues):
            print(f"  Progress: {i}/{len(issues)}")

    print(f"\n{'='*50}")
    print(f"  Issues to sync: {len(issues_data)}")
    print(f"{'='*50}")

    if not sync_to_sheet(issues_data):
        sys.exit(1)


if __name__ == "__main__":
    main()
