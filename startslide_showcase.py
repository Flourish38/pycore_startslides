from dolphin import event, gui, utils
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence
import os


@event.on_savestateload
def onStateLoad(is_slot, slot):
    playerInputs.readFromFile()


@event.on_frameadvance
def onFrameAdvance():
    global playerInputs
    frame = core.get_frame_of_input()
    stage = classes.RaceInfo.stage()

    playerInput = playerInputs[frame]
    if playerInput and stage == 1:
        TTK_Lib.writePlayerInputs(playerInput)

    if stage == 2:
        if frame == 240:
            gui.add_osd_message(
                f"""Race completion: {classes.RaceInfoPlayer.race_completion()}\n
                    Boost frames: {classes.KartBoost.all_mt()}"""
            )
        elif frame == 241:
            utils.toggle_play()


def main() -> None:
    global playerInputs
    playerInputs = FrameSequence(
        os.path.join(
            utils.get_script_dir(),
            "MKW_Inputs",
            "Startslides",
            "best_random_inputs.csv",
        )
    )


if __name__ == "__main__":
    main()
