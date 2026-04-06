# 配置文件：统一管理可调参数

WECHAT_WINDOW_KEYWORDS = ["微信", "WeChat"]
FILE_HELPER_NAME = "文件传输助手"
APP_WINDOW_TITLE = "校园集市APP"

LINK_PREFIX = "mp://"
SAVE_KEYWORD = "怪怪"
RESULT_DIR = "result"

WAIT_AFTER_FOCUS = 0.1
WAIT_AFTER_SEND = 0.01
WAIT_APP_POPUP = 0.01
WAIT_AFTER_APP_FOCUS = 0.01
WAIT_AFTER_CLOSE_APP = 0.01

# 小程序打开后，先进行高速连拍抓取，尽量拿到短暂出现的正文
INITIAL_CAPTURE_BURST_COUNT = 10
INITIAL_CAPTURE_BURST_INTERVAL = 0.01

APP_CAPTURE_ROUNDS = 1
APP_WINDOW_FIND_RETRIES = 12
APP_WINDOW_FIND_INTERVAL = 0.35

SKIP_TEXT_KEYWORDS = [
    "最小化", "最大化", "关闭", "返回", "转发", "收藏", "投诉", "更多",
    "Page-Frame", "AppIndex", "搜索", "消息", "通讯录"
]

BLOCK_TEXT_KEYWORDS = [
    "人机身份验证",
    "请求太频繁",
    "请稍后再试",
]

# 帖子数据文件：使用聊天记录文本格式（txt）
POSTS_FILE = "posts.txt"