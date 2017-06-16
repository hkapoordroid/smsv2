"""
The flask application package.
"""

from flask import Flask
from flask_login import LoginManager
from model.user import User
import awshelper
import os

#app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.curdir), 'instance'), instance_relative_config=True)
app.config.from_pyfile('flask.cfg')
#app.config['SECRET_KEY'] = "FLASK_SECRET_KEY"

#sess = Session()
#sess.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"
login_manager.login_message = "Please Login"


@login_manager.user_loader
def load_user(email):
    #TODO: here based on id, AWS RDS lookup needs to be done to get the data back to LoginManager
    
    if not awshelper.check_if_login_exists(email):
        return

    user = User()
    user.id = email
    return user


#@login_manager.request_loader
#def request_loader(request):
#    email = request.form.get('loemail')
#    if email not in users:
#        return
    
#    user = User()
#    user.id = email

#    # DO NOT ever store passwords in plaintext and always compare password
#    # hashes using constant-time comparison!
#    user.is_authenticated = request.form['pw'] == users[email]['pw']

#    return user
    

import sms.views
import sms.igauth
