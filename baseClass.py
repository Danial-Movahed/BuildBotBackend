from common import *


class Main:
    def __init__(self) -> None:
        self.GitController = GitController()
        self.t = threading.Thread(target=self.SendSystemUsage)
        self.t.start()

    def SendSystemUsage(self):
        while True:
            socketio.emit("SystemUsageStat", {
                "CPU": psutil.cpu_percent(),
                "Memory": psutil.virtual_memory()[2],
                "Disk": psutil.disk_usage("/")[3]
            })
            sleep(2)

    @socketio.on('Console')
    def HandleConsole(jsonData):
        if jsonData["data"] == "Start":
            t = threading.Thread(target=lambda p: subprocess.Popen(
                ["/usr/bin/env", "ttyd", "-p", p, "--writable", "-o", "bash"]), args=(jsonData["port"],))
            t.start()
            socketio.emit("ConsoleStarted", {"data": jsonData["port"]})


class GitController:
    def __init__(self) -> None:
        self.CloneProgress = CloneProgress()

    def Clone(self, url: str, directory: str):
        projectName = ""
        if directory == "":
            projectName = url.split("/")[-1].removesuffix(".git")
            directory = os.path.join(os.getcwd(), "../Projects/"+projectName)
        else:
            projectName = directory
            directory = os.path.join(os.getcwd(), "../Projects/"+projectName)
        try:
            git.Repo.clone_from(url, directory, progress=self.CloneProgress)
            socketio.emit('CloneStatus', {"data": 'Success'})
        except Exception as e:
            socketio.emit("CloneStatus", {"data": str(e)})
            print(str(e))


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()

    def update(self, op_code, cur_count, max_count=None, message=''):
        socketio.emit("CloneMaxProgress", max_count)
        socketio.emit("CloneProgress", cur_count)
