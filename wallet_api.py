import os
import signal
import sys
import logging
from aiohttp import web

from utils.create_wallet_tables import create_tables
from wallet.database import db, RegticketDB
from wallet.settings import WALLET_DATABASE_FILE


APP_DIR = None
routes = web.RouteTableDef()
pastel_client = None


def get_artwork_dir():
    return os.path.join(APP_DIR, 'artworks')


def get_pastel_client():
    # this import should be local to let env varibles be set earlier than blockchain object will be created
    # global blockchain object uses env variables for getting pastelID and passphrase
    from wallet.pastel_client import PastelClient
    global pastel_client
    if pastel_client is None:
        pastel_client = PastelClient(pastelid, passphrase)
    return pastel_client


@routes.post('/image_registration_step_2')
async def image_registration_step_2(request):
    """
    - Send regticket to MN0
    - Receive upload_code
    - Upload image
    - Receive worker's fee
    - Store regticket metadata to loca db
    Input {image: path_to_image_file, title: image_title}
    Returns {workers_fee, regticket_id}
    """
    data = await request.json()
    image_path = data['image']
    title = data['title']
    with open(image_path, 'rb') as f:
        content = f.read()
    # try:
    result = await get_pastel_client().image_registration_step_2(title, content)
    # except Exception as ex:
    #     return web.json_response({'error': str(ex)}, status=400)
    regticket_db = RegticketDB.get(RegticketDB.id == result['regticket_id'])
    regticket_db.path_to_image = image_path
    regticket_db.save()
    print('Fee received: {}'.format(result['worker_fee']))
    return web.json_response({'fee': result['worker_fee'], 'regticket_id': regticket_db.id})


@routes.post('/image_registration_step_3')
async def image_registration_step_3(request):
    """
    - Send regticket to mn2, get upload code, upload image to mn2
    - Send regticket to mn3, get upload code, upload image to mn3
    - Verify both MNs accepted images - then return success, else return error
    Input {regticket_id: id}
    Returns transaction id, success/fail
    """
    data = await request.json()
    regticket_id = data['regticket_id']

    response = await get_pastel_client().image_registration_step_3(regticket_id)
    print('Img registration step 3 response: {}'.format(response), file=sys.stderr)
    return web.json_response(response)


@routes.post('/image_registration_cancel')
async def image_registration_cancel(request):
    """
    Input {regticket_id}
    """
    data = await request.json()
    RegticketDB.get(RegticketDB.id == data['regticket_id']).delete_instance()
    return web.json_response({})


@routes.post('/download_image')
async def download_image(request):
    """
    Input {regticket_id}  - id from local DB.
    """
    data = await request.json()
    regticket_db = RegticketDB.get(RegticketDB.id == data['regticket_id'])
    response = await get_pastel_client().download_image(regticket_db.image_hash)
    if response is not None:
        filename = os.path.join(get_artwork_dir(), '{}.jpg'.format(data['regticket_id']))
        with open(filename, 'wb') as f:
            f.write(response)
        return web.json_response({'status': 'SUCCESS', 'filename': filename})
    return web.json_response({'status': 'error', 'msg': 'Image not found on masternodes'})


@routes.post('/ping')
async def ping(request):
    get_pastel_client()
    return web.json_response({})

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise Exception('Usage: ./wallet_api <wallet_dir> <pastelid> <passphrase>')
    APP_DIR = sys.argv[1]
    pastelid = sys.argv[2]
    passphrase = sys.argv[3]
    os.environ.setdefault('PASTEL_ID', pastelid)
    os.environ.setdefault('PASSPHRASE', passphrase)
    if not os.path.exists(get_artwork_dir()):
        os.mkdir(get_artwork_dir())
    db.init(os.path.join(APP_DIR, WALLET_DATABASE_FILE))
    if not os.path.exists(os.path.join(APP_DIR, WALLET_DATABASE_FILE)):
        create_tables()
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, port=5000)
    app.loop.add_signal_handler(signal.SIGINT, app.loop.stop)
