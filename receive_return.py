import asyncio
import os

import aio_pika
from gino import Gino
from sanic import Sanic, response
from sanic_jinja2 import SanicJinja2
from sanic_openapi import swagger_blueprint

app = Sanic(__name__)
app.blueprint(swagger_blueprint)

jinja = SanicJinja2(app)
app.static('/static', './static')

db = Gino()


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    path = db.Column(db.Unicode(), default='noname')

# описать входные и выходные данные
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

# описать входные и выходные данные
@app.route(methods=['GET', 'POST'], uri='/images')
async def return_img(request):
    await db.set_bind('postgresql://kamil3:adsladsl199812@localhost:5432/gino2')

    all_images_path_tuple = await Image.select('path').gino.all()

    def convertTuple(tup):
        res_string = ''.join(tup)
        return res_string

    images_path_tuple_list = []

    for elem in all_images_path_tuple:
        images_path_tuple_list.append(convertTuple(elem))
    print("lenght is: ", len(all_images_path_tuple))
    # exists() и isfile()
    return jinja.render("return_image.html", request, filenames=images_path_tuple_list)


@app.listener('before_server_stop')
async def db_connection_close():
    await db.pop_bind().close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
