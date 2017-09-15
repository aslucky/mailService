# coding:utf-8
import logging
import os
from email.header import make_header

import requests
from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger
from flask import Flask, jsonify
from flask import render_template
from flask import request
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object('config126')

handler = logging.handlers.RotatingFileHandler('emails.log', encoding='UTF-8', maxBytes=1024 * 1024 * 5,
                                               backupCount=10)
handler.setLevel(logging.DEBUG)
# logging的级别主要有NOTSET、DEBUG、INFO、WARNING、ERROR和CRITICAL
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

celeryLogger = get_task_logger(__name__)

mail = Mail(app)
curPath = os.path.split(os.path.realpath(__file__))[0]
app.logger.info('email server start.')


celery = Celery(app.import_name)
celery.config_from_object('celeryconfig')
celery.conf.update(app.config)


def http_post(msgJson):
    r = requests.post(app.config['MAIL_BACKEND_NOTIFY_URL'],
                      json=msgJson, verify=False)

    if r.status_code == 200:
        resp = r.json()
        print(resp)
    else:
        app.logger.error('notify backend failed:%d' % r.status_code)
        resp = None
    return resp


def notifyBackend(msgJson):
    app.logger.info('enter notifyBackend.')
    return
    try:
        resp = http_post(msgJson)
    except Exception as e:
        import traceback
        traceback.print_exc()
        app.logger.exception('notify backend service exception.')
        return
    if resp and resp['code'] == "SUCCESS":
        app.logger.info('notify backend success.')
        return
    else:
        app.logger.error('notify backend failed.')


@celery.task(bind=True, name='send_async_email', trail=True, default_retry_delay=5, max_retries=3)
def send_async_email(self, msgJson):
    app.logger.info('enter send_async_email')
    if not msgJson['title']:
        subject = app.config['TITLE_TEMP']['invoice']
    else:
        subject = app.config['TITLE_TEMP'][msgJson['title']['subject']]
        if not subject:
            subject = app.config['TITLE_TEMP']['invoice']
    sender = app.config['MAIL_DEFAULT_SENDER']
    recipients = msgJson['emailTo']
    tempDict = {}
    if msgJson['templateId'] == 'invoiceError':

        if not msgJson['content']:
            # post error info and return
            param = {'appId': msgJson['appId'], 'thirdId': msgJson['thirdId'], "sendStatus": 1}
            app.logger.exception('mandatory param not exist, email not send.')
            notifyBackend(param)
            return
        else:
            tempDict = msgJson['content']

    attachments = msgJson['attachment']
    ccTo = msgJson['cc']
    bccTo = msgJson['bcc']
    with app.app_context():
        try:
            html_body = render_template(msgJson['templateId'] + ".html", tempDict=tempDict)
            text_body = render_template(msgJson['templateId'] + ".txt", tempDict=tempDict)
            msg = Message(subject, sender=sender, recipients=recipients, cc=ccTo, bcc=bccTo,
                          charset='utf-8')
            msg.body = text_body
            msg.html = html_body
            if attachments:
                for f in attachments:
                    with app.open_resource(f['filePath']) as fp:
                        # 解决QQ附件乱码问题，使用base64编码传输
                        name = make_header([(f['dealFileName'], 'utf8')]).encode('utf8')
                        msg.attach(filename=name, data=fp.read(),
                                   content_type='application/octet-stream', disposition='attachment')
            # add html content png
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            imgPath = os.path.join(SITE_ROOT, "templates", "invoice.png")

            with open(imgPath, 'rb') as fp:
                msg.attach(filename=imgPath, data=fp.read(),
                           content_type='application/octet-stream', disposition='inline',
                           headers=[('Content-ID', 'invoice')])
            try:
                app.logger.info('before send mail')
                mail.send(msg)
            except MaxRetriesExceededError as e2:
                app.logger.info('logger: MaxRetriesExceededError raised')
                celeryLogger.error('MaxRetriesExceededError raised')
                return {"code": "ERROR", "message": "MaxRetriesExceededError failed."}
            except Exception as e1:
                app.logger.info('logger: exception raised')
                import traceback
                traceback.print_exc()
                raise self.retry(exc=e1)
                return {"code": "ERROR", "message": "failed."}
            param = {'appId': msgJson['appId'], 'thirdId': msgJson['thirdId'], "sendStatus": 0}
            print('email send success')
            app.logger.info('email send success.')
        except Exception as e:
            import traceback
            traceback.print_exc()
            print('email send exception.')
            param = {'appId': msgJson['appId'], 'thirdId': msgJson['thirdId'], "sendStatus": 1}
            app.logger.exception('email send exception.')
            app.logger.info('logger: exception send tail')

        notifyBackend(param)


def que_async_email(email):
    ret = send_async_email.delay(email)
    if ret.failed():
        app.logger.exception('send_async_email failed.')
        param = {'appId': email['appId'], 'thirdId': email['thirdId'], "sendStatus": 1}
        notifyBackend(param)


"""
POST 创建新任务-发送邮件
http://[hostname]/api/v1.0/emails

GET 查询邮件状态
http://[hostname]/api/v1.0/emails/[thirdId]
"""


@app.route('/api/v1.0/emails', methods=['POST'])
def sendEmail():
    email = request.json
    app.logger.info(email)
    try:
        que_async_email(email)
    except Exception as e:
        import traceback
        traceback.print_exc()
        app.logger.exception('start que_async_email failed.')
        return jsonify({"code": "506", "message": "请求接收，进入异步处理队列失败"})
    return jsonify({"code": "202", "message": "请求接收，进入异步处理队列成功"})


if __name__ == '__main__':
    print("main entry debug")
    app.run(debug=True, port=8020, host='0.0.0.0')
