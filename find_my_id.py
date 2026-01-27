from src.modules.telegram_bot import TelegramBot
import json

def main():
    bot = TelegramBot()
    print("🔍 텔레그램 봇 업데이트 확인 중...")
    updates = bot.get_updates()
    
    print("\n" + "="*40)
    print("📩 최근 메시지 목록")
    print("="*40)
    
    if isinstance(updates, dict) and updates.get('ok'):
        results = updates.get('result', [])
        if not results:
            print("📭 메시지가 없습니다. 봇에게 'Hello'라고 말을 걸어주세요!")
        else:
            for update in results:
                msg = update.get('message', {})
                chat = msg.get('chat', {})
                sender = msg.get('from', {})
                text = msg.get('text', '(No Text)')
                
                print(f"👤 보낸이: {sender.get('first_name')} (ID: {sender.get('id')})")
                print(f"💬 채팅방 ID (Chat ID): {chat.get('id')}  <-- 이걸 쓰세요!")
                print(f"📝 내용: {text}")
                print("-" * 20)
    else:
        print(f"❌ 에러: {updates}")

if __name__ == "__main__":
    main()
