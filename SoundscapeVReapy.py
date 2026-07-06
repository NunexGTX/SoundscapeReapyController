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

DISCONNECT_END_SOUNDSCAPE_DELAY_MS = 5000

def ReapyInit():
    global project, config
    print("SoundscapeVReapy Initializing...")
    print("Checking if reaper is working")
    check_reaper_running()

    print("Reading config.json")
    config = SoundscapeReapyControllerConfig()

    print(f"Opening {config.ReapyTemplateProjectPath} in Reaper DAW")
    print("   ⚠️  If REAPER is asking you to save the current project, click 'Don't Save' to continue.")
    print()
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
    #reapy.open_project(config.ReapyTemplateProjectPath)
    print("Goodbye...")

async def main():
    global communicator, ReapyManager
    communicator = SoundscapeVRCommunicationsService(config)
    ReapyManager = TrackSoundscapeDJManager(project, config)

    await communicator.start() # Binds the server

    while True:
        try:
            # If we aren't connected (first time or after a disconnect), wait.
            if not communicator.is_connected:
                await communicator.wait_for_connection()

            request = await communicator.receiveRequest()
            
            if "RESET" in request:
                Reset()
                response = "Reaper Project has been reset"
            else:
                response = ReapyManager.CommandReceive(request)
                
            await communicator.sendResponse(response)

        except (ConnectionResetError, OSError):
            # This catches the disconnect.
            # The service handles cleanup internally, so we just loop back
            # and wait for a new connection.
            print("Unity client disconnected. Waiting for a new session...")
            await asyncio.sleep(DISCONNECT_END_SOUNDSCAPE_DELAY_MS/1000)
            print("Forcefully Ending Soundscape due to lost connection, without a successful reconnection.")
            ReapyManager.CommandReceive('{"command": "end_soundscape"}') #Ends the soundscape
            continue
        except asyncio.CancelledError:
            Exit(communicator)
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == '__main__':
    ReapyInit()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass