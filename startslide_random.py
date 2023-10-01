from dolphin import event, gui, utils, savestate
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
import os
from copy import copy
from random import getrandbits, randint


def randomize_current_frame(frame):
    global current_frame

    current_frame.accel = not getrandbits(1) if frame < 164 else True
    current_frame.dpad_up = not getrandbits(4)
    current_frame.stick_x = randint(-7, 7)
    current_frame.stick_y = randint(-7, 7)


@event.on_frameadvance
def onFrameAdvance():
    global start_state, best_completion, current_frame, frame_sequence
    stage = classes.RaceInfo.stage()

    if stage == 1:
        frame = core.get_frame_of_input()
        if start_state == None and frame == 0:
            start_state = savestate.save_to_bytes()

        randomize_current_frame(frame)
        TTK_Lib.writePlayerInputs(current_frame)
        frame_sequence.frames.append(copy(current_frame))

    if stage == 2 and start_state != None:
        race_completion = classes.RaceInfoPlayer.race_completion()
        gui.add_osd_message(f"Final race completion:   {race_completion}", 4000)
        gui.add_osd_message(f"Current best completion: {best_completion}", 4000)

        if race_completion > best_completion:
            gui.add_osd_message(
                f"New best completion by   {race_completion - best_completion}", 4000
            )
            best_completion = race_completion
            frame_sequence.writeToFile(
                os.path.join(
                    utils.get_script_dir(),
                    "MKW_Inputs",
                    "Startslides",
                    "best_random_inputs.csv",
                )
            )

        frame_sequence = FrameSequence()
        savestate.load_from_bytes(start_state)


def main() -> None:
    global start_state, best_completion, current_frame, frame_sequence
    start_state = None
    best_completion = float("-inf")
    current_frame = Frame(["", "", "", "", "", ""])
    frame_sequence = FrameSequence()

    current_frame.accel = False
    current_frame.brake = False
    current_frame.item = False
    current_frame.stick_x = 0
    current_frame.stick_y = 0
    current_frame.dpad_up = False
    current_frame.dpad_down = False
    current_frame.dpad_left = False
    current_frame.dpad_right = False
    current_frame.valid = True
    current_frame.iter_idx = 0


if __name__ == "__main__":
    main()
