# ZanaoJishi-Spider

一个用于校园集市小程序帖子检索的自动化脚本。

An automation script for searching posts in the Campus Market WeChat mini program.

## 项目背景 | Background

校园集市微信小程序本身不支持直接查看某个用户的历史发帖。

The Campus Market mini program does not directly provide a "view all historical posts by one user" feature.

这个项目的目标是：

The goal of this project is to:

1. 你先把群聊里看到的帖子链接批量复制到 `posts.txt`。
1. Batch copy post links from WeChat chat history into `posts.txt`.
2. 脚本自动逐条打开这些帖子。
2. Open those links one by one automatically.
3. 从页面中抓取文本并按指定昵称关键字筛选。
3. Capture on-screen text and filter by a target nickname keyword.
4. 把命中的帖子内容保存到本地文件。
4. Save matched post content to local text files.

这样就能快速整理出「某个 nickname 可能发过的帖子集合」。

This helps you quickly build a collection of posts that were likely published by a specific nickname.

## 关于 `posts.txt`（手动准备） | About `posts.txt` (Manual Input)

目前 `posts.txt` 需要手动从微信里复制，这个流程实际上不复杂：

`posts.txt` is currently prepared manually from WeChat, and the process is straightforward:

1. 在微信聊天窗口里一次复制一批聊天文本。
1. Copy a batch of chat text from a WeChat conversation.
2. 粘贴到 `posts.txt`。
2. Paste it into `posts.txt`.
3. 脚本会自动从文本中提取 `mp://...` 链接，并把链接前面的最近一段文字当作标题。
3. The script extracts `mp://...` links and uses the nearest preceding text as the title.

实践上，一次复制大约 100 条消息、每条约 8 个链接，整理速度已经很快。

In practice, copying around 100 messages at a time with about 8 links each is already fast enough.

## 项目结构 | Project Structure

```text
ZanaoJishi-Spider/
├─ spider_by_links.py   # 主脚本 Main script: parse links, drive WeChat, capture text, save results
├─ config.py            # 配置文件 Config: window titles, keywords, waits, file paths
├─ posts.txt            # 输入文件 Input: copied chat text containing mp:// links
├─ result/
│  ├─ ocount.txt        # 断点计数 Resume counter (current processed index)
│  └─ 帖子_*.txt        # 命中文件 Matched output files (generated after running)
└─ README.md
```

## 运行环境 | Requirements

- Windows（脚本依赖桌面 UI 自动化）
- Windows (desktop UI automation is required)
- Python 3.9+（推荐使用 conda/venv）
- Python 3.9+ (conda/venv recommended)
- 已安装并登录 PC 微信
- PC WeChat installed and logged in
- 微信里可正常打开校园集市小程序
- Campus Market mini program can be opened from WeChat

安装依赖 | Install dependency:

```bash
pip install uiautomation
```

## 使用方法 | Usage

### 1. 修改配置 | Update config

打开 `config.py`，至少检查以下配置：

Open `config.py` and check at least these fields:

- `SAVE_KEYWORD`：你要检索的昵称关键字
- `SAVE_KEYWORD`: nickname keyword to match
- `POSTS_FILE`：输入文件路径（默认 `posts.txt`）
- `POSTS_FILE`: input file path (default `posts.txt`)
- `RESULT_DIR`：输出目录（默认 `result`）
- `RESULT_DIR`: output directory (default `result`)

如果电脑较卡或网络慢，可以适当调大这些等待时间：

If your machine/network is slow, increase these wait values:

- `WAIT_AFTER_SEND`
- `WAIT_APP_POPUP`
- `WAIT_AFTER_APP_FOCUS`

### 2. 准备输入文件 | Prepare input file

把微信中复制的聊天文本粘贴到 `posts.txt`，确保其中包含 `mp://...` 链接。

Paste copied chat text into `posts.txt` and make sure it includes `mp://...` links.

### 3. 打开微信并定位到合适会话 | Open WeChat and choose a chat

运行脚本前建议：

Before running the script:

1. 打开 PC 微信并保持前台可操作。
1. Open PC WeChat and keep it available in the foreground.
2. 切到一个可发送消息的会话（通常可用文件传输助手）。
2. Switch to a chat where messages can be sent (File Transfer Assistant is commonly used).

### 4. 运行脚本 | Run the script

```bash
python spider_by_links.py
```

脚本会：

The script will:

1. 读取 `posts.txt`。
1. Read `posts.txt`.
2. 从 `result/ocount.txt` 读取断点位置（支持中断后继续跑）。
2. Read resume index from `result/ocount.txt` (supports restart from breakpoints).
3. 逐条发送链接并尝试打开小程序窗口。
3. Send each link and try to open the mini program window.
4. 抓取可见文本，判断是否包含 `SAVE_KEYWORD`。
4. Capture visible text and check whether it contains `SAVE_KEYWORD`.
5. 命中则在 `result/` 下写入对应 `帖子_序号_标题.txt`。
5. Save matched results as `帖子_序号_标题.txt` under `result/`.

## 输出说明 | Output

- 控制台会显示每条链接的处理状态：`命中` 或 `未命中`。
- Console status per link: `命中` (matched) or `未命中` (not matched).
- 命中后输出文件中会包含：
- Matched output files include:
  - 帖子标题 / Post title
  - 链接 / Link
  - 抓取时间 / Capture time
  - 过滤后的文本内容 / Filtered text content

## 常见问题 | FAQ

### 找不到微信窗口 | WeChat window not found

- 确保 PC 微信已打开且窗口标题包含“微信”或“WeChat”。
- Make sure PC WeChat is open and window title contains "微信" or "WeChat".

### 链接发送了但没抓到内容 | Link sent but no content captured

- 提高 `WAIT_APP_POPUP` 和 `WAIT_AFTER_APP_FOCUS`。
- Increase `WAIT_APP_POPUP` and `WAIT_AFTER_APP_FOCUS`.
- 保证运行期间不要频繁切换焦点窗口。
- Avoid switching focus between windows while the script is running.

### 误判或漏判 | False positives / misses

- 当前是按文本是否包含 `SAVE_KEYWORD` 进行匹配。
- Matching is currently based on whether text contains `SAVE_KEYWORD`.
- 可把关键字设得更精确，或后续增加更严格的匹配规则。
- Use a more specific keyword or add stricter matching rules later.

## 注意 | Notes

- 本项目是个人效率工具，请在合规和不影响他人的前提下使用。
- This project is a personal productivity tool. Use it responsibly and in compliance with relevant rules.
- 小程序界面结构变化可能导致自动化定位失效，需要按实际情况微调参数或逻辑。
- UI changes in the mini program may break automation selectors; adjust parameters or logic as needed.
