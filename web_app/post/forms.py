from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from flask_pagedown.fields import PageDownField



class PostForm(FlaskForm):
    body = PageDownField('想写些什么？', validators=[DataRequired(message='Post不能为空')])
    submit = SubmitField('Post!')


class CommentForm(FlaskForm):
    body = StringField('输入您的评论', validators=[DataRequired(message='评论不能为空')])
    submit = SubmitField('Comment！')
