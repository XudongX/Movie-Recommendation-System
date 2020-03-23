from flask import Blueprint

post = Blueprint('post', __name__)

from . import views, errors
from ..models.user_model import Permission


@post.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
