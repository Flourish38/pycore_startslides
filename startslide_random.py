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
    global currentFrame
    stage = classes.RaceInfo.stage()

    if stage == 1:
        randomize_frame()
        TTK_Lib.writePlayerInputs(currentFrame)


def main() -> None:
    global currentFrame
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
