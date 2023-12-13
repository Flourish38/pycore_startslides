from dolphin import event, utils, savestate
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
import os
from time import time
from copy import copy
from random import getrandbits, randint
from pycore_startslides.my_utils.start_boost import *


def randomize_frame(frame, frame_of_input):
    frames_remaining = 239 - frame_of_input
    (a_set, a) = a_forced(frames_remaining)
    if a_set:
        frame.accel = a
    else:
        frame.accel = not getrandbits(1)
    frame.dpad_up = not getrandbits(5)
    if frame_of_input == 0 or not getrandbits(3):
        frame.stick_x = randint(-7, 7)
        frame.stick_y = randint(-7, 7)


@event.on_frameadvance
def onFrameAdvance():
    global start_state, best_completion, current_frame, frame_sequence, start_time
    stage = classes.RaceInfo.stage()
    
    if stage == 0:
        start_time = time()
        savestate.load_from_bytes(start_state)

        # TODO actually make this work
        # Will work well in combination with Gaberboo's multi-ghost code:
        # https://discord.com/channels/1087909304700522549/1087909305400950816/1167688695000858705
        
        # This code currently does nothing.
        num_players = 1
        player_count = classes.RaceDataScenario.player_count()
        if player_count > 1:
            player_vehicle = classes.KartParam.vehicle()
            for idx in range(1, player_count):
                if classes.KartParam.vehicle(idx) == player_vehicle:
                    num_players += 1
                else:
                    break 

    if stage == 1:
        frame = core.get_frame_of_input()

        randomize_frame(current_frame, frame)
        TTK_Lib.writePlayerInputs(current_frame)
        frame_sequence.frames.append(copy(current_frame))
    
    if stage == 2 and start_state != None:
        race_completion = classes.RaceInfoPlayer.race_completion()

        if race_completion > best_completion and len(frame_sequence.frames) == 240:
            print(
                f"New best completion by   {race_completion - best_completion}"
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
        t = time()
        print(
            f"dt: {t - start_time}\tFinal race completion:   {race_completion}\t\tCurrent best completion: {best_completion}"
        )
        start_time = t
        savestate.load_from_bytes(start_state)


def main() -> None:
    global start_state, best_completion, current_frame, frame_sequence, start_time
    
    with open(os.path.join(
                    utils.get_script_dir(),
                    "savestates",
                    "rMC3_Funky Kong_Flame Runner.savestate")
                    , "rb") as f:
        start_state = f.read()
    
    start_time = time()
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
