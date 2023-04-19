import telegram
import threading
from bot import setup
from urllib import parse
from waitress import serve
from runasync import run_async
from flask import Flask, request, jsonify
from config import BOT_TOKEN, WEB_HOOK, PORT
from flask import request
import datetime

app = Flask(__name__)
application = setup(BOT_TOKEN)

@app.route('/', methods=['GET'])
def hello():
    return 'Bot has connected!'
@app.before_request
def log_request_info():
    now = datetime.datetime.now()
    bj_time = now + datetime.timedelta(hours=8)
    date_str = bj_time.strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request.access_route[0]
    user_agent = request.headers.get('User-Agent')
    print(f'访问ip: {ip_address}, 中国时间:{date_str}\n设备： {user_agent}')

@app.route(rf'/{BOT_TOKEN}'.format(), methods=['POST'])
async def respond():
    update = telegram.Update.de_json(request.get_json(force=True), application.bot)
    run_async(application.initialize())
    thread = threading.Thread(target=run_async, args=(application.process_update(update),))
    thread.start()
    return jsonify({'status': 'success', 'message': 'Received message successfully.'})

@app.route('/setwebhook', methods=['GET', 'POST'])
async def configure_webhook():
    webhookUrl = parse.urljoin(WEB_HOOK,rf"/{BOT_TOKEN}")
    result = await application.bot.setWebhook(webhookUrl)
    if result:
        print(rf"webhook configured: {webhookUrl}")
        return rf"webhook configured: {webhookUrl}"
    else:
        print("webhook setup failed")
        return "webhook setup failed"

if __name__ == '__main__':
    run_async(configure_webhook())
    serve(app, host="0.0.0.0", port=PORT)
