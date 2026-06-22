import time
from pathlib import Path
from datetime import datetime
from TrackDiscJockey.ControllerWorkspace import ControllerWorkspace

class PlayDelayMeasure(ControllerWorkspace):
    print_delay_message = True
    save_to_file = True
    delays_file = "{REAPY_CONTROLLER_DIR}/logs/PlayDelays.csv"
    clock_offset: int = 0

    @classmethod
    def set_clock_offset(cls, offset: int):
        cls.clock_offset = offset


    @classmethod
    def measure_delay(cls, timestamp):
        delay_count = time.time_ns() // 1_000_000 - timestamp - PlayDelayMeasure.clock_offset

        if PlayDelayMeasure.print_delay_message:
            print(f"Soundscape started with a delay of {delay_count}ms")
        if PlayDelayMeasure.save_to_file:
            PlayDelayMeasure.save_measure_to_file(delay_count)

    @classmethod
    def save_measure_to_file(cls, delay_time):
        delay_file_path = Path(cls._get_project_file_path(PlayDelayMeasure.delays_file)).resolve()
        delay_file_path.parent.mkdir(parents=True, exist_ok=True)  # create ./logs/ if missing

        if not delay_file_path.exists():
            delay_file_path.touch()  # create the empty file

        dt = datetime.now().isoformat(timespec="seconds")

        write_header = delay_file_path.stat().st_size == 0  # file is empty
        with delay_file_path.open("a", encoding="utf-8") as f:
            if write_header:
                f.write("delay;date_time\n")
            f.write(f"{delay_time}ms;{dt}\n")