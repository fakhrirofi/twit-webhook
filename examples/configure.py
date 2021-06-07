from dotenv import load_dotenv
from pyngrok import ngrok
from time import sleep
from twitivity import Activity
import os

load_dotenv(".env")

print("Creating Ngrok process")
http = ngrok.connect(8080, bind_tls=True)
URL = http.public_url
print(f"NGROK_URL: {URL}")
input("Start the webhook, then press enter...")

reg = Activity(
    os.environ["CONSUMER_KEY"],
    os.environ["CONSUMER_SECRET"],
    os.environ["ACCESS_TOKEN"],
    os.environ["ACCESS_TOKEN_SECRET"],
    os.environ["ENV_NAME"],
)

print("Deleting the previous webhook")
reg.delete_all()
print("Registering webhook")
reg.register_webhook(f"{URL}/callback/name_of_the_webhook")
print("Creating subscription")
reg.subscribe()

print("All done!\nDon't close this, Ngrok process is still running...")
while True:
    try:
        sleep(15)
    except KeyboardInterrupt:
        exit()
