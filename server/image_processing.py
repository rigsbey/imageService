import asyncio
import io
import os
import uuid

import aio_pika
from PIL import Image as imgPil
from PIL import ImageDraw
from gino import Gino

db = Gino()


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    path = db.Column(db.Unicode(), default='noname')


async def main(loop):
    try:
        await asyncio.sleep(7)
        await db.set_bind('postgresql://kamil3:adsladsl199812@postgres/gino2')

        print("bd started")
    except Exception as error:
        print('Error connecting database', error)

    await db.gino.create_all()

    try:
        await asyncio.sleep(7)
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@rabbitmq", loop=loop
        )
        queue_name = "image_path"
        async with connection:
            # Creating channel
            channel = await connection.channel()
            # Declaring queue
            queue = await channel.declare_queue(queue_name, auto_delete=True)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():

                        original_image = imgPil.open(io.BytesIO(message.body))

                        original_image.thumbnail((128, 128), imgPil.ANTIALIAS)
                        orig_img_path = "./static/img/" + str(uuid.uuid4()) + ".png"
                        original_image.save(orig_img_path)

                        image = imgPil.open(orig_img_path)  # Открываем изображение
                        draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования
                        width = image.size[0]  # Определяем ширину
                        height = image.size[1]  # Определяем высоту
                        pix = image.load()  # Выгружаем значения пикселей

                        for x in range(width):
                            for y in range(height):
                                r = pix[x, y][0]
                                g = pix[x, y][1]
                                b = pix[x, y][2]
                                draw.point((x, y), (255 - r, 255 - g, 255 - b))

                        image.save(orig_img_path)

                        # Adding to DB
                        img = await Image.create(path=orig_img_path)
                        print("\n\nAdded to DB: \n")
                        print(f'path: {img.path}')
                        print(f'id:       {img.id}')

    except ConnectionError:
        print('waiting for connection(AIO-PIKA)')



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()