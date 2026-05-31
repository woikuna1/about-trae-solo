import pyautogui
import time
import json
import os
import sys
import threading
from datetime import datetime

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

STOP_EVENT = threading.Event()
RECORD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")


def ensure_record_dir():
    os.makedirs(RECORD_DIR, exist_ok=True)


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


def scroll(amount):
    pyautogui.scroll(amount)


def wait(seconds):
    time.sleep(seconds)


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


def save_recording(name, actions, loop_interval=2.0):
    ensure_record_dir()
    filepath = os.path.join(RECORD_DIR, f"{name}.json")
    data = {
        "name": name,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "loop_interval": loop_interval,
        "actions": actions,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] 录制 '{name}' 已保存到 {filepath}")
    return filepath


def load_recording(name):
    filepath = os.path.join(RECORD_DIR, f"{name}.json")
    if not os.path.exists(filepath):
        print(f"[错误] 录制 '{name}' 不存在: {filepath}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def list_recordings():
    ensure_record_dir()
    files = [f for f in os.listdir(RECORD_DIR) if f.endswith(".json")]
    if not files:
        print("[信息] 暂无录制记录。")
        return []
    recordings = []
    for f in sorted(files):
        filepath = os.path.join(RECORD_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            recordings.append(data)
        except (json.JSONDecodeError, KeyError):
            recordings.append({"name": f[:-5], "created": "未知", "actions": [], "loop_interval": 2.0})
    return recordings


def delete_recording(name):
    filepath = os.path.join(RECORD_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"[删除] 录制 '{name}' 已删除。")
    else:
        print(f"[错误] 录制 '{name}' 不存在。")


def show_recordings():
    recordings = list_recordings()
    if not recordings:
        return
    print()
    print("=" * 60)
    print("  已保存的录制记录")
    print("=" * 60)
    for i, rec in enumerate(recordings, 1):
        action_count = len(rec.get("actions", []))
        loop_interval = rec.get("loop_interval", 2.0)
        created = rec.get("created", "未知")
        print(f"  [{i}] {rec['name']}")
        print(f"      创建时间: {created} | 操作数: {action_count} | 循环间隔: {loop_interval}s")
    print("=" * 60)
    print()


def record_actions():
    from pynput import mouse, keyboard

    actions = []
    last_time = time.time()
    stop_recording = threading.Event()

    def add_wait():
        nonlocal last_time
        now = time.time()
        elapsed = round(now - last_time, 3)
        if elapsed > 0.05:
            actions.append({"action": "wait", "params": {"seconds": elapsed}})
        last_time = now

    def on_click(x, y, button, pressed):
        if stop_recording.is_set():
            return False
        if pressed:
            add_wait()
            btn = "left" if button == mouse.Button.left else "right" if button == mouse.Button.right else "middle"
            actions.append({"action": "click", "params": {"x": x, "y": y, "button": btn}})
            print(f"  [录制] 点击 ({x}, {y}) {btn}")

    def on_scroll(x, y, dx, dy):
        if stop_recording.is_set():
            return False
        add_wait()
        actions.append({"action": "scroll", "params": {"amount": dy}})
        print(f"  [录制] 滚动 {dy}")

    def on_press(key):
        if stop_recording.is_set():
            return False
        if key == keyboard.Key.esc:
            print("  [录制] 检测到 ESC，停止录制...")
            stop_recording.set()
            return False
        add_wait()
        try:
            char = key.char
            actions.append({"action": "type_text", "params": {"text": char, "interval": 0.02}})
            print(f"  [录制] 输入字符: {char}")
        except AttributeError:
            key_name = str(key).replace("Key.", "")
            if key_name in ("ctrl_l", "ctrl_r"):
                key_name = "ctrl"
            elif key_name in ("alt_l", "alt_r"):
                key_name = "alt"
            elif key_name in ("shift_l", "shift_r"):
                key_name = "shift"
            actions.append({"action": "press_key", "params": {"key": key_name}})
            print(f"  [录制] 按键: {key_name}")

    print()
    print("=" * 60)
    print("  录制模式")
    print("=" * 60)
    print("  鼠标点击、滚动和键盘操作都会被记录")
    print("  按 ESC 停止录制")
    print("=" * 60)
    print()

    countdown = 3
    print(f"  {countdown} 秒后开始录制...")
    for i in range(countdown, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("  录制开始！按 ESC 停止。")
    print()

    last_time = time.time()

    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()

    mouse_listener.join()
    keyboard_listener.join()

    if not actions:
        print("[信息] 未录制到任何操作。")
        return None

    print(f"\n[录制完成] 共录制 {len(actions)} 个操作。")
    return actions


def manual_create():
    print()
    print("=" * 60)
    print("  手动创建操作序列")
    print("=" * 60)
    print("  支持的动作:")
    print("    1. click       - 鼠标点击 (x, y, button)")
    print("    2. double_click- 双击 (x, y)")
    print("    3. right_click - 右键点击 (x, y)")
    print("    4. move_to     - 移动鼠标 (x, y, duration)")
    print("    5. drag_to     - 拖拽 (x, y, duration)")
    print("    6. type_text   - 输入文字 (text, interval)")
    print("    7. press_key   - 按键 (key)")
    print("    8. hotkey      - 组合键 (keys列表)")
    print("    9. scroll      - 滚动 (amount)")
    print("    10. wait       - 等待 (seconds)")
    print("    输入 'done' 完成编辑")
    print("    输入 'undo' 撤销上一步")
    print("=" * 60)
    print()

    actions = []

    while True:
        cmd = input("  动作类型 (1-10/done/undo): ").strip().lower()
        if cmd == "done":
            break
        if cmd == "undo":
            if actions:
                removed = actions.pop()
                print(f"  [撤销] 移除: {removed}")
            else:
                print("  [提示] 没有可撤销的操作。")
            continue

        action_map_input = {
            "1": "click", "2": "double_click", "3": "right_click",
            "4": "move_to", "5": "drag_to", "6": "type_text",
            "7": "press_key", "8": "hotkey", "9": "scroll", "10": "wait",
        }
        action_name = action_map_input.get(cmd)
        if not action_name:
            print("  [错误] 无效选择，请重新输入。")
            continue

        try:
            if action_name == "click":
                x = int(input("  x: "))
                y = int(input("  y: "))
                button = input("  button (left/right/middle, 默认left): ").strip() or "left"
                actions.append({"action": "click", "params": {"x": x, "y": y, "button": button}})

            elif action_name == "double_click":
                x = int(input("  x: "))
                y = int(input("  y: "))
                actions.append({"action": "double_click", "params": {"x": x, "y": y}})

            elif action_name == "right_click":
                x = int(input("  x: "))
                y = int(input("  y: "))
                actions.append({"action": "right_click", "params": {"x": x, "y": y}})

            elif action_name == "move_to":
                x = int(input("  x: "))
                y = int(input("  y: "))
                duration = float(input("  duration (默认0.3): ").strip() or "0.3")
                actions.append({"action": "move_to", "params": {"x": x, "y": y, "duration": duration}})

            elif action_name == "drag_to":
                x = int(input("  x: "))
                y = int(input("  y: "))
                duration = float(input("  duration (默认0.5): ").strip() or "0.5")
                actions.append({"action": "drag_to", "params": {"x": x, "y": y, "duration": duration}})

            elif action_name == "type_text":
                text = input("  text: ")
                interval = float(input("  interval (默认0.05): ").strip() or "0.05")
                actions.append({"action": "type_text", "params": {"text": text, "interval": interval}})

            elif action_name == "press_key":
                key = input("  key (如 enter, tab, space, esc): ").strip()
                actions.append({"action": "press_key", "params": {"key": key}})

            elif action_name == "hotkey":
                keys_str = input("  keys (逗号分隔, 如 ctrl,c): ").strip()
                keys = [k.strip() for k in keys_str.split(",")]
                actions.append({"action": "hotkey", "params": {"keys": keys}})

            elif action_name == "scroll":
                amount = int(input("  amount (正数向上,负数向下): "))
                actions.append({"action": "scroll", "params": {"amount": amount}})

            elif action_name == "wait":
                seconds = float(input("  seconds: "))
                actions.append({"action": "wait", "params": {"seconds": seconds}})

            print(f"  [添加] {actions[-1]}")
        except (ValueError, EOFError):
            print("  [错误] 输入无效，请重试。")
            continue

    if not actions:
        print("[信息] 未添加任何操作。")
        return None

    print(f"\n[完成] 共 {len(actions)} 个操作。")
    return actions


def run_once(actions):
    for i, step in enumerate(actions):
        if STOP_EVENT.is_set():
            return False
        action = step["action"]
        params = step["params"]
        print(f"  [{i+1}/{len(actions)}] {action} {params}")
        handler = ACTION_MAP.get(action)
        if handler:
            handler(params)
        else:
            print(f"  [警告] 未知动作: {action}")
    return True


def execute_recording(recording):
    name = recording.get("name", "未命名")
    actions = recording.get("actions", [])
    loop_interval = recording.get("loop_interval", 2.0)

    if not actions:
        print("[错误] 该录制没有操作。")
        return

    STOP_EVENT.clear()

    print()
    print("=" * 60)
    print(f"  执行录制: {name}")
    print("=" * 60)
    print(f"  操作数: {len(actions)}")
    print(f"  循环间隔: {loop_interval}s")
    print(f"  安全退出: Ctrl+C 或鼠标移至屏幕角落")
    print("=" * 60)
    print()

    countdown = 5
    print(f"  {countdown} 秒后开始执行，请切换到目标窗口...")
    for i in range(countdown, 0, -1):
        if STOP_EVENT.is_set():
            return
        print(f"  {i}...")
        time.sleep(1)
    print("  开始执行！")
    print()

    round_num = 0
    try:
        while not STOP_EVENT.is_set():
            round_num += 1
            print(f"--- 第 {round_num} 轮 ---")
            completed = run_once(actions)
            if not completed:
                break
            print(f"--- 第 {round_num} 轮完成 ---")
            print()
            if loop_interval > 0:
                STOP_EVENT.wait(timeout=loop_interval)
    except KeyboardInterrupt:
        print("\n[停止] 收到 Ctrl+C，退出。")
    except pyautogui.FailSafeException:
        print("\n[停止] 触发安全退出（鼠标移至屏幕角落），退出。")

    print(f"共执行了 {round_num} 轮。")


def select_and_run():
    recordings = list_recordings()
    if not recordings:
        return

    show_recordings()

    try:
        choice = input("  选择要执行的录制编号 (或输入名称, q取消): ").strip()
        if choice.lower() == "q":
            return

        selected = None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(recordings):
                selected = recordings[idx]
        else:
            for rec in recordings:
                if rec["name"] == choice:
                    selected = rec
                    break

        if not selected:
            print("[错误] 无效选择。")
            return

        execute_recording(selected)

    except (ValueError, EOFError):
        print("[错误] 输入无效。")


def main():
    while True:
        print()
        print("=" * 60)
        print("  鼠标键盘自动化工具")
        print("=" * 60)
        print("  1. 录制操作 (实时录制鼠标键盘)")
        print("  2. 手动创建操作序列")
        print("  3. 查看已保存的录制")
        print("  4. 执行录制")
        print("  5. 删除录制")
        print("  6. 退出")
        print("=" * 60)

        try:
            choice = input("  请选择 (1-6): ").strip()
        except EOFError:
            break

        if choice == "1":
            actions = record_actions()
            if actions:
                name = input("  保存名称: ").strip()
                if not name:
                    name = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    loop_interval = float(input("  循环间隔秒数 (默认2.0): ").strip() or "2.0")
                except ValueError:
                    loop_interval = 2.0
                save_recording(name, actions, loop_interval)

        elif choice == "2":
            actions = manual_create()
            if actions:
                name = input("  保存名称: ").strip()
                if not name:
                    name = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    loop_interval = float(input("  循环间隔秒数 (默认2.0): ").strip() or "2.0")
                except ValueError:
                    loop_interval = 2.0
                save_recording(name, actions, loop_interval)

        elif choice == "3":
            show_recordings()

        elif choice == "4":
            select_and_run()

        elif choice == "5":
            show_recordings()
            name = input("  要删除的录制名称: ").strip()
            if name:
                delete_recording(name)

        elif choice == "6":
            print("再见！")
            break
        else:
            print("[错误] 无效选择。")


if __name__ == "__main__":
    main()
