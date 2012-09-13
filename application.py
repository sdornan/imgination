from flask import Flask, abort, request, flash, redirect, url_for, render_template, send_from_directory

from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from flask.ext.wtf import Form, FileField, file_allowed, file_required

from datetime import datetime
import os
import redis
from uuid import uuid4

REDIS_PREFIX = 'image:'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ewoipjfisoafsdpo'
app.config['UPLOADS_DEFAULT_DEST'] = UPLOAD_FOLDER


images = UploadSet('images', IMAGES)
configure_uploads(app, images)


class UploadForm(Form):
    upload = FileField('Upload your image',
                        validators=[file_required(),
                                    file_allowed(images, "Images only!")])


@app.route('/', methods=("GET", "POST"))
def home():
    form = UploadForm()
    if form.validate_on_submit():
        filename = images.save(form.upload.data)
        image_id = unicode(uuid4())[:8]
        r = redis.StrictRedis(host='localhost')
        image = {
            'filename': filename,
            'uploaded_by': request.remote_addr,
            'uploaded_at': datetime.now()
        }
        r.hmset(REDIS_PREFIX + image_id, image)
        flash("Success")
        return redirect(url_for('show', id=image_id))

    return render_template('home.html', form=form)


@app.route('/<id>')
def show(id):
    r = redis.StrictRedis(host='localhost')
    image = r.hgetall(REDIS_PREFIX + id)
    if not image:
        abort(404)
    url = images.url(image['filename'])
    return render_template('show.html', url=url, image=image)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)
