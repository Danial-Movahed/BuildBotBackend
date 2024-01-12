from common import *
from baseClass import *

CORS(app)
mainApp = Main()

@app.route('/git/clone', methods=['POST'])
def git_clone():
    req = request.get_json()
    t = threading.Thread(target=mainApp.GitController.Clone, args=(
        req["URL"].strip(), req["Directory"].strip()))
    t.start()
    return "", 204


if __name__ == "__main__":
    print("Starting server...")
    socketio.run(app, "0.0.0.0", 443, debug=True, ssl_context=('/etc/letsencrypt/live/seyeddanialmovahed.eu.org/fullchain.pem', '/etc/letsencrypt/live/seyeddanialmovahed.eu.org/privkey.pem'))
