from app import db

class Pricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # Lưu danh sách tính năng, cách nhau bằng dòng mới
    featured = db.Column(db.Boolean, default=False)  # Gói nổi bật