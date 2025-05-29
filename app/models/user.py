from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))  # Trường số điện thoại
    address = db.Column(db.String(200))  # Trường địa chỉ
    avatar = db.Column(db.String(200), default='default_avatar.png')  # Trường avatar với giá trị mặc định

    def __repr__(self):
        return f'<User {self.username}>'