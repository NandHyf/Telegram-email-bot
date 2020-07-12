# coding=utf-8
# @author NandHyf
import os, toml, json, re, base64
import threading, datetime, requests
import getpass, poplib
from telegram import bot

# 全局注释(lol):
# "en_xxx" = encode_xxx, "已编码的(解码前的)变量"
# "de_xxx" = decode_xxx, "解码后的变量"


# 读取配置文件
class Configs():
    # 读取配置文件
    def __init__(self, configFileName):
        self.configFileName = str(configFileName)
        self.cRead = {}
        self.dicts = {}
        self.labelNames = []

        # 检查配置文件是否存在
        try:
            with open(self.configFileName,'r', encoding='utf-8')as c:
                self.cRead = toml.loads(c.read())
        
            self.labelNames = list(self.cRead.keys())
            for self.labelName in self.labelNames:
                configs = []
                configs = self.cRead[self.labelName]
                self.dicts[self.labelName] = configs

        # 不存在就询问是否自动生成
        except FileNotFoundError:
            while(1):
                genConfirm = input("Would you like do generate a new \"MailBot.toml\" ?[y/n]")
                if genConfirm == 'y' or genConfirm == 'n':
                    break

            if genConfirm == 'y':
                gen = {'commands': {'pull': 'Pull()', 'set': 'Set()'}, 'bot': {'token': '', 'chatId': ''}, 'timers': {'globalTimer': 5}, 'box1': {'ssl': True, 'host': 'pop.domainName.com', 'userName': 'exapmle@domainName.com', 'passWd': 'passwd', 'notedNum': 0}, 'box2': {'ssl': False, 'host': 'pop.domainName.com', 'userName': 'exapmle@domainName.com', 'passWd': 'passwd', 'notedNum': 0}}

                with open('MailBot.toml','w', encoding='utf-8') as config:
                    config.write(toml.dumps(gen))
                print("Sucessfully generated \"MailBot.toml\".")

            elif genConfirm == 'n':
                exit()


    # 检查配置内容是否存在
    def IsExisted(self, keyName):
        pass


    # 加载特定配置
    def LoadConfig(self, labelName, keyName):
        keyConfigs = []
        keyConfigs = self.dicts[labelName][keyName]
        return keyConfigs


    # 查询邮箱
    def GetBoxes(self):
        getBoxes = list(self.labelNames)[3:]
        return getBoxes


    # 生成配置文件模板
    def GenConfig():
        with open('MailBot.toml','w', encoding='utf-8') as config:
            gen = {'commands': {'pull': 'Pull()', 'set': 'Set()'}, 'bot': {'token': '', 'chatId': ''}, 'timers': {'globalTimer': 5}, 'box1': {'ssl': True, 'host': 'pop.domainName.com', 'userName': 'exapmle@domainName.com', 'passWd': 'passwd', 'notedNum': 0}, 'box2': {'ssl': False, 'host': 'pop.domainName.com', 'userName': 'exapmle@domainName.com', 'passWd': 'passwd', 'notedNum': 0}}
        config.write(toml.dumps(gen))


    # 更新(覆写)配置文件
    def Update(self, labelName, upNum):
        self.dicts[labelName]['notedNum'] = upNum
        with open(self.configFileName, 'w', encoding='utf-8') as reW:
            reW.write(toml.dumps(self.dicts))


# 命令
class Commands():
    def __init__(self):
        pass


    def Pull(self, targetObj):
        pass


    def Set(self, targetObj):
        pass


# 拉取邮件
class PullMove():
    def __init__(self, ssl, ho, us, pa, no, latestNum):# 原谅起名起到大脑爆炸orz;
        self.ssl = bool(ssl)
        self.host = ho
        self.user = us
        self.passwd = pa
        self.notedNum = int(no)
        self.latestNum = latestNum

    # 获取邮件内容
    def PullMessages(self, latestNum):
        latestNum = latestNum
        self.notedNum = self.notedNum + 1
        # 创建一个列表用于存储retr回来的邮件内容
        retrStore = {}

        # 备用连接方式
        if self.ssl == True:
            mailServer = poplib.POP3_SSL(self.host)
            mailServer.user(self.user)
            mailServer.pass_(self.passwd)
            mailServer.noop()

        elif self.ssl == False:
            mailServer = poplib.POP3(self.host)
            mailServer.user(self.user)
            mailServer.pass_(self.passwd)
            mailServer.noop()
        
        while self.notedNum <= latestNum:
            TempKey = 'retr'''+str(self.notedNum)+''
            retrStore[TempKey] = str(mailServer.retr(self.notedNum))
            self.notedNum = self.notedNum + 1
        
        mailServer.quit()
        # retrStore -> en_dicts
        return retrStore

        # 用一个json存储起来, 不过似乎不是必需的;
        # with open('retrStore.json','w', encoding='utf-8') as tempStore:
        #     tempStore.write(json.dumps(retrStore))


    # 获取服务器邮件数
    def PullNumbers(self):
        if self.ssl == True:
            mailServer = poplib.POP3_SSL(self.host)
            mailServer.user(self.user)
            mailServer.pass_(self.passwd)
            mailServer.noop()

        elif self.ssl == False:
            mailServer = poplib.POP3(self.host)
            mailServer.user(self.user)
            mailServer.pass_(self.passwd)
            mailServer.noop()

        latestNum = len(mailServer.list()[1])
        # 与本地"已经通知过"的邮件的差值
        # differNum = latestNum - self.notedNum
        # 保持连接
        mailServer.quit()
        return latestNum


# 解码过程
class Decodes():
    def __init__(self, en_content, en_Method):
        self.en_content = en_content
        self.en_Method = en_Method


    def ToBase64(self):
        de_origin = base64.b64decode(self.en_content) # "de_origin"是因为很久没有改动过, 所以一直是原来的草稿状态; 不过这个堆屎行为会在下个版本被改掉的
        return de_origin


    def DeMethod(self):
        de_origin = base64.b64decode(self.en_content)
        res = de_origin.decode(encoding=self.en_Method)
        return res


# "解码行为(动作)" 函数; 返回一个列表
def Decoding(en_dicts):
    en_dicts = en_dicts
    de_dict_main = {}
    de_dict_temp = {}
    getKeys = list(en_dicts.keys())

    for getKey in getKeys:
        de_contents = []
        en_contents = en_dicts[getKey]

        for en_content in en_contents:
            en_contents = []
            # "是否需要解码"的标记
            needDecode = bool(re.search(r"=\?", en_content))
            # 判断是不是正文内容
            isBody = bool(re.search(r"charset=", en_content))

            if needDecode == True:
                findEn_Method = str(re.search(r'=\?(.*?)\?=', en_content).group(1))
                # 匹配出编码方式
                en_Method = str(re.search(r'(.*?)\?', findEn_Method).group(1))
                # 匹配出编码的内容
                matched_en_content = str(re.search(r'B\?(.*?)\?=', en_content).group(1))
                # 获得解码内容
                de_content = Decodes(matched_en_content, en_Method)
                # 添加解码内容到列表
                de_contents.append(de_content.DeMethod())
            
            elif isBody == True:
                en_Method = re.search(r"charset=(.*?)',", en_content).group(1)
                bodies = list(re.findall(r"b'(.*?)',", en_content))
                bodies = bodies[2:]
                matched_body = ""

                for i in range(len(bodies)):
                    matched_body = matched_body + bodies[i]
    
                de_content = Decodes(matched_body, en_Method)
                de_contents.append(de_content.DeMethod())

            else:
                de_contents.append(en_content)

            de_dict_temp[getKey] = de_contents

        de_dict_main.update(de_dict_temp)

    return de_dict_main


# 匹配内容：获取邮件基本信息(Date, From, Subject, 正文内容, 是否包含附件, 附件名称); 返回一个列表
def Match_en_contents(en_dicts):
    en_dicts = en_dicts
    matechedDict_main = {}
    matechedDict_temp = {}
    getKeys = list(en_dicts.keys())

    for getKey in getKeys:
        matchedContents = []
        
        # 匹配邮件信息的表达式
        en_date =  str(re.search(r"Date: (.*?)',", en_dicts[getKey]).group(1))
        en_from = str(re.search(r"b'From: (.*?)',", en_dicts[getKey]).group(1))
        
        addressInclude = bool(re.search(r"<(.*?)>", en_from))
        if addressInclude == True:
            mailAddress = str(re.search(r"<(.*?)>", en_from).group(1))
        else:
            mailAddress = en_from

        en_subject = str(re.search(r"Subject: (.*?)',", en_dicts[getKey]).group(1))
        
        try:
            en_bodyText = str(re.search(r"plain;(.*?)b'', b'--", en_dicts[getKey]).group(1))
        except AttributeError:
            en_bodyText = '(None)'

        contentInclude = bool(re.search(r"Content-Type: application/octet-stream;", en_dicts[getKey]))

        # 直观的表示是否包含附件的数据(标记)
        if contentInclude == True:
            contentInclude = 'Yes' # 这里本来是想用布尔类型的,但是后面在解码的时候有BUG直接提前结束了循环所以就换成了Y/N
        else:
            contentInclude = 'None'

        contentNames = re.findall(r"tname=(.*?)',", en_dicts[getKey])

        # 最后写入列表(然后返回)
        matchedContents.append(en_date)
        matchedContents.append(mailAddress)
        matchedContents.append(en_subject)
        matchedContents.append(en_bodyText)
        matchedContents.append(contentInclude)
        matchedContents = matchedContents + contentNames

        matechedDict_temp[getKey] = matchedContents
        matechedDict_main.update(matechedDict_temp)

    return matechedDict_main


# 制作推送文本
def MakeNotes(ct, boxName, notedNum, endNum, de_dict):
    ct = ct
    boxName = boxName
    notedNum = notedNum
    endNum = endNum
    de_dict = de_dict
    getKeys = list(de_dict.keys())
    pull = "Pulled from {}\nNo.%d to No.%d".format(boxName)% (notedNum + 1, endNum)
    hr = "-------------------------"
    tab = "    "
    head = "{}\n{}\n".format(ct, pull)
    notes = "" + head
    
    for getKey in getKeys:
        seq = int(getKey[-2:])
        mailDate = de_dict[getKey][0]
        mailFrom = de_dict[getKey][1]
        mailSubject = de_dict[getKey][2]
        mailBodyText = de_dict[getKey][3]
        mailInclude = de_dict[getKey][4]
        attachmentNum = ""

        basicInfo = hr + "\nNo.%d: "% (seq) + "\nDate: {}\nFrom: {}\nSubject: {}\nBodyText: \n\n{}\n\nAttachment(s): {}".format(mailDate, mailFrom, mailSubject, mailBodyText, mailInclude)
        includeNames = ""

        if mailInclude == 'Yes':
            includeNum = len(de_dict[getKey]) - 5
            attachmentNum = ", (%d)\n"% (includeNum)
    
            i = 0
            n = 5
            while i < includeNum:
                includeNames = includeNames + tab + "{}\n".format(de_dict[getKey][n])
                n = n + 1
                i = i + 1

        elif mailInclude == 'None':
            attachmentNum = "\n"

        notes = notes + basicInfo + attachmentNum + includeNames

    return notes


# 推送功能
def PushNotes(token, chatId, notes):
    url =  "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(token, chatId, notes)
    try:
        requests.get(url)
        
        return 'D'
    except requests.exceptions.ProxyError:

        return 'requests.exceptions.ProxyError'


# 定时器
def Timing():
    configFileName = 'MailBot.toml'

    ct = datetime.datetime.now()
    print(ct)

    # 拉取数据用的本地变量
    gets = Configs(configFileName)

    cycle = gets.LoadConfig('timers', 'globalTimer') * 60

    global clk
    clk = threading.Timer(cycle, Timing)
    clk.start()

    boxNames = gets.GetBoxes()

    for boxName in boxNames:
        ssl = gets.LoadConfig(boxName, 'ssl')
        host = gets.LoadConfig(boxName, 'host')
        userName = gets.LoadConfig(boxName, 'userName')
        passWd = gets.LoadConfig(boxName, 'passWd')
        notedNum = gets.LoadConfig(boxName, 'notedNum')
        
        pull = PullMove(ssl, host, userName, passWd, notedNum, 0)
        endNum = pull.PullNumbers()

        if endNum == notedNum:
            print('{}: All %d emails have been notefied.'.format(boxName) %(endNum))
            print('=========================\n')

        # 把差值小于0直接当作清理过邮箱了, 所以只做重置计数; 之后会采用新的判定方式所以就这样了
        elif endNum < notedNum:
            print('{}: All %d emails have been notefied.'.format(boxName) %(endNum))
            # 调用更新函数覆写配置文件
            gets.Update(boxName, endNum)
            print("Set {}'s notedNum to %d".format(boxName) %(endNum))
            print('=========================\n')

        elif endNum > notedNum:
            messages = pull.PullMessages(endNum)
            print("Pulled from {}, No.%d to No.%d".format(boxName) % (notedNum + 1, endNum))
            # with open('tempStore.json', 'w', encoding='utf-8')as s:
            #     s.write(toml.dumps(messages))

            # en_dicts = {}

            # with open('tempStore.json', 'r', encoding='utf-8')as s:
            #     en_dicts = json.loads(s.read())

            en_contents = Match_en_contents(messages)

            with open('tempStore.json', 'w', encoding='utf-8')as s:
                s.write(json.dumps(en_contents))

            de_contents = {}
            de_contents = Decoding(en_contents)

            # 拼接消息文本
            notes = MakeNotes(ct, userName, notedNum, endNum, de_contents)

            # 推送消息
            token = gets.LoadConfig('bot', 'token')
            chatId = gets.LoadConfig('bot', 'chatId')
            pushNote = PushNotes(token, chatId, notes)

            if pushNote == 'D':
                gets.Update(boxName, endNum)
                print(notes)
                print('-------------------------')
                print("Set {}'s notedNum to %d".format(boxName) %(endNum))
                print('=========================\n')

            elif pushNote == 'requests.exceptions.ProxyError':
                print("{} met requests.exceptions.ProxyError.".format(boxName))
                print('=========================\n')
                # pushNote = PushNotes(token, chatId, notes)
                clk = threading.Timer(10,Timing)
                clk.start()

if __name__ == "__main__":
    clk = threading.Timer(2,Timing)
    clk.start()