CELERY_BROKER_URL='amqp://guest@localhost//'
CELERY_RESULT_BACKEND='amqp://guest@localhost//'
CELERY_TASK_SERIALIZER='json'
# Ignore other content
CELERY_ACCEPT_CONTENT=['json']
# 长时间运行Celery有可能发生内存泄露，可以像下面这样设置
CELERYD_MAX_TASKS_PER_CHILD = 80 # 每个worker执行了多少任务就会死掉
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Asia/Shanghai'