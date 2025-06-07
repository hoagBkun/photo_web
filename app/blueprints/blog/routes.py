from flask import Blueprint, render_template
from app.models.post import Post
from app.models.banner import Banner

blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

@blog_bp.route('/')
def index():
    posts = Post.query.all()
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/blog.html', posts=posts, banners=banners)

@blog_bp.route('/<int:id>')
def blog_detail(id):
    post = Post.query.get_or_404(id)
    prev_post = Post.query.filter(Post.id < id).order_by(Post.id.desc()).first()
    next_post = Post.query.filter(Post.id > id).order_by(Post.id.asc()).first()
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/blog_detail.html', post=post, prev_post=prev_post, next_post=next_post, banners=banners)