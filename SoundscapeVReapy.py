import reapy
import asyncio
import sys
from SoundscapeVRCommunications.SoundscapeVRCommunicationsService import SoundscapeVRCommunicationsService
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig
from TrackDiscJockey.TrackSoundscapeDJManager import TrackSoundscapeDJManager

project = None
config = None
communicator = None
ReapyManager = None

def ReapyInit():
    global project, config
    print("SoundscapeVReapy Initializing...")
    print("Checking if reaper is working")
    check_reaper_running()

    print("Reading config.json")
    config = SoundscapeReapyControllerConfig()

    print(f"Opening {config.ReapyTemplateProjectPath} in Reaper DAW")
    reapy.open_project(config.ReapyTemplateProjectPath)

    print("Retrieving Reapy's DAW Project")
    project = reapy.Project()
    print("SoundscapeVReapy Ready!\n")

def check_reaper_running():
    if not reapy.dist_api_is_enabled():
        print("\n-> Reapy is either not opened or inaccessible")
        print("Make Sure Reapy is opened and that you ran reapy's initial configuration step")
        print('     python -c "import reapy; reapy.configure_reaper()"')
        sys.exit(1)
    print("Reaper DAW Connection: OK")

def Reset():
    global project, ReapyManager
    reapy.open_project(config.ReapyTemplateProjectPath)
    project = reapy.Project()
    ReapyManager = TrackSoundscapeDJManager(project, config)

def Exit(communicator: SoundscapeVRCommunicationsService):
    print("\nExitting...")
    communicator.disconnect()
    print("Goodbye...")

async def main():
    global communicator, ReapyManager
    communicator = SoundscapeVRCommunicationsService(config)
    ReapyManager = TrackSoundscapeDJManager(project, config)

    try:
        await communicator.start()
        while True:
            request = await communicator.receiveRequest()
            if "RESET" in request:
                Reset()
                response = "Reaper Project has been reset"
            else:
                response = ReapyManager.CommandReceive(request)
            await communicator.sendResponse(response)
    except asyncio.CancelledError:
        Exit(communicator)

if __name__ == '__main__':
    ReapyInit()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass