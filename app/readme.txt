
http://localhost:8020/api/v1.0/emails

使用默认模板，无参数
{
 "appId" : "INVOICE",
 "attachment" : [ {
  "dealFileName" : "电子发票.pdf",
  "filePath" : "/Users/zhengjun/project/PycharmProjects/mailServer/src/行程报销单.pdf"
 } ],
 "bcc" : null,
 "cc" : null,
 "content" : null,
 "emailTo" : [ "email2918@126.com","tylerwork@qq.com" ],
 "templateId" : "invoice",
 "thirdId" : "17081711474677700039",
 "title" : null
}

使用默认模板，有参数在content域
{
 "appId" : "INVOICE",
 "attachment" : null,
 "bcc" : null,
 "cc" : null,
 "content" :  {
     "applicationId":"123456",
                "applicationTime":"2017-08-01"
             },
 "emailTo" : [ "email2918@126.com" ],
 "templateId" : "invoiceError",
 "thirdId" : "17081711474677700039",
 "title" : null
}


在配置文件里面设置日志等相关信息
gunicorn mailServerStudy:app -p mailServerStudy.pid -c gunicorn_config.py

