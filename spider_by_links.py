import uiautomation as auto
import time
import os
import re
from config import (
    WECHAT_WINDOW_KEYWORDS,
    FILE_HELPER_NAME,
    APP_WINDOW_TITLE,
    LINK_PREFIX,
    SAVE_KEYWORD,
    RESULT_DIR,
    WAIT_AFTER_FOCUS,
    WAIT_AFTER_SEND,
    WAIT_APP_POPUP,
    WAIT_AFTER_APP_FOCUS,
    WAIT_AFTER_CLOSE_APP,
    APP_CAPTURE_ROUNDS,
    APP_WINDOW_FIND_RETRIES,
    APP_WINDOW_FIND_INTERVAL,
    SKIP_TEXT_KEYWORDS,
    POSTS_FILE,
)


def collect_all_text(ctrl, max_depth=30):
    """从控件树中递归提取所有文本"""
    results = []
    seen = set()

    def walk(c, depth):
        if depth > max_depth:
            return
        try:
            text = str(c.Name).strip() if c.Name else ""
            if text and text not in seen and len(text) > 0:
                results.append(text)
                seen.add(text)
        except:
            pass
        try:
            for child in c.GetChildren():
                walk(child, depth + 1)
        except:
            pass

    walk(ctrl, 0)
    return results


def safe_filename(text):
    """清理文件名中的非法字符"""
    cleaned = re.sub(r'[\\/:*?"<>|\r\n]+', '_', text).strip()
    return cleaned or "untitled"


def load_posts(file_path):
    """读取聊天文本格式的帖子列表，返回 [(title, link), ...]"""
    if not os.path.exists(file_path):
        print(f"✗ 未找到帖子文件: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except Exception as e:
        print(f"✗ 读取帖子文件失败: {e}")
        return []

    posts = []
    # 聊天文本格式：按 mp:// 链接位置切分标题
    link_pattern = re.compile(r'mp://[A-Za-z0-9]+')
    matches = list(link_pattern.finditer(raw_text))
    if not matches:
        return []

    prev_end = 0
    for m in matches:
        link = m.group(0).strip()
        segment = raw_text[prev_end:m.start()]

        # 取紧邻链接前的最后一段非空文本作为标题
        lines = [ln.strip() for ln in segment.replace('\r', '').split('\n') if ln.strip()]
        title = lines[-1] if lines else ""

        # 去掉聊天前缀（例如：okdl🤨: ）
        title = re.sub(r'^[^:\n]{1,40}:\s*', '', title).strip()
        # 规范空白
        title = re.sub(r'\s+', ' ', title).strip()

        if not title:
            title = f"未命名帖子_{len(posts) + 1:02d}"

        posts.append((title, link))
        prev_end = m.end()

    # 按文本原始顺序处理：从第一条到最后一条
    return posts


def find_window_by_exact_title(title, retries=10, interval=0.6):
    """按窗口标题精确查找顶级窗口，支持短时重试"""
    for _ in range(retries):
        root = auto.GetRootControl()
        for child in root.GetChildren():
            try:
                name = str(child.Name).strip() if child.Name else ""
                if name == title:
                    return child
            except:
                pass
        time.sleep(interval)
    return None


def collect_market_app_text(app_window, rounds=1, click_before_capture=False):
    """从“校园集市APP”窗口抓取可见文本，并翻页收集更多内容"""
    merged = []
    seen = set()

    for i in range(rounds):
        # 默认不进行二次点击，避免进入链接后再次触发页面交互。
        if click_before_capture:
            try:
                rect = app_window.BoundingRectangle
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                auto.Click(center_x, center_y)
            except:
                pass

        texts = collect_all_text(app_window)
        added = 0
        for t in texts:
            text = t.strip()
            # 过滤空文本和明显的系统控件标识
            if not text:
                continue
            if text in ["", "0", "1", "2", "3"]:
                continue
            if text not in seen:
                seen.add(text)
                merged.append(text)
                added += 1

        # 最后一轮不滚动
        if i < rounds - 1:
            try:
                auto.SendKeys('{PageDown}')
            except:
                # 某些环境下特殊键名兼容性差，降级为向下键多次
                for _ in range(6):
                    auto.SendKeys('{Down}')
                    time.sleep(0.05)
            time.sleep(1.1)

    return merged


def find_and_click_link(ctrl, link_text, max_depth=20):
    """在右侧聊天区中搜索包含指定链接文本的控件并点击，避免误点会话列表"""
    link_id = link_text.replace("mp://", "")
    candidates = []

    try:
        root_rect = ctrl.BoundingRectangle
    except:
        root_rect = None

    def in_chat_pane(c_rect):
        """只接受右侧聊天区域控件，过滤左侧会话列表"""
        if not root_rect or not c_rect:
            return True
        width = root_rect.right - root_rect.left
        boundary_x = root_rect.left + int(width * 0.35)
        center_x = (c_rect.left + c_rect.right) // 2
        return center_x >= boundary_x

    def search(c, depth):
        if depth > max_depth:
            return
        try:
            name = str(c.Name).strip() if c.Name else ""
            if name and (link_id in name or link_text in name):
                c_rect = c.BoundingRectangle
                if "文件传输助手" not in name and in_chat_pane(c_rect):
                    candidates.append((c_rect.bottom, c, name))
        except:
            pass
        try:
            for child in c.GetChildren():
                search(child, depth + 1)
        except:
            pass

    search(ctrl, 0)

    if not candidates:
        return False

    # 优先点击最靠下的一条（通常是刚发出的最新消息）
    candidates.sort(key=lambda x: x[0], reverse=True)
    _, target_ctrl, target_name = candidates[0]
    target_ctrl.Click()
    return True


def read_resume_index(counter_path, total_posts):
    """读取断点序号，返回 1-based 起始下标"""
    if not os.path.exists(counter_path):
        return 1
    try:
        with open(counter_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        idx = int(text)
        if idx < 1:
            return 1
        if idx > total_posts:
            return total_posts
        return idx
    except:
        return 1


def write_resume_index(counter_path, idx):
    """写入当前处理到的帖子序号（1-based）"""
    with open(counter_path, 'w', encoding='utf-8') as f:
        f.write(str(idx))


posts = load_posts(POSTS_FILE)
if not posts:
    print(f"✗ 帖子列表为空，请检查 {POSTS_FILE}")
    exit(1)

# ========== 找到微信窗口 ==========
root = auto.GetRootControl()
wechat_window = None

for child in root.GetChildren():
    try:
        name = child.Name
        if name and any(kw in name for kw in WECHAT_WINDOW_KEYWORDS):
            wechat_window = child
            break
    except:
        pass

if not wechat_window:
    print("✗ 未找到微信窗口，请先打开微信")
    exit(1)

# ========== 处理每个帖子链接 ==========
success_count = 0

result_dir = RESULT_DIR
os.makedirs(result_dir, exist_ok=True)
counter_file = os.path.join(result_dir, 'ocount.txt')
start_idx = read_resume_index(counter_file, len(posts))

for idx, (title, link) in enumerate(posts[start_idx - 1:], start_idx):
    write_resume_index(counter_file, idx)
    hit = False

    # 只处理以 mp:// 开头的链接
    if not isinstance(link, str) or not link.startswith(LINK_PREFIX):
        print(f"[{idx}/{len(posts)}] 未命中")
        continue

    try:
        # 点击输入框区域（微信窗口底部）
        rect = wechat_window.BoundingRectangle
        input_x = (rect.left + rect.right) // 2
        input_y = rect.bottom - 80
        auto.Click(input_x, input_y)
        time.sleep(0.12)

        # 全选清除输入框中可能残留的文字
        auto.SendKeys('{Ctrl}a')
        time.sleep(0.05)
        auto.SendKeys('{Delete}')
        time.sleep(0.05)

        # 粘贴链接并发送
        auto.SetClipboardText(link)
        time.sleep(0.08)
        auto.SendKeys('{Ctrl}v')
        time.sleep(0.18)
        auto.SendKeys('{Return}')
        time.sleep(WAIT_AFTER_SEND)  # 等待消息发送完成

        # ====== 关键步骤：点击刚发送的链接 ======
        clicked = find_and_click_link(wechat_window, link)

        if not clicked:
            # 备用方案：点击右侧聊天区域最下方的消息位置，避免点到左侧会话列表
            msg_x = rect.left + int((rect.right - rect.left) * 0.75)
            msg_y = rect.bottom - 180
            auto.Click(msg_x, msg_y)

        time.sleep(WAIT_APP_POPUP)  # 等待小程序窗口弹出

        # ====== 抓取“校园集市APP”窗口内容 ======
        app_window = find_window_by_exact_title(
            APP_WINDOW_TITLE,
            retries=APP_WINDOW_FIND_RETRIES,
            interval=APP_WINDOW_FIND_INTERVAL,
        )
        if not app_window:
            print(f"[{idx}/{len(posts)}] 未命中")
            continue

        app_window.SetFocus()
        time.sleep(WAIT_AFTER_APP_FOCUS)

        all_texts = collect_market_app_text(app_window, rounds=APP_CAPTURE_ROUNDS)

        # 过滤掉明显非正文控件词
        skip_keywords = SKIP_TEXT_KEYWORDS
        filtered = [
            t for t in all_texts
            if t and not any(k in t for k in skip_keywords)
        ]

        keyword = SAVE_KEYWORD
        content_text = "\n".join(filtered)
        if keyword in content_text:
            filename = f"帖子_{idx:02d}_{safe_filename(title)}.txt"
            filepath = os.path.join(result_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== {title} ===\n")
                f.write(f"链接: {link}\n")
                f.write(f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                for i, t in enumerate(filtered, 1):
                    f.write(f"{i}. {t}\n")

            hit = True
            success_count += 1

        # 返回聊天界面（关闭小程序）
        app_window.SetFocus()
        time.sleep(0.1)
        auto.SendKeys('{Escape}')
        time.sleep(WAIT_AFTER_CLOSE_APP)
        wechat_window.SetFocus()
        time.sleep(0.12)

    except Exception:
        time.sleep(0.2)

    print(f"[{idx}/{len(posts)}] {'命中' if hit else '未命中'}")

