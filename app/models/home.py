from app import db
from datetime import datetime

class IntroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False, default='default_intro.jpg')
    cta_text = db.Column(db.String(50), default='Tìm Hiểu Thêm')
    cta_url = db.Column(db.String(255), default='/introduce')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    cta_text = db.Column(db.String(50), default='Khám Phá')
    cta_url = db.Column(db.String(255), default='/pricing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    cta_text = db.Column(db.String(50), default='Đọc Thêm')
    cta_url = db.Column(db.String(255), default='/blog')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)