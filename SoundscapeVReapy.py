#import reapy
import asyncio
import sys
from SoundscapeVRCommunications.SoundscapeVRCommunicationsService import SoundscapeVRCommunicationsService
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig

#Reaper project
project = None
config = None
communicator = None

def ReapyInit():
    #Open Reapy

    #Open the template project on reapy

    #Get that project
    #project = reapy.Project()
    pass

def Reset():
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