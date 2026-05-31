import pyautogui
import time
import sys
import threading

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

STOP_EVENT = threading.Event()


def listen_for_stop():
    print("[停止监听] 按下 Ctrl+C 停止脚本...")
    try:
        while not STOP_EVENT.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    STOP_EVENT.set()
    print("\n[停止] 收到停止信号，正在退出...")


def click(x, y, button="left", clicks=1, interval=0.1):
    pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)


def double_click(x, y):
    pyautogui.doubleClick(x=x, y=y)


def right_click(x, y):
    pyautogui.rightClick(x=x, y=y)


def move_to(x, y, duration=0.3):
    pyautogui.moveTo(x=x, y=y, duration=duration)


def drag_to(x, y, duration=0.5, button="left"):
    pyautogui.dragTo(x=x, y=y, duration=duration, button=button)


def type_text(text, interval=0.05):
    pyautogui.typewrite(text, interval=interval)


def press_key(key):
    pyautogui.press(key)


def hotkey(*keys):
    pyautogui.hotkey(*keys)


def wait(seconds):
    time.sleep(seconds)


def scroll(amount):
    pyautogui.scroll(amount)


ACTIONS = [
    # ========== 在这里定义你的操作序列 ==========
    # 格式: (动作名, 参数字典)
    #
    # 支持的动作:
    #   ("click",       {"x": 100, "y": 200})
    #   ("click",       {"x": 100, "y": 200, "button": "right"})
    #   ("double_click",{"x": 100, "y": 200})
    #   ("right_click", {"x": 100, "y": 200})
    #   ("move_to",     {"x": 100, "y": 200, "duration": 0.3})
    #   ("drag_to",     {"x": 500, "y": 300, "duration": 0.5})
    #   ("type_text",   {"text": "hello world", "interval": 0.05})
    #   ("press_key",   {"key": "enter"})
    #   ("press_key",   {"key": "tab"})
    #   ("hotkey",      {"keys": ["ctrl", "c"]})
    #   ("hotkey",      {"keys": ["ctrl", "v"]})
    #   ("scroll",      {"amount": 3})
    #   ("wait",        {"seconds": 1.0})
    #
    # ===== 示例流程（请替换为你自己的操作）=====

    ("click",       {"x": 500, "y": 300}),
    ("wait",        {"seconds": 0.5}),
    ("click",       {"x": 600, "y": 400}),
    ("wait",        {"seconds": 0.5}),
    ("hotkey",      {"keys": ["ctrl", "a"]}),
    ("wait",        {"seconds": 0.3}),
    ("hotkey",      {"keys": ["ctrl", "c"]}),
    ("wait",        {"seconds": 0.3}),
    ("click",       {"x": 700, "y": 500}),
    ("wait",        {"seconds": 0.5}),
    ("hotkey",      {"keys": ["ctrl", "v"]}),
    ("wait",        {"seconds": 0.3}),
    ("press_key",   {"key": "enter"}),
    ("wait",        {"seconds": 1.0}),

    # ===== 示例结束 =====
]

ACTION_MAP = {
    "click": lambda p: click(**p),
    "double_click": lambda p: double_click(**p),
    "right_click": lambda p: right_click(**p),
    "move_to": lambda p: move_to(**p),
    "drag_to": lambda p: drag_to(**p),
    "type_text": lambda p: type_text(**p),
    "press_key": lambda p: press_key(**p),
    "hotkey": lambda p: hotkey(*p["keys"]),
    "scroll": lambda p: scroll(**p),
    "wait": lambda p: wait(**p),
}

LOOP_INTERVAL = 2.0


def run_once():
    for i, (action, params) in enumerate(ACTIONS):
        if STOP_EVENT.is_set():
            return False
        print(f"  [{i+1}/{len(ACTIONS)}] {action} {params}")
        handler = ACTION_MAP.get(action)
        if handler:
            handler(params)
        else:
            print(f"  [警告] 未知动作: {action}")
    return True


def main():
    print("=" * 50)
    print("  鼠标键盘自动化脚本")
    print("=" * 50)
    print(f"  操作序列: {len(ACTIONS)} 步")
    print(f"  循环间隔: {LOOP_INTERVAL} 秒")
    print(f"  安全退出: Ctrl+C 或将鼠标移至屏幕角落")
    print("=" * 50)
    print()

    countdown = 5
    print(f"  {countdown} 秒后开始执行，请切换到目标窗口...")
    for i in range(countdown, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("  开始执行！")
    print()

    stop_thread = threading.Thread(target=listen_for_stop, daemon=True)
    stop_thread.start()

    round_num = 0
    try:
        while not STOP_EVENT.is_set():
            round_num += 1
            print(f"--- 第 {round_num} 轮 ---")
            completed = run_once()
            if not completed:
                break
            print(f"--- 第 {round_num} 轮完成 ---")
            print()
            if LOOP_INTERVAL > 0:
                STOP_EVENT.wait(timeout=LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("\n[停止] 收到 Ctrl+C，退出。")
    except pyautogui.FailSafeException:
        print("\n[停止] 触发安全退出（鼠标移至屏幕角落），退出。")

    print(f"共执行了 {round_num} 轮。")


if __name__ == "__main__":
    main()
