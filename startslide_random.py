from dolphin import event, gui, utils, savestate
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
import os
from copy import copy
from random import getrandbits, randint
from pycore_startslides.my_utils.start_boost import *


def randomize_frame(frame, frame_of_input):
    frames_remaining = 239 - frame_of_input
    (a_set, a) = a_forced(frames_remaining)
    if a_set:
        frame.accel = a
    else:
        frame.accel = not not getrandbits(4)
    frame.dpad_up = not getrandbits(5)
    if frame_of_input == 0 or not getrandbits(3):
        frame.stick_x = randint(-7, 7)
        frame.stick_y = randint(-7, 7)


@event.on_frameadvance
def onFrameAdvance():
    global start_state, best_completion, current_frame, frame_sequence
    stage = classes.RaceInfo.stage()

    # intro_timer == 171 is the frame before the start of input
    # intro_timer == 172 for the whole race
    if classes.RaceInfo.intro_timer() == 171:
        frame_sequence = FrameSequence()
        start_state = savestate.save_to_bytes()

    if stage == 1:
        frame = core.get_frame_of_input()

        randomize_frame(current_frame, frame)
        TTK_Lib.writePlayerInputs(current_frame)
        frame_sequence.frames.append(copy(current_frame))

    if stage == 2 and start_state != None:
        race_completion = classes.RaceInfoPlayer.race_completion()
        gui.add_osd_message(
            f"Final race completion:   {race_completion}\nCurrent best completion: {best_completion}\nBoost frames: {classes.KartBoost.all_mt()}",
            1500,
        )

        if race_completion > best_completion:
            gui.add_osd_message(
                f"New best completion by   {race_completion - best_completion}", 3000
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

    boost_init_70f()
    precalculate_lists()


if __name__ == "__main__":
    main()
