#import reapy
import asyncio
from SoundscapeVRCommunications.SoundscapeVRCommunicationsService import SoundscapeVRCommunicationsService
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig

#Reaper project
#project = reapy.Project()

async def main():
    config = SoundscapeReapyControllerConfig()
    communicator = SoundscapeVRCommunicationsService(config)

    await communicator.start() # blocks until Unity connects

    while True:
        request = await communicator.receiveRequest()
        print(request)

if __name__ == '__main__':
    asyncio.run(main())