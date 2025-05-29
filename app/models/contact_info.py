from app import db

class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))

    def __repr__(self):
        return f'<ContactInfo {self.email}>'