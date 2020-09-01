from sanic import Sanic, response
import os
import uuid
from sanic_jinja2 import SanicJinja2
from PIL import Image
import io

app = Sanic(__name__)
jinja = SanicJinja2(app, pkg_name="main")
app.static('/static', './static')


# todo сделать проверку поступившего изображения по имени
@app.route(methods=['GET', 'POST'], uri='/upload')
def upload_img(request):
    template = open(os.getcwd() + "/templates/index.html")
    if request.files:
        args = request.files
        byte_file = args.getlist('file')[0][1]
        original_image = Image.open(io.BytesIO(byte_file))
        original_image.thumbnail((256, 256), Image.ANTIALIAS)
        global ready_image
        ready_image = original_image.save("./static/img/" + str(uuid.uuid4()) + ".png")
    # todo добавить else (???)
    return response.html(template.read())


@app.route(methods=['GET', 'POST'], uri='/images')
def return_img(request):
    # todo сделать вывод всех загруженных изображений

    # return jinja.render("return_image.html", request, img_path=upload_img)
    filenames = os.listdir(os.getcwd() + "/static/img/")
    for elem in filenames:
        # return response.text(body=elem)
        return jinja.render("return_image.html", request, img_path=os.getcwd() + "/static/img/" + elem)


app.run(host="0.0.0.0", port=8000, debug=True)
