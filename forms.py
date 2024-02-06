from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired

class URLForm(FlaskForm):
    url = StringField('URL:', validators=[DataRequired()])
    submit = SubmitField('Submit')
