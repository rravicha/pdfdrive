'''
module name     :   routes.py
functionality   :   provides all the routes needed for the app
'''
from flask import jsonify, request, send_file
from engine import app
from engine.forms import Compute

@app.route("/", methods=['POST'])
def home():
    try:
        c=request.headers.get('clientid')
        s=request.headers.get('secret')
        print(f"clientid : {c} | secret {s}")
        print(f"clientid type : {type(c)} | secret {type(s)}")
        print(request.headers.keys)
        if ((c=='sparkey') and (s=='qpalzmwiskxn')):
            if request.is_json:
                comp = Compute(request.get_json())
                res, msg = comp.validate()
                if res:
                    response = comp.calculate()
                    return jsonify(response)
                else:
                    print((msg))
                    return jsonify(msg)
            else:
                return 'Incorrect json format', 400
        else:
            return 'Incorrect credentials',400
    except Exception as err:
        return(str(err))

@app.route("/logs", methods=['GET'])
def logs():
    logpath='/home/susi/gitlab/gitlive/flask-api/monitor.txt'
    return send_file(logpath, as_attachment=False)
    

@app.route("/logsdown", methods=['GET'])
def logdown():
    logpath='/home/susi/gitlab/gitlive/flask-api/monitor.txt'
    return send_file(logpath, as_attachment=True)
