import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading


# 监控相关配置
TELEGRAM_BOT_TOKEN = '你的 Telegram Bot Token'  # 替换为你的 Telegram Bot Token
TELEGRAM_CHAT_ID = '你的 Chat ID'      # 替换为你的 Chat ID
last_number = 170000

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    requests.post(url, data=data)

import time

last_check_time = 0  # 记录上次检查的时间

def check_serv00():
    global last_number, last_check_time
    try:
        current_time = time.time()  # 获取当前时间戳
        
        # 检查是否距离上次变化检查已经超过24小时
        if last_check_time > 0 and current_time - last_check_time < 24 * 60 * 60:
            return  # 如果没有超过24小时，则返回
        
        # 等待页面加载
        time.sleep(5)  # 等待5秒，确保页面加载完成
        
        response = requests.get('https://serv00.com')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有符合条件的元素
        users_elements = soup.select('.button.is-large.is-flexible')
        if len(users_elements) > 1:  # 确保有第二个元素
            users_element = users_elements[1]  # 获取第二个元素
            # 查找包含数字的文本
            text_content = users_element.get_text(strip=True)
            # 使用更精确的方式提取数字
            import re
            numbers = re.findall(r'(\d+)\s*/\s*\d+', text_content)
            if numbers:
                current_number = int(numbers[0])
                print(f"当前用户数量: {current_number}")
                
                if last_number is not None and current_number != last_number:
                    if current_number > last_number:
                        message = f'Serv00用户数量发生变化：从 {last_number} 增加到 {current_number}，新增 {current_number - last_number} 位用户'
                    elif current_number < last_number:
                        message = f'Serv00用户数量发生变化：从 {last_number} 减少到 {current_number}，减少 {last_number - current_number} 位用户'
                    else:
                        message = f'Serv00用户数量发生变化：从 {last_number} 变为 {current_number}'
                    print(message)
                    send_telegram_message(message)
                    
                    last_check_time = current_time  # 更新上次变化检查时间
                
                last_number = current_number
            else:
                print(f"未找到用户数量，页面内容: {text_content}")
        else:
            print("未找到第二个用户数量元素")
    except Exception as e:
        print(f'监控错误: {str(e)}')

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# ... existing code ...

# 设置定时任务
schedule.every(5).minutes.do(check_serv00)

# 立即执行一次检查
check_serv00()

# 在新线程中运行定时任务
monitoring_thread = threading.Thread(target=run_schedule, daemon=True)
monitoring_thread.start()

# 添加以下代码，保持主线程运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("程序已停止")
