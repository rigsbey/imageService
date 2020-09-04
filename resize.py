import asyncio
import io
import os
import sys
import uuid

import aio_pika
from PIL import Image
from gino import Gino
from sanic import Sanic, response
from sanic_jinja2 import SanicJinja2

app = Sanic(__name__)
jinja = SanicJinja2(app)
app.static('/static', './static')

db = Gino()


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    path = db.Column(db.Unicode(), default='noname')


@app.route(methods=['GET', 'POST'], uri='/upload')
async def upload_img(request):
    loop = asyncio.get_event_loop()

    template = open(os.getcwd() + "/templates/index.html")
    if request.files:
        args = request.files
        byte_image = args.getlist('file')[0][1]
        #     подключение к aio-pika, создание очереди  и пеердача в очередь [путь или набор байтов]
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@localhost/", loop=loop
        )
        async with connection:
            routing_key = "image_path"  # название очереди
            # создание очереди
            channel = await connection.channel()

            await channel.default_exchange.publish(
                aio_pika.Message(byte_image),
                routing_key=routing_key,
            )
        await connection.close()

    return response.html(template.read())


@app.route(methods=['GET', 'POST'], uri='/images')
async def return_img(request):
    await db.set_bind('postgresql://kamil3:adsladsl199812@localhost:5432/gino2')

    all_images_path = await Image.select('path').gino.all()

    filenames = os.listdir(os.getcwd() + "/static/img/")
    print(all_images_path)
    return jinja.render("return_image.html", request, imgpath="/static/img/", filenames=filenames)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
