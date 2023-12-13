from dolphin import event, utils, savestate
from Modules import mkw_classes as classes
from Modules import mkw_translations as translate
import os

@event.on_frameadvance
def onFrameAdvance():
    # intro_timer == 171 is the frame before the start of input
    # intro_timer == 172 for the whole race
    if classes.RaceInfo.intro_timer() == 171:
        state = savestate.save_to_bytes()
        with open(os.path.join(
                    utils.get_script_dir(),
                    "savestates",
                    f"{translate.course_slot_abbreviation()}_{translate.character_id()}_{translate.vehicle_id()}.savestate"
                ), "wb") as f:
            f.write(state)
            print(f"Wrote savestate {f.name}")

