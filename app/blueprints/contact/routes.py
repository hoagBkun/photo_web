
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models.contact import ContactMessage
from app import db

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')

@contact_bp.route('/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service = request.form.get('service')
        budget = request.form.get('budget')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Vui lòng điền đầy đủ thông tin bắt buộc.', 'error')
            return redirect(url_for('contact.contact'))

        contact_message = ContactMessage(
            name=name, email=email, phone=phone,
            service=service, budget=budget, message=message
        )
        db.session.add(contact_message)
        db.session.commit()
        flash('Tin nhắn của bạn đã được gửi thành công!', 'success')
        return redirect(url_for('contact.contact'))

    return render_template('contact.html')