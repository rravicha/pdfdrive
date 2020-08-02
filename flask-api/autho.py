from flask import Flask,jsonify,request,make_response
import jwt
import datetime
from functools import wraps
app=Flask(__name__)
app.config['SECRET_KEY'] = 'SECRETYKEY'

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=request.args.get('token')#query string
        if not token:
            return jsonify({'message':'token missing'}),403
        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonfiy({'message':'token invalid'}),403
        return f(*args,**kwargs)
    return decorated


@app.route("/public")
def unprotected():
    return jsonify({'message':'public unprotected view'})
@app.route("/private")
@token_required
def protected():
    return jsonify({'message':'private protected view'})

@app.route("/login")
def login():
    auth=request.authorization
    if auth and auth.password=='password':
        token =jwt.encode(
            {
            'user':auth.username,
            'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=5),
            },app.config['SECRET_KEY']
            )
        return jsonify({'token':token.decode('UTF-8')})
    
    return make_response('could not verify',401,{'WWW-Authenticate':'Basic Realm="Login Required'})



if __name__ == '__main__':
    app.run(debug=True)
    
    
# 500
# 600
# 400
# 400
# 321
# 333
# 3
# unit test
# doc creation
# cicd pipeline
# deploy and run it
# enable logs

# @app.route("/", methods=['POST'])
# @app.route("/home", methods=['POST'])