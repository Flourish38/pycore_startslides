from dolphin import event, gui, utils, savestate
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
import os
from copy import copy
from random import getrandbits, randint


def frames_up_to_full_boost(start_charge):
    output = 0
    while start_charge < 0.94:
        output += 1
        start_charge = 0.982 * start_charge + 0.02
    return output


def frames_down_to_full_boost(start_charge):
    output = 0
    while start_charge > 0.95:
        output += 1
        start_charge *= 0.96
    # There's a very good chance this will drop you out of range,
    # so add on the number of frames to get back up in range.
    return output + frames_up_to_full_boost(start_charge)


def randomize_frame(frame, frame_of_input, holding_a):
    a_set = False
    if holding_a or frame_of_input == 239:
        frame.accel = True
        a_set = True
    # 136 is the first frame we might need to start holding A, since it takes 103 frames to get to full start boost from 0
    elif frame_of_input >= 136:
        charge = classes.KartState.start_boost_charge()
        if charge < 0.94:
            # Check to see if, if we DON'T push A, can we still get full start boost?
            if frames_up_to_full_boost(0.96 * charge) + frame_of_input > 238:
                frame.accel = True
                holding_a = True
                a_set = True
        elif charge > 0.95 and frame_of_input >= 231:
            # Check to see if, if we DO push A, can we still not burn out?
            if (
                frames_down_to_full_boost(min(1, 0.982 * charge + 0.02))
                + frame_of_input
                > 238
            ):
                frame.accel = False
                a_set = True
    if not a_set:
        frame.accel = not getrandbits(1)
    frame.dpad_up = not getrandbits(4)
    if frame_of_input == 0 or not getrandbits(3):
        frame.stick_x = randint(-7, 7)
        frame.stick_y = randint(-7, 7)

    return holding_a


@event.on_frameadvance
def onFrameAdvance():
    global start_state, best_completion, current_frame, frame_sequence, holding_a
    stage = classes.RaceInfo.stage()

    # intro_timer == 171 is the frame before the start of input
    # intro_timer == 172 for the whole race
    if classes.RaceInfo.intro_timer() == 171:
        start_state = savestate.save_to_bytes()

    if stage == 1:
        frame = core.get_frame_of_input()

        holding_a = randomize_frame(current_frame, frame, holding_a)
        TTK_Lib.writePlayerInputs(current_frame)
        frame_sequence.frames.append(copy(current_frame))

    if stage == 2 and start_state != None:
        race_completion = classes.RaceInfoPlayer.race_completion()
        gui.add_osd_message(
            f"Final race completion:   {race_completion}\nCurrent best completion: {best_completion}",
            3000,
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

        holding_a = False
        frame_sequence = FrameSequence()
        savestate.load_from_bytes(start_state)


def main() -> None:
    global start_state, best_completion, current_frame, frame_sequence, holding_a
    start_state = None
    best_completion = float("-inf")
    current_frame = Frame(["", "", "", "", "", ""])
    frame_sequence = FrameSequence()
    holding_a = False

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
