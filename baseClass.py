import signal
from common import *


def follow(thefile, aliveChecker):
    thefile.seek(0, 2)
    while aliveChecker.poll() == None:
        line = thefile.readline()
        if not line:
            sleep(0.5)
            continue
        yield line


def StartBuild(jsonData):
    global buildingProcess
    buildingProcess = subprocess.Popen("/usr/bin/env make > .BuildOutput 2>.BuildError", cwd=os.path.join(os.getcwd(),
                   "../Projects/"+jsonData["Project"]), shell=True, preexec_fn=os.setsid)

def StartClean(jsonData):
    global buildingProcess
    buildingProcess = subprocess.Popen("/usr/bin/env make clean > .BuildOutput 2>.BuildError", cwd=os.path.join(os.getcwd(),
                   "../Projects/"+jsonData["Project"]), shell=True, preexec_fn=os.setsid)

def SendBuildOut(jsonData):
    print("called")
    global buildingProcess
    try:
        logfile = open(os.path.join(os.getcwd(), "../Projects/" +
                    jsonData["Project"]+"/.BuildOutput"), "r")
    except:
        SendBuildOut(jsonData)
        return
    loglines = follow(logfile, buildingProcess)
    socketio.emit("RunningStatus", {"data": True})
    for line in loglines:
        print("sending "+line)
        socketio.emit("BuildLog", {"line": line})
    logfile.close()


def SendBuildErr(jsonData):
    print("called")
    global buildingProcess
    try:
        errfile = open(os.path.join(os.getcwd(), "../Projects/" +
                    jsonData["Project"]+"/.BuildError"), "r")
    except:
        SendBuildErr(jsonData)
        return
    errlines = follow(errfile, buildingProcess)
    socketio.emit("RunningStatus", {"data": True})
    for line in errlines:
        print("sending "+line)
        socketio.emit("BuildError", {"line": line})
    errfile.close()
    print("Done exiting")


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
            subprocess.Popen(["/usr/bin/env", "ttyd", "-p",
                             jsonData["port"], "--writable", "-o", "bash"])
            socketio.emit("ConsoleStarted", {"data": jsonData["port"]})

    @socketio.on('StartBuild')
    def HandleStartBuild(jsonData):
        # global buildingProcess
        # buildingProcess = multiprocessing.Process(target=StartBuild, args=(jsonData,))
        # buildingProcess.start()
        StartBuild(jsonData)
        buildingLogs = threading.Thread(target=SendBuildOut, args=(jsonData,))
        buildingLogs.start()
        buildingErr = threading.Thread(target=SendBuildErr, args=(jsonData,))
        buildingErr.start()

    @socketio.on('StopBuild')
    def HandleStopBuild(jsonData):
        global buildingProcess
        # print(buildingProcess.pid)
        # os.kill(buildingProcess.pid, signal.SIGINT)
        # buildingProcess.send_signal(signal.SIGINT)
        os.killpg(os.getpgid(buildingProcess.pid), signal.SIGINT)
        print("stopped build!")
        socketio.emit("RunningStatus", {"data": False})

    @socketio.on("KillBuild")
    def HandleKillBuild(jsonData):
        global buildingProcess
        # buildingProcess.kill()
        os.killpg(os.getpgid(buildingProcess.pid), signal.SIGKILL)
        print("killed build!")
        socketio.emit("RunningStatus", {"data": False})

    @socketio.on("CleanProject")
    def HandleCleanProject(jsonData):
        StartClean(jsonData)
        buildingLogs = threading.Thread(target=SendBuildOut, args=(jsonData,))
        buildingLogs.start()
        buildingErr = threading.Thread(target=SendBuildErr, args=(jsonData,))
        buildingErr.start()
        buildingProcess.wait()
        socketio.emit("CleanProjectStatus", {"data": True})

    @socketio.on("CheckRunningStatus")
    def HandleCheckRunningStatus(jsonData):
        global buildingProcess
        if buildingProcess == None:
            socketio.emit("RunningStatus", {"data": False})
            return
        socketio.emit("RunningStatus", {"data": buildingProcess.poll()})

    @socketio.on("GetAvailableProjects")
    def HandleGetAvailableProjects(jsonData):
        onlyDirs = [f for f in os.listdir("../Projects") if os.path.isdir(os.path.join("../Projects", f))]
        socketio.emit("ListAvailableProjects", {"Projects": onlyDirs})


class GitController:
    def __init__(self) -> None:
        self.CloneProgress = CloneProgress()

    def Clone(self, url: str, directory: str):
        projectName = ""
        if directory == "":
            projectName = url.split("/")[-1].removesuffix(".git")
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
