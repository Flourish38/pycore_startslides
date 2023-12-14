from dolphin import event, utils, savestate
from Modules import TTK_Lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
import os
from time import time
from copy import copy
from random import getrandbits, randint, random
from pycore_startslides.my_utils.start_boost import *

class Slide:
    def __init__(self):
        self.accel = []
        self.dpad_up = []
        self.stick_x = []
        self.stick_x_values = []
        self.stick_y = []
        self.stick_y_values = []

    def apply(self, frame, frame_of_input):
        # If the frame is in the list, then wheelie on that frame.
        frame.dpad_up = frame_of_input in self.dpad_up
        
        frame.accel = False
        for f in self.accel:
            if f > frame_of_input:
                break
            # Every frame in the list *toggles* the A button. For now. We'll see
            frame.accel = not frame.accel
        
        frame.stick_x = 0
        for i in range(len(self.stick_x)):
            if self.stick_x[i] > frame_of_input:
                break
            frame.stick_x = self.stick_x_values[i]
        
        frame.stick_y = 0
        for i in range(len(self.stick_y)):
            if self.stick_y[i] > frame_of_input:
                break
            frame.stick_y = self.stick_y_values[i]

    def mutate(self):
        # Always do at least one mutation
        while not self.single_mutation():
            pass

        # Each subsequent mutation has a 3/4 chance of happening, up to a max of 16 times.
        # This gives an expected value of almost exactly 4 mutations each time. (I calculate ~3.97)
        bits = getrandbits(32)
        while bits & 0b11 != 0b00:
            # This makes sure that at least SOMETHING happens.
            while not self.single_mutation():
                pass
            bits >>= 2
    
    def single_mutation(self):
        r = random()
        if r < 0.5:
            return self.modify(2*r)
        elif r < 5/6:
            return self.add(3*(r-0.5))
        else:
            return self.remove(6*(1-r))
    
    def modify(self, r):
        # r is a random value ranging from 0-1
        # I am doing this because I have trained myself to be averse to needless rng calls. -_-
        # It doesn't really make the function much more complicated anyways...
        n = 1
        bits = getrandbits(32)
        while bits & 0b11 != 0b00:
            n += 1
            bits >>= 2
        
        index_scalar = 12*r - int(12*r)
        
        if r < 1/6:
            i = int(len(self.wheelie) * index_scalar)
            new = self.wheelie[i]
            if r < 1/12:
                new -= n
                if (i > 0 and self.wheelie[i-1] > new - 20) or new < 0:
                    return False
            else:
                new += n
                if (i < len(self.wheelie) - 1 and self.wheelie[i+1] < new + 20) or new > 239:
                    return False
            self.wheelie[i] = new
            return True
        elif r < 2/6:
            i = int(len(self.accel) * index_scalar)
            new = self.accel[i]
            if r < 3/12:
                new -= n
                if (i > 0 and self.accel[i-1] >= new) or new < 0:
                    return False
            else:
                new += n
                if (i < len(self.accel) - 1 and self.accel[i+1] <= new) or new > 239:
                    return False
            self.accel[i] = new
            return True
        elif r < 3/6:
            i = int(len(self.stick_x) * index_scalar)
            new = self.stick_x[i]
            if r < 5/12:
                new -= n
                if (i > 0 and self.stick_x[i-1] >= new) or new < 0:
                    return False
            else:
                new += n
                if (i < len(self.stick_x) - 1 and self.stick_x[i+1] <= new) or new > 239:
                    return False
            self.stick_x[i] = new
            return True
        elif r < 4/6:
            i = int(len(self.stick_y) * index_scalar)
            new = self.stick_y[i]
            if r < 7/12:
                new -= n
                if (i > 0 and self.stick_y[i-1] >= new) or new < 0:
                    return False
            else:
                new += n
                if (i < len(self.stick_y) - 1 and self.stick_y[i+1] <= new) or new > 239:
                    return False
            self.stick_y[i] = new
            return True
        elif r < 5/6:
            i = int(len(self.stick_x_values) * index_scalar)
            # Not nearly as worried about rejecting invalid values.
            # Extreme stick values are more likely to be useful anyways.
            # This also means that stick values will be modified slightly more often,
            # Which doesn't sound bad to me. They do have more potential values, after all.
            self.stick_x_values[i] = max(-7, min(7, self.stick_x_values[i] + (-n if r < 9/12 else n)))
            return True
        else:
            i = int(len(self.stick_y_values) * index_scalar)
            # Same as above.
            self.stick_y_values[i] = max(-7, min(7, self.stick_y_values[i] + (-n if r < 11/12 else n)))
            return True
            



def update_frame(frame, frame_of_input):
    frames_remaining = 239 - frame_of_input
    
    
    (a_set, a) = a_forced(frames_remaining)
    if a_set:
        frame.accel = a
    


@event.on_frameadvance
def onFrameAdvance():
    global start_state, best_completion, current_frame, frame_sequence, start_time
    stage = classes.RaceInfo.stage()
    
    if stage == 0:
        start_time = time()
        savestate.load_from_bytes(start_state)

    if stage == 1:
        frame = core.get_frame_of_input()

        update_frame(current_frame, frame)
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
