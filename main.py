import io
import os
import uuid

from PIL import Image
from sanic import Sanic, response
from sanic_jinja2 import SanicJinja2

app = Sanic(__name__)
jinja = SanicJinja2(app, pkg_name="main")
app.static('/static', './static')


# todo сделать проверку поступившего изображения по имени
@app.route(methods=['GET', 'POST'], uri='/upload')
def upload_img(request):
    template = open(os.getcwd() + "/templates/index.html")
    if request.files:
        args = request.files
        byte_image = args.getlist('file')[0][1]
        original_image = Image.open(io.BytesIO(byte_image))
        original_image.thumbnail((256, 256), Image.ANTIALIAS)
        # if(os.path.isfile("./static/img/" + str(uuid.uuid4()) + ".png")):
        original_image.save("./static/img/" + str(uuid.uuid4()) + ".png")
    return response.html(template.read())

@app.route(methods=['GET', 'POST'], uri='/images')
def return_img(request):
    filenames = os.listdir(os.getcwd() + "/static/img/")
    for elem in filenames:
        return jinja.render("return_image.html", request, img_path="/static/img/" + elem)


app.run(host="0.0.0.0", port=8000, debug=True)
