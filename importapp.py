# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import tkFileDialog
import os
import os.path
import dealcsv
import ttk
import threading
import datetime
import time
import magento
import ConfigParser

ALLOWFILETYPES =[("CSV File","*.csv")]#,("Excel File","*.xls")]

CONFIGFILENAME = 'magento.cfg'

def saveconfigfile(url,username,password):
    result,message = magento.testconfig(url,username,password)
    if not result:
        tkMessageBox.showinfo(title="参数有误，请修正",message=message)
        return

    config = ConfigParser.RawConfigParser()
    config.add_section('Server')
    config.set('Server','url',url)
    config.set('Server','username',username)
    config.set('Server','password',password)

    with open(CONFIGFILENAME,'wb') as configfile:
        config.write(configfile)


def getconfigvalue(section,key):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIGFILENAME)
    return config.get(section,key)

class ConfigDialog(Toplevel):
    def __init__(self,parent,title=None):
        Toplevel.__init__(self,parent)
        self.top = parent

        self.lb_server = Label(self,text="URL")
        self.lb_username = Label(self,text="用户名")
        self.lb_password = Label(self,text="密码")

        self.txt_server = Entry(self,width=50)
        self.txt_username = Entry(self,width=50)
        self.txt_password = Entry(self,width=50)

        self.bt_Enter = Button(self,text="保存",command=self.enter)
        self.bt_Cancel = Button(self,text="取消",command=self.cancel)

        self.lb_server.grid(row=0,column=0,sticky=W)
        self.lb_username.grid(row=1,column=0,sticky=W)
        self.lb_password.grid(row=2,column=0,sticky=W)

        self.txt_server.grid(row=0,column=1,columnspan=4,sticky=E)
        self.txt_username.grid(row=1,column=1,columnspan=4, sticky=E)
        self.txt_password.grid(row=2,column=1,columnspan=4,sticky=E)

        self.bt_Enter.grid(row=3,column=4,sticky=W)
        self.bt_Cancel.grid(row=3,column=4,sticky=E)
        
        self._loadconfig()
        
    def _loadconfig(self):
        if os.path.exists(CONFIGFILENAME):
            self.txt_server.insert(0,getconfigvalue('Server','url'))
            self.txt_username.insert(0,getconfigvalue('Server','username'))
            self.txt_password.insert(0,getconfigvalue('Server','password'))

    def enter( self ):
        url = self.txt_server.get()
        username = self.txt_username.get()
        password = self.txt_password.get()
        saveconfigfile(url,username,password)
        self.destroy()

    def cancel( self ):
        self.destroy()


class Application(Frame):
    def __init__(self,master):
        Frame.__init__(self,master,bd=1)
        self['width']=800
        
        self.lb_chooseFirstFile = Label(self,text="产品文件")
        self.lb_chooseFirstFile.grid(row=0,column=0,sticky=W)
        
        self.txt_firstfilename = Entry(self,width=30)
        self.txt_firstfilename.grid(row=0,column=1,sticky=W)
        
        self.bt_openfirstfile = Button(self,text="选择文件..")
        self.bt_openfirstfile.bind("<ButtonRelease-1>",self.selectFile)
        self.bt_openfirstfile.grid(row=0, column=2,sticky=E)

        self.progressbar = ttk.Progressbar(self,length=300,mode="determinate")
        self.progressbar.grid(row=1,columnspan=3,sticky=W+S+N+E) 

        self.bt_comparedata = Button(self,text="开始导入",fg="blue")
        self.bt_comparedata.grid(row=2,column=0,columnspan=3,sticky=E)
        self.bt_comparedata.bind("<ButtonRelease-1>",self.startimport)
        
        self.msg_result = Message(self,text="",fg="red",width=500)
        self.msg_result.grid(row=3,columnspan=3)
        self.msg_result.bind("<ButtonRelease-1>",self.open_result)
        self.pack(side=LEFT)

            

    def open_result(self,event):
        message = self.msg_result["text"]
        if message and u"生成成功" in message:
            os.system("start excel.exe result.csv")
            return        
    
    def selectFile(self,event):
        filename = tkFileDialog.askopenfilename(title="请选择需要上传的CSV文件",filetypes=ALLOWFILETYPES)
        if not filename:
            return
        if event and event.widget == self.bt_openfirstfile:
            self.selectfirstfile(filename)

    def selectfirstfile(self,filename):
        self.txt_firstfilename.delete(0,END)
        self.txt_firstfilename.insert(0,filename)
            
    def startimport(self,event):
        #init thread argument
        self.progressbar['value']=0
        magento.hasproc_count = 0
        magento.totalcount=0

        firstfile = self.txt_firstfilename.get()
        url = getconfigvalue('Server','url') #'http://localhost/magento/index.php/api/xmlrpc'
        username = getconfigvalue('Server','username') #'tedi'
        password = getconfigvalue('Server','password') #'loveyuanyuan'
        print url,username,password
        importthread = threading.Thread(target=self.startimportproductthread,args=(url,username,password,firstfile))
        importthread.start()

        time.sleep(1)
        thread = threading.Thread(target=self.startprogressbarthread)
        thread.start()

    
    def startimportproductthread(self,url,username,password,firstfile):
        result = magento.importproducts(url,username,password,firstfile)
        self.msg_result["text"] = "所有产品已经成功导入magento!"


    def startprogressbarthread(self):
        print "thread.totalcount=%s,thread.hasproc_count=%s"%(magento.totalcount,magento.hasproc_count)
        complete_percent =1
        while complete_percent<100:
            complete_percent = int(float(magento.hasproc_count)/magento.totalcount*100)
            #print "complete_percent=%s"%complete_percent
            self.msg_result["text"] = "当前任务的处理进度%s%%" % complete_percent
            #self.progressbar.step(complete_percent)
            self.progressbar["value"] = complete_percent
            if complete_percent<100:
                import time
                time.sleep(1)
            else:
                self.msg_result["text"] = "所有产品已经成功导入magento,请登陆网站查看"


def show_about_dialog():
    tkMessageBox.showinfo(title="About",message="Magento import products tool version 0.1")


def show_config_dialog():
    d = ConfigDialog(master)

def setmenu(master):
    menubar = Menu(master)
    master.config(menu=menubar)

    #add menuitem
    filemenu = Menu(menubar)
    menubar.add_cascade(label="文件", menu=filemenu)
    filemenu.add_command(label="配置服务器",command=show_config_dialog)
    filemenu.add_command(label="关于",command=show_about_dialog)

if __name__ == "__main__":
    global master
    global app
    master = Tk()
    ws = master.winfo_screenwidth()
    hs = master.winfo_screenheight()
    print "system.width=%s ,system.height=%s" %(ws,hs)
    # calculate position x, y
    width=400
    height=125
    x = (ws/2)-(width/2)   
    y = (hs/2)-(height/2)
    setmenu(master)    
    master.title("Magento import products tool version 0.1")
    app = Application(master)
    master.geometry('%dx%d%+d%+d'%(width,height,x,y))
    master.maxsize(width,height)
    master.minsize(width,height)
    app.mainloop()
    
