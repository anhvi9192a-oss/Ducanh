import telebot 
import requests 
import random 
import string 
import json 
import os 
import subprocess
import sys
import psutil
from datetime import datetime, timedelta 
 
# --- CẤU HÌNH --- 
API_TOKEN = '7865551342:AAGhXB7flKN07hH1rGd8OvIAIv0n6PzCKjo'  
ADMIN_ID = 7782382498 # ID Admin tối cao (Admin 9)
BASE_URL = "http://180.93.52.41:2010"  
GIFT_FILE = "giftcode.json" 
BOT_CHILD_FILE = "active_bots.json"
 
bot = telebot.TeleBot(API_TOKEN) 
 
# --- HÀM HỖ TRỢ DỮ LIỆU --- 
def load_data(file_name): 
    if not os.path.exists(file_name): 
        return [] 
    try: 
        with open(file_name, "r", encoding="utf-8") as f: 
            data = json.load(f) 
            return data if isinstance(data, list) else [] 
    except: 
        return [] 
 
def save_data(file_name, data): 
    with open(file_name, "w", encoding="utf-8") as f: 
        json.dump(data, f, indent=4, ensure_ascii=False) 
 
# --- XỬ LÝ LỆNH CHO BOT CHÍNH --- 
@bot.message_handler(func=lambda message: True) 
def handle_commands(message): 
    msg_text = message.text.strip() 
    if not msg_text or not msg_text.startswith("/"): return 
     
    parts = msg_text.split() 
    cmd = parts[0].lower() 
    uid_sender = message.from_user.id 
 
    # KIỂM TRA QUYỀN ADMIN TỔNG (ID 9)
    if uid_sender != ADMIN_ID: 
        bot.reply_to(message, "❌ Bạn không có quyền Admin để thực hiện lệnh này.")
        return 

# FILE: bot.py

    # LỆNH /THEMACCAPI - Thêm tài khoản để tự động lấy token
    elif cmd == "/themaccapi":
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ **Cú pháp:** `/themaccapi [uid] [password]`\nVí dụ: `/themaccapi 100012345 pass123`", parse_mode="Markdown")
            return

        uid_new = parts[1]
        pw_new = parts[2]
        file_acc = "accounts.json"

        try:
            # Load dữ liệu cũ hoặc tạo mới nếu chưa có
            if os.path.exists(file_acc):
                with open(file_acc, "r", encoding="utf-8") as f:
                    accounts = json.load(f)
            else:
                accounts = []

            # Kiểm tra xem UID đã tồn tại chưa để tránh trùng lặp
            exists = False
            for acc in accounts:
                if acc['uid'] == uid_new:
                    acc['pw'] = pw_new  # Cập nhật pass mới nếu trùng UID
                    exists = True
                    break
            
            if not exists:
                accounts.append({"uid": uid_new, "pw": pw_new})

            # Lưu lại vào file
            with open(file_acc, "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=4)

            bot.reply_to(message, f"✅ **Thành công!**\nĐã thêm UID: `{uid_new}` vào danh sách tự động lấy token.", parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"❌ **Lỗi:** {str(e)}")

# LỆNH /LISTACCAPI - Xem danh sách tài khoản lấy token
    elif cmd == "/listaccapi":
        file_acc = "accounts.json"
        if not os.path.exists(file_acc):
            bot.reply_to(message, "📭 Danh sách tài khoản trống.")
            return

        try:
            with open(file_acc, "r", encoding="utf-8") as f:
                accounts = json.load(f)
            
            if not accounts:
                bot.reply_to(message, "📭 Không có tài khoản nào trong danh sách.")
                return

            txt = "📋 **DANH SÁCH ACC GET TOKEN:**\n"
            txt += "━━━━━━━━━━━━━━\n"
            for idx, acc in enumerate(accounts, 1):
                txt += f"{idx}. UID: `{acc['uid']}` | PW: `{acc['pw']}`\n"
            
            bot.reply_to(message, txt, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {str(e)}")

# LỆNH /XOAACCAPI - Xóa tài khoản khỏi danh sách
    elif cmd == "/xoaaccapi":
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ **Cú pháp:** `/xoaaccapi [uid]`")
            return

        uid_del = parts[1]
        file_acc = "accounts.json"
        
        try:
            if not os.path.exists(file_acc):
                bot.reply_to(message, "❌ File dữ liệu không tồn tại.")
                return

            with open(file_acc, "r", encoding="utf-8") as f:
                accounts = json.load(f)

            new_accounts = [acc for acc in accounts if str(acc['uid']) != str(uid_del)]

            if len(new_accounts) == len(accounts):
                bot.reply_to(message, f"❌ Không tìm thấy UID `{uid_del}` trong danh sách.")
            else:
                with open(file_acc, "w", encoding="utf-8") as f:
                    json.dump(new_accounts, f, indent=4)
                bot.reply_to(message, f"✅ Đã xóa UID `{uid_del}` thành công.")
                
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {str(e)}")
                                    
# 10. LỆNH /BIO
    elif cmd == "/bio":
        if len(parts) < 4:
            guide = (
                "⚠️ **Cú pháp thiếu tham số!**\n"
                "Sử dụng: `/bio [uid] [password] [nội dung bio]`\n"
                "Ví dụ: `/bio 1000123456789 pass123 Hello World`"
            )
            bot.reply_to(message, guide, parse_mode="Markdown")
            return

        uid_target = parts[1]
        pwd_target = parts[2]
        bio_content = " ".join(parts[3:])
        
        # --- ĐO ĐỘ DÀI NỘI DUNG BIO ---
        char_count = len(bio_content) 
        # ------------------------------

        sent_msg = bot.reply_to(message, f"⏳ **Đang thay đổi tiểu sử cho ID:** `{uid_target}`...")

        try:
            api_url = f"https://danger-long-bio.vercel.app/update_bio?uid={uid_target}&password={pwd_target}&bio={bio_content}"
            response = requests.get(api_url, timeout=20)
            
            if response.status_code == 200:
                # Giả sử API trả về tên tài khoản trong response.text
                account_name = response.text.strip()
                
                success_msg = (
                    f"✅ **ĐÃ ĐỔI BIO THÀNH CÔNG!**\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"👤 **Tên Acc:** `{account_name}`\n"
                    f"📝 **Độ dài:** `{char_count}/180` ký tự\n"
                    f"🆔 **UID:** `{uid_target}`\n"
                    f"✨ **Nội dung:** {bio_content}"
                )
                
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    text=success_msg,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    text=f"❌ **Lỗi:** API không phản hồi (Mã: `{response.status_code}`)"
                )
        except requests.exceptions.RequestException:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                text=f"❌ **Lỗi kết nối:** Không thể kết nối tới server Bio."
            )
            
 # 2. XỬ LÝ LỆNH /REG
# 2. XỬ LÝ LỆNH /REG
    if cmd == "/reg":
        if len(parts) < 6:
            guide = (
                "⚠️ **Cú pháp thiếu tham số!**\n"
                "Sử dụng: `/reg [số lượng] [tên] [pass] [luồng] [vùng]`\n"
                "Ví dụ: `/reg 10 quanghau pass123 5 VN`\n\n"
                "🌍 **Vùng:** ME, IND, ID, VN, TH, BD, PK, TW, CIS, SAC, BR"
            )
            bot.reply_to(message, guide, parse_mode="Markdown")
            return

        try:
            sl_str, ten, mk, luong, vung = parts[1], parts[2], parts[3], parts[4], parts[5].upper()
            num_to_take = int(sl_str)
            
            sent_msg = bot.reply_to(message, f"🚀 **Đang bắt đầu tạo {num_to_take} tài khoản vùng {vung}...**")

            # Gọi script generator chạy ngầm
            # RioRareCoupleGen.py cần nhận tham số qua sys.argv
            subprocess.run([sys.executable, "RioRareCoupleGen.py", sl_str, ten, mk, luong, vung], check=True)

            # Thư mục lưu trữ
            base_dir = "LUANORI-ERA"
            sub_dir = "ACCOUNTS" 
            path_to_check = os.path.join(base_dir, sub_dir)

            if os.path.exists(path_to_check):
                # Lấy danh sách file .json
                files = [os.path.join(path_to_check, f) for f in os.listdir(path_to_check) if f.endswith('.json')]
                
                if files:
                    # Lấy file có thời gian cập nhật mới nhất
                    latest_file = max(files, key=os.path.getmtime)
                
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Lấy đúng số lượng 'num_to_take' tài khoản cuối cùng trong danh sách
                    if isinstance(data, list):
                        new_accounts = data[-num_to_take:]
                    else:
                        new_accounts = [] # Trường hợp JSON không phải là list

                    # Xây dựng nội dung tin nhắn
                    acc_text = f"✅ **TẠO TÀI KHOẢN THÀNH CÔNG!**\n"
                    acc_text += f"━━━━━━━━━━━━━━\n"
                    acc_text += f"📍 Vùng: `{vung}` | 📊 SL: `{len(new_accounts)}` acc\n\n"
                    
                    for idx, acc in enumerate(new_accounts, 1):
                        # Tự động tìm key phù hợp (username/uid và password/pass)
                        user = acc.get('username') or acc.get('uid') or acc.get('id') or "N/A"
                        pwd = acc.get('password') or acc.get('pass') or "N/A"
                        acc_text += f"{idx}. `{user}|{pwd}`\n"
                    
                    # Kiểm tra độ dài tin nhắn tránh lỗi Telegram (max 4096 ký tự)
                    if len(acc_text) > 4000:
                        bot.send_message(message.chat.id, "⚠️ Danh sách quá dài, đang gửi file thay thế...")
                        with open(latest_file, 'rb') as f_send:
                            bot.send_document(message.chat.id, f_send)
                    else:
                        bot.send_message(message.chat.id, acc_text, parse_mode="Markdown")
                else:
                    bot.send_message(message.chat.id, "❌ Lỗi: Tiến trình xong nhưng không tìm thấy file dữ liệu.")
            else:
                bot.send_message(message.chat.id, f"❌ Lỗi: Thư mục `{sub_dir}` không tồn tại.")

        except subprocess.CalledProcessError:
            bot.reply_to(message, "❌ Lỗi: Script Generator gặp sự cố khi đang chạy.")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi hệ thống: {str(e)}")
         
    # LỆNH /CHECK - XEM TẤT CẢ TÀI KHOẢN TRONG FILE
    elif cmd == "/checkreg":
        base_dir = "LUANORI-ERA"
        sub_dir = "ACCOUNTS"
        path_to_check = os.path.join(base_dir, sub_dir)

        try:
            if os.path.exists(path_to_check):
                files = [os.path.join(path_to_check, f) for f in os.listdir(path_to_check) if f.endswith('.json')]
                
                if files:
                    latest_file = max(files, key=os.path.getmtime)
                    file_name = os.path.basename(latest_file)

                    # Đọc file (json đã được import ở đầu file nên sẽ không lỗi nữa)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if isinstance(data, list) and len(data) > 0:
                        total_acc = len(data)
                        acc_text = f"📂 **DANH SÁCH TÀI KHOẢN**\n"
                        acc_text += f"━━━━━━━━━━━━━━\n"
                        acc_text += f"📄 File: `{file_name}`\n"
                        acc_text += f"📊 Tổng cộng: `{total_acc}` acc\n\n"

                        for idx, acc in enumerate(data, 1):
                            user = acc.get('username') or acc.get('uid') or acc.get('id') or "N/A"
                            pwd = acc.get('password') or acc.get('pass') or "N/A"
                            acc_text += f"{idx}. `{user}|{pwd}`\n"

                        if len(acc_text) > 4000:
                            bot.send_message(message.chat.id, f"⚠️ Danh sách quá dài ({total_acc} acc), đang gửi file thay thế.")
                            with open(latest_file, 'rb') as f_send:
                                bot.send_document(message.chat.id, f_send)
                        else:
                            bot.send_message(message.chat.id, acc_text, parse_mode="Markdown")
                    else:
                        bot.send_message(message.chat.id, "❌ File JSON rỗng hoặc không đúng cấu trúc.")
                else:
                    bot.send_message(message.chat.id, "❌ Không tìm thấy file .json nào.")
            else:
                bot.send_message(message.chat.id, "❌ Thư mục lưu trữ không tồn tại.")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {str(e)}")
            
    # 1. LỆNH /GEN (Bot chính)
    if cmd == "/gen": 
        if len(parts) != 3: 
            bot.reply_to(message, "⚠️ Cú pháp: `/gen [số ngày] [số lượt]`") 
            return 
        try: 
            days, max_uses = int(parts[1]), int(parts[2]) 
            expire_str = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S") 
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) 
            gifts = load_data(GIFT_FILE) 
            gifts.append({"code": code, "time": f"{days}d", "expire_date": expire_str, "max_uses": max_uses, "current_uses": 0}) 
            save_data(GIFT_FILE, gifts) 
            bot.reply_to(message, f"✅ **Code:** `{code}`\n📅 **Hạn:** {days} ngày\n👥 **Lượt:** {max_uses}", parse_mode="Markdown")
        except: bot.reply_to(message, "❌ Lỗi định dạng số.") 
 
    # 2. LỆNH /ADDBOT 
    elif cmd == "/addbot": 
        if len(parts) != 2: 
            bot.reply_to(message, "⚠️ Cú pháp: `/addbot [token]`") 
            return 
        try: 
            res = requests.get(f"{BASE_URL}/addbot?token={parts[1]}").text 
            bot.reply_to(message, f"📡 **Kết quả:** {res}")
        except: bot.reply_to(message, "❌ Lỗi kết nối API.") 
 
    # 3. LỆNH /DELBOT 
    elif cmd == "/delbot": 
        if len(parts) != 2: 
            bot.reply_to(message, "⚠️ Cú pháp: `/delbot [bot_id]`") 
            return 
        try: 
            res = requests.get(f"{BASE_URL}/delbot?botid={parts[1]}").text 
            bot.reply_to(message, f"🗑 **Xóa Bot:** {res}")
        except: bot.reply_to(message, "❌ Lỗi kết nối API.") 
 
    # 4. LỆNH /ADD & /DEL (Bot chính)
    elif cmd == "/add":
        try:
            res = requests.get(f"{BASE_URL}/addid?id={parts[1]}&uid={parts[2]}&time={parts[3]}d").text
            bot.reply_to(message, f"✅ **Thêm ID:** {res}")
        except: bot.reply_to(message, "❌ Lỗi kết nối API.")
    elif cmd == "/del":
        try:
            res = requests.get(f"{BASE_URL}/delid?botid={parts[1]}&uid={parts[2]}").text
            bot.reply_to(message, f"🗑 **Xóa ID:** {res}")
        except: bot.reply_to(message, "❌ Lỗi kết nối API.")
 
    # 6. LỆNH QUẢN LÝ BOT CON: /TAOBOT
    elif cmd == "/taobot":
        if len(parts) != 3:
            bot.reply_to(message, "⚠️ Cú pháp: `/taobot [token] [id_admin_con]`") 
            return
        token_con, admin_con = parts[1], parts[2]
        file_name = f"bot_{admin_con}.py"

        # --- NỘI DUNG BOT CON (ĐÃ THÊM /GEN) ---
        bot_template = f"""
import telebot
import requests
import random
import string
import json
import os
from datetime import datetime, timedelta

bot = telebot.TeleBot('{token_con}')
ADMIN_ID_CON = {admin_con}
BASE_URL = "{BASE_URL}"
GIFT_FILE = "{GIFT_FILE}"

def load_data(file_name):
    if not os.path.exists(file_name): return []
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except: return []

def save_data(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

HELP_TEXT = \"\"\"
🤖 **HƯỚNG DẪN ADMIN BOT CON**

👤 **Quyền hạn:** Admin Bot Con
--------------------------------
🎫 `/gen [ngày] [lượt]` : Tạo Giftcode
➕ `/add [bot_id] [uid] [ngày]` : Thêm người dùng
➖ `/delid [bot_id] [uid]` : Xóa người dùng
🤖 `/addbot [token]` : Thêm bot con vào hệ thống
🗑 `/delbot [bot_id]` : Xóa bot con khỏi hệ thống
❓ `/help` hoặc `/start` : Xem hướng dẫn
\"\"\"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(m):
    if str(m.from_user.id) == str(ADMIN_ID_CON):
        bot.reply_to(m, HELP_TEXT, parse_mode="Markdown")
    else:
        bot.reply_to(m, "❌ Bạn không có quyền sử dụng bot này.")

@bot.message_handler(func=lambda m: True)
def handle(m):
    if str(m.from_user.id) != str(ADMIN_ID_CON): return
    text = m.text.strip()
    if not text.startswith("/"): return
    p = text.split()
    c = p[0].lower()
    
    try:
        if c == "/gen" and len(p) == 3:
            days, max_uses = int(p[1]), int(p[2])
            expire_str = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            gifts = load_data(GIFT_FILE)
            gifts.append({{"code": code, "time": f"{{days}}d", "expire_date": expire_str, "max_uses": max_uses, "current_uses": 0}})
            save_data(GIFT_FILE, gifts)
            bot.reply_to(m, f"✅ **Code:** `{{code}}`\\n📅 **Hạn:** {{days}} ngày\\n👥 **Lượt:** {{max_uses}}", parse_mode="Markdown")
            
        elif c == "/add" and len(p)==4:
            r = requests.get(f"{{BASE_URL}}/addid?id={{p[1]}}&uid={{p[2]}}&time={{p[3]}}d").text
            bot.reply_to(m, f"✅ Kết quả: {{r}}")
        elif c == "/delid" and len(p)==3:
            r = requests.get(f"{{BASE_URL}}/delid?botid={{p[1]}}&uid={{p[2]}}").text
            bot.reply_to(m, f"🗑 Kết quả: {{r}}")
        elif c == "/addbot" and len(p)==2:
            r = requests.get(f"{{BASE_URL}}/addbot?token={{p[1]}}").text
            bot.reply_to(m, f"📡 Kết quả: {{r}}")
        elif c == "/delbot" and len(p)==2:
            r = requests.get(f"{{BASE_URL}}/delbot?botid={{p[1]}}").text
            bot.reply_to(m, f"🗑 Kết quả: {{r}}")
    except Exception as e: bot.reply_to(m, f"❌ Lỗi: {{e}}")
bot.infinity_polling()
"""
        try:
            with open(file_name, "w", encoding="utf-8") as f: f.write(bot_template)
            p = subprocess.Popen([sys.executable, file_name])
            active_bots = load_data(BOT_CHILD_FILE)
            active_bots.append({"admin_id": admin_con, "pid": p.pid, "file": file_name, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_data(BOT_CHILD_FILE, active_bots)
            bot.reply_to(message, f"🚀 **Bot con đã chạy!**\n👤 Admin: `{admin_con}`\n💡 Gõ `/help` tại bot con để xem lệnh.", parse_mode="Markdown")
        except Exception as e: bot.reply_to(message, f"❌ Lỗi: {e}")

    # 7. LỆNH /LISTBOTCON
    elif cmd == "/listbotcon":
        active_bots = load_data(BOT_CHILD_FILE)
        if not active_bots:
            bot.reply_to(message, "📭 Không có bot con nào.")
            return
        txt = "🤖 **DANH SÁCH BOT CON:**\n"
        for b in active_bots: txt += f"• Admin: `{b['admin_id']}` | PID: `{b['pid']}`\n"
        bot.reply_to(message, txt, parse_mode="Markdown")

    # 8. LỆNH /DELBOTCON
    elif cmd == "/delbotcon":
        target = parts[1] if len(parts) > 1 else ""
        active_bots = load_data(BOT_CHILD_FILE)
        new_list = []
        found = False
        for b in active_bots:
            if str(b['admin_id']) == str(target):
                try:
                    psutil.Process(b['pid']).terminate()
                    if os.path.exists(b['file']): os.remove(b['file'])
                    found = True
                except: pass
            else: new_list.append(b)
        save_data(BOT_CHILD_FILE, new_list)
        bot.reply_to(message, f"✅ Đã dừng bot của {target}" if found else "❌ Không tìm thấy.")

    # 9. LỆNH /CHECK 
    elif cmd == "/check": 
        try: 
            res = requests.get(f"{BASE_URL}/check").text 
            bot.reply_to(message, f"🔍 **Server Status:**\n`{res}`", parse_mode="Markdown")
        except: bot.reply_to(message, "❌ Server Offline.") 
 
if __name__ == "__main__": 
    print("Bot chính đang chạy...") 
    bot.infinity_polling()