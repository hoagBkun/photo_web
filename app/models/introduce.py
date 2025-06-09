from app import db
from datetime import datetime

class IntroduceSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default='/static/images/default.jpg')
    cta_text = db.Column(db.String(50), nullable=False)
    cta_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default='/static/images/default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MissionSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default='/static/images/default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)