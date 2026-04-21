from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "cbs.login"
login_manager.login_message_category = "info"
# check of niemand aan de sessie zit: beveiliging op strong
login_manager.session_protection = 'strong'

.