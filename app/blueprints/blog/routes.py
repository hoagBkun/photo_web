from flask import Blueprint, render_template
from app.models.post import Post

blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

@blog_bp.route('/')
def index():
    posts = Post.query.all()
    return render_template('blog.html', posts=posts)

@blog_bp.route('/<int:id>')
def blog_detail(id):
    post = Post.query.get_or_404(id)
    return render_template('blog_detail.html', post=post)