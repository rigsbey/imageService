import asyncio
import io
import os
import sys
import uuid

import asyncpg
from PIL import Image as pilimg
from gino import Gino
from sanic import Sanic, response
from sanic_jinja2 import SanicJinja2

app = Sanic(__name__)
jinja = SanicJinja2(app, pkg_name="main")
app.static('/static', './static')

db = Gino()


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    path = db.Column(db.Unicode(), default='noname')


@app.listener('before_server_start')
async def bd_adding_listener(app: Sanic, loop):
    print('Server successfully started!')
    await db.set_bind('postgresql://kamil3:adsladsl199812@localhost:5432/gino2')
    await db.gino.create_all()


@app.route(methods=['GET', 'POST'], uri='/upload')
async def upload_img(request):
    template = open(os.getcwd() + "/templates/index.html")
    if request.files:
        args = request.files
        byte_image = args.getlist('file')[0][1]
        original_image = pilimg.open(io.BytesIO(byte_image))
        original_image.thumbnail((256, 256), pilimg.ANTIALIAS)
        pth = "./static/img/" + str(uuid.uuid4()) + ".png"
        original_image.save(pth)
        # Adding to DB
        img = await Image.create(path=pth)
        print("\n\nAdded to DB: \n")
        print(f'path: {img.path}')
        print(f'id:       {img.id}')

    return response.html(template.read())


@app.listener('after_server_stop')
async def bd_adding_listener(app: Sanic, loop):
    print('Server successfully stopped!')
    await db.pop_bind().close()


app.run(host="0.0.0.0", port=5000, debug=True)
