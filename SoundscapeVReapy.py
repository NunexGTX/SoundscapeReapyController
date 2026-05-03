import reapy
import asyncio
import sys
from SoundscapeVRCommunications.SoundscapeVRCommunicationsService import SoundscapeVRCommunicationsService
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig

#Reaper project
project = None
config = None
communicator = None

def ReapyInit():
    print("SoundscapeVReapy Initializing...")

    print("Checking if reaper is working")
    check_reaper_running()

    #Read config file
    print("Reading config.json")
    config = SoundscapeReapyControllerConfig()

    #Open the template project on reapy
    print(f"Opening {config.ReapyTemplateProjectPath} in Reaper DAW")
    reapy.open_project(config.ReapyTemplateProjectPath)

    #Get that project
    print("Retrieving Reapy's DAW Project")
    project = reapy.Project()
    
    print("SoundscapeVReapy Ready!")
    print()

def check_reaper_running():
    distant_api_enabled = reapy.dist_api_is_enabled()
    if not distant_api_enabled:
        #Reapy is not running or the api was not configured properly
        print()
        print("-> Reapy is either not opened or inaccessible")
        print("Make Sure Reapy is opened and that you ran reapy's initial configuration step with you current python environment")
        print("To do that, reset you reaper's configuration and run the command below with your python venv: ")
        print(f'     python -c "import reapy; reapy.configure_reaper()"')
        print()
        sys.exit(1) #Exited because reaper was unvailable
    print("Reaper DAW Connection: OK")


def Reset():
    '''Resets reaper project and its tracks'''
    pass

def Exit(communicator: SoundscapeVRCommunicationsService):
    print()
    print("Exitting...")
    communicator.disconnect()
    print("Goodbye...")
    #sys.exit(0) #Stop execution
    #----END----

async def main():
    config = SoundscapeReapyControllerConfig()
    communicator = SoundscapeVRCommunicationsService(config)

    try:
        await communicator.start() # blocks until Unity connects
        while True:
            request = await communicator.receiveRequest()
            await communicator.sendResponse("OK")
    except asyncio.CancelledError:
        Exit(communicator)
    finally:
        pass
            

if __name__ == '__main__':
    ReapyInit()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass