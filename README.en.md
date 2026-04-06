# ZanaoJishi-Spider

An automation script for searching posts in the Campus Market WeChat mini program.

Chinese version: [README.md](README.md)

## Background

The Campus Market mini program does not directly provide a way to view all historical posts from one specific user.

This project is designed to:

1. Batch copy post links from WeChat chat history into `posts.txt`.
2. Open those links one by one automatically.
3. Capture on-screen text and filter by a target nickname keyword.
4. Save matched post content into local files.

This helps you quickly build a collection of posts that were likely published by a specific nickname.

## About `posts.txt` (Manual Input)

`posts.txt` is currently prepared manually from WeChat, and the workflow is straightforward:

1. Copy a batch of chat text from a WeChat conversation.
2. Paste it into `posts.txt`.
3. The script extracts `mp://...` links and uses the nearest preceding text as each post title.

In practice, copying about 100 messages at a time with around 8 links per message is already quite fast.

## Project Structure

```text
ZanaoJishi-Spider/
├─ spider_by_links.py   # Main script: parse links, drive WeChat, capture text, save results
├─ config.py            # Config: window titles, keywords, waits, input/output paths
├─ posts.txt            # Input: copied chat text containing mp:// links
├─ result/
│  ├─ ocount.txt        # Resume counter (current processed index)
│  └─ 帖子_*.txt        # Matched output files (generated after running)
├─ README.md            # Chinese (primary)
└─ README.en.md         # English
```

## Requirements

- Windows (desktop UI automation is required)
- Python 3.9+ (conda/venv recommended)
- PC WeChat installed and logged in
- Campus Market mini program can be opened from WeChat

Install dependency:

```bash
pip install uiautomation
```

## Usage

### 1. Update Config

Open `config.py` and check at least:

- `SAVE_KEYWORD`: nickname keyword to match
- `POSTS_FILE`: input file path (default: `posts.txt`)
- `RESULT_DIR`: output directory (default: `result`)

If your machine/network is slower, increase these wait values:

- `WAIT_AFTER_SEND`
- `WAIT_APP_POPUP`
- `WAIT_AFTER_APP_FOCUS`

### 2. Prepare Input File

Paste copied WeChat chat text into `posts.txt`, and make sure it contains `mp://...` links.

### 3. Open WeChat and Choose a Chat

Before running the script:

1. Open PC WeChat and keep it available in the foreground.
2. Switch to a chat where messages can be sent (File Transfer Assistant is commonly used).

### 4. Run Script

```bash
python spider_by_links.py
```

The script will:

1. Read `posts.txt`.
2. Read resume index from `result/ocount.txt` (supports restart from breakpoints).
3. Send each link and try to open the mini program window.
4. Capture visible text and check whether it contains `SAVE_KEYWORD`.
5. Save matched results as `帖子_序号_标题.txt` under `result/`.

## Output

- Console status per link: `命中` (matched) or `未命中` (not matched).
- Matched output files include:
  - Post title
  - Link
  - Capture time
  - Filtered text content

## FAQ

### WeChat Window Not Found

- Make sure PC WeChat is open and the window title contains "微信" or "WeChat".

### Link Sent but No Content Captured

- Increase `WAIT_APP_POPUP` and `WAIT_AFTER_APP_FOCUS`.
- Avoid switching focus between windows while the script is running.

### False Positives / Misses

- Matching is currently based on whether text contains `SAVE_KEYWORD`.
- Use a more specific keyword or add stricter matching rules later.

## Notes

- This is a personal productivity tool. Use it responsibly and in compliance with applicable rules.
- UI changes in the mini program may break automation selectors. Adjust parameters or logic when needed.
