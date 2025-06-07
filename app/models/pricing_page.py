from app import db

class PricingPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="Bảng Giá Dịch Vụ")
    description = db.Column(db.Text, nullable=False, default="Khám phá các gói dịch vụ phù hợp với nhu cầu của bạn tại HoagART.")
    show_banner = db.Column(db.Boolean, default=True)  # Bật/tắt banner