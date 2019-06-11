from django.shortcuts import render,HttpResponse
import datetime
from myapp import models
import json
from elasticsearch import Elasticsearch
import smtplib
import random
import hashlib
import json
from email.mime.text import MIMEText

# 返回数据格式
def getandReturn(status,info,data):
    d = {}
    d['status'] = status
    d['info'] = info
    d['data'] = data
    return json.dumps(d)

# 验证码发送子程序
def emailSender(targetEmail,num):
    # 第三方 SMTP 服务
    mail_host = 'smtp.qq.com'
    mail_user = '2030396508@qq.com'
    mail_pass = 'bzadzamjpodshecf'

    sender = '2030396508@qq.com'
    receivers = targetEmail

    title = '欢迎使用普罗米修斯搜索引擎！'
    content = '您的验证码：' + num + '，有效期1分钟。'

    message = MIMEText(content,'plain','utf-8')
    message['Form'] = '{}'.format(sender)
    message['To'] = ','.join(receivers)
    message['Subject'] = title
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host,465) #启用SSL发信
        smtpObj.login(mail_user,mail_pass) #登录验证
        smtpObj.sendmail(sender,receivers,message.as_string()) #发送
        print('邮件发送成功！')
    except smtplib.SMTPException as e:
        print(e)

# 登录
def login(request):
    '''

    :param request: email,password
    :return:
    '''
    if request.method == "POST":
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        if email == "" or password == "":
            print('邮箱和密码不能为空!')
            return HttpResponse(getandReturn(0,"邮箱和密码不能为空!",None))
        try:
            user = models.User.objects.get(email = email)
            if user.password == password:
                #设置session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username

                print('登陆成功！')
                return HttpResponse(getandReturn(1,"登录成功!",None))
            else:
                print('密码不正确！')
                return HttpResponse(getandReturn(0,"密码不正确!",None))
        except:
            print('用户不存在！')
            return HttpResponse(getandReturn(0,"用户不存在!",None))

# 注册
def register(request):
    '''

    :param request: username,sex,email,num,password
    :return:
    '''
# 注销
def logout(request):
    '''

    :param request:
    :return:
    '''
# 添加收藏
def addcollect(request):
    '''

    :param request: url,title
    :return:
    '''
# 删除收藏
def delcollect(request):
    '''

    :param request: url,title
    :return:
    '''
# 获取所有收藏
def getAllcollect(request):
    '''

    :param request:
    :return:
    '''
# 添加足迹
def addFootprint(request):
    '''

    :param request: search_content,url,title
    :return:
    '''
# 删除足迹
def delFootprint(request):
    '''

    :param request: url,title
    :return:
    '''
# 获取所有足迹
def getAllFootprint(request):
    '''

    :param request:
    :return:nothing
    '''
# 搜索
def search(request):
    '''
    :param request: question(get)
    :return:
    '''
    es = Elasticsearch()
    question = request.GET.get("question")
    qq = {
        "query": {
            "match_phrase_prefix": {
                "title": {
                    "query": question,
                    "slop": 4

                }
            }
        }
    }
    res1 = es.search(index="mmp", body=qq)
    list = []
    cc = 0
    if len(question) <= 4:
        tt = "百科 " + question
        uu = '''https://baike.baidu.com/item/''' + str(question)
        mm = question
        ll = {}
        ll['title'] = tt
        ll['url'] = uu
        ll['main'] = mm
        list.append(ll)
        cc = 1

    for itt in res1['hits']['hits']:
        tt = itt['_source']['title']
        uu = itt['_source']['url']
        mm = itt['_source']['main']
        ll = {}
        ll['title'] = tt
        ll['url'] = uu
        ll['main'] = mm
        list.append(ll)
        cc = cc + 1
    return HttpResponse(getandReturn(1, cc, list))