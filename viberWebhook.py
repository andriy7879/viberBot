from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
import logging
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest

app = Flask(__name__)
# сюда нужно вставить инфу со своего бота
viber = Api(BotConfiguration(
    name='rorextermobileapp',
    avatar='http://site.com/avatar.jpg',
    auth_token='51ae52131ea7e51c-9fcb75c341c5804b-df39aea10a6d287f'
))

try:
    viber.set_webhook('https://regal-phoenix-72e850.netlify.app')
except Exception as e:
    if hasattr(e, 'result') and 'status' in e.result:
        status = e.result['status']
        if status != 0:
            print(f"Failed to set the webhook. Status: {status}")
        else:
            print("Webhook was set successfully.")
    else:
        print("Failed to set the webhook. Unexpected response structure.")

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        # lets echo back
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True)
