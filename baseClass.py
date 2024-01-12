from common import *

class Main:
    def __init__(self) -> None:
        self.GitController = GitController()

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
