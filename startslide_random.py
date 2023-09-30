from dolphin import event, gui, utils, savestate
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
from random import getrandbits, randint


def randomize_frame():
    global currentFrame

    currentFrame.accel = not getrandbits(1)
    currentFrame.dpad_up = not getrandbits(1)
    currentFrame.stick_x = randint(-7, 7)
    currentFrame.stick_y = randint(-7, 7)


@event.on_frameadvance
def onFrameAdvance():
    global currentFrame, slot_zero_valid
    stage = classes.RaceInfo.stage()

    if stage == 1:
        if not slot_zero_valid and core.get_frame_of_input() == 0:
            slot_zero_valid = True
            # This crashes dolphin
            savestate.save_to_slot(0)

        randomize_frame()
        TTK_Lib.writePlayerInputs(currentFrame)

    if stage == 2 and slot_zero_valid:
        race_completion = classes.RaceInfoPlayer.race_completion()
        gui.add_osd_message(f"Final Race Completion: {race_completion}")
        # This also crashed dolphin when I ran it, but there was nothing saved to the slot.
        savestate.load_from_slot(0)


def main() -> None:
    global currentFrame, slot_zero_valid
    slot_zero_valid = False
    currentFrame = Frame(["", "", "", "", "", ""])

    currentFrame.accel = False
    currentFrame.brake = False
    currentFrame.item = False
    currentFrame.stick_x = 0
    currentFrame.stick_y = 0
    currentFrame.dpad_up = False
    currentFrame.dpad_down = False
    currentFrame.dpad_left = False
    currentFrame.dpad_right = False
    currentFrame.valid = True
    currentFrame.iter_idx = 0


if __name__ == "__main__":
    main()
