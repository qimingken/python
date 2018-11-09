#!/usr/bin/env python3
from flask import Flask,jsonify,abort,make_response,request,url_for,render_template
import pymssql
app = Flask(__name__)

class MSSQL:
    def __init__(self,host,user,pwd,db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise(NameError,"没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host,user=self.user,password=self.pwd,database=self.db,charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"连接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()
        description = cur.description

        descriptionlist = []  
        datalisttmp = []
        datalist = []
        for i in description:
             descriptionlist.append(i[0])
        for i in resList:
            datalisttmp = []
            for j in i:
                datalisttmp.append(j)
            datalist.append(datalisttmp)

        #查询完毕后必须关闭连接
        self.conn.close()
        result = [descriptionlist,datalist]
        return result

    def ExecNonQuery(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()




def Getdata(bookinglistno):    
    ms = MSSQL(host="192.168.200.2",user="sa",pwd="",db="bookinfo")
    if bookinglistno == None or bookinglistno == '':
        reslist = None
        return []
    else:
        sqlconfirm = "SELECT BookingBarNo,BookingType,BookingName,BookingTime from BookingInfo where BookingBarNo = '"+ bookinglistno +"'" 
        reslist = ms.ExecQuery(sqlconfirm)
        if reslist[1] != []:              
            j = 0
            while j < len(reslist[0]):
                if reslist[0][j] == "BookingBarNo":
                    reslist[0][j] = "产品条码"
                elif  reslist[0][j] == "BookingType":
                    reslist[0][j] = "产品型号"
                elif  reslist[0][j] == "BookingName":
                    reslist[0][j] = "产品名称"
                elif  reslist[0][j] == "BookingTime":
                    reslist[0][j] = "出库日期"
                j = j+1
            return reslist
        else:
            return []
    


@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def getresult():
    print('testPost')
    print(request.form['bookinglistnoinput'])
    getlistno = request.form['bookinglistnoinput']
    aaa = Getdata(getlistno)

    return render_template('index.html',bookinglistnoinput = getlistno,  result = aaa)
    """return jsonify(aaa)


newsql="update webuser set name='%s' where id=1"%u'测试'
print newsql
ms.ExecNonQuery(newsql.encode('utf-8')) """










tasks = [
    { 
        'id': 1,
        'title': 'Buy groceries',
        'description': 'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': 'Learn Python',
        'description': 'Need to find a good Python tutorial on the web',
        'done': False 
    }
]

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/todo/api/v1.0/tasks', methods=['GET'])

def get_tasks():
    return jsonify({'tasks': list(map(make_public_task, tasks))})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(400)
    return jsonify({'tasks': task[0]})

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 400)

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400) 
    if 'title' in request.json and not(isinstance(request.json['title'],str)):
        abort(400)
    if 'description' in request.json and not(isinstance(request.json['description'],str)):
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)