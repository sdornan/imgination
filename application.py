from flask import Flask, request, flash, redirect, url_for, render_template

from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from flask.ext.wtf import Form, FileField, file_allowed, file_required

from werkzeug import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ewoipjfisoafsdpo'


images = UploadSet('images', IMAGES, default_dest=lambda app: '/uploads/')
configure_uploads(app, images)



class UploadForm(Form):
    upload = FileField('Upload your image',
                        validators=[file_required(),
                                    file_allowed(images, "Images only!")])


@app.route('/', methods=("GET", "POST"))
def home():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.upload.data.filename)
        flash("Success")
    else:
        filename = None
    return render_template('home.html', form=form, filename=filename)


# @app.route('/images/<id>')
# def show(id):
#     image = 



if __name__ == '__main__':
    app.run(debug=True)
