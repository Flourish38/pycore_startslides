from dolphin import event, utils, savestate
from Modules import ttk_lib
from Modules import mkw_classes as classes
from Modules import mkw_core as core
from Modules import mkw_translations as translate
from Modules.framesequence import FrameSequence, Frame
import os
from time import time
from copy import copy, deepcopy
from random import getrandbits, randint, random, randrange
from pycore_startslides.my_utils.start_boost import *

class Slide:
    def __init__(self):
        self.keyframes = []
        self.is_wheelie = []
        self.stick_x_values = []

    def apply(self, frame, frame_of_input):
        frame.dpad_up = False
        frame.stick_x = 0
        for i in range(len(self.keyframes)):
            f = self.keyframes[i]
            if f > frame_of_input:
                break
            if f == frame_of_input:
                frame.dpad_up = self.is_wheelie[i]
            frame.stick_x = self.stick_x_values[i]
            

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
            return self.modify()
        elif r < 5/6:
            return self.add()
        else:
            return self.remove()
    
    def modify(self):
        
        index_to_change = randint(0, len(self.keyframes)-1)
        
        if random() < 0.5: # Modify one of the keyframes
            n = 1
            bits = getrandbits(32)
            while bits & 0b11 != 0b00:
                n += 1
                bits >>= 2
            f = self.keyframes[index_to_change]
            if random() < 0.5:
                for i in range(1, index_to_change+1):
                    f_i = self.keyframes[index_to_change-i]
                    if f_i + 20 < f - n:
                        break
                    if f_i >= f - n or (self.is_wheelie[index_to_change-i] and (f_i + 13 >= f - n or (self.is_wheelie[index_to_change] and f_i + 19 >= f - n))):
                        return False
                self.keyframes[index_to_change] = f - n
                return True
            else:
                for i in range(1, len(self.keyframes) - index_to_change):
                    f_i = self.keyframes[index_to_change+i]
                    if f_i - 20 > f + n:
                        break
                    if f_i <= f + n or (self.is_wheelie[index_to_change+i] and (f_i - 13 <= f + n or (self.is_wheelie[index_to_change] and f_i - 19 <= f + n))):
                        return False
                self.keyframes[index_to_change] = f + n
                return True
        else:  # Modify one of the stick values
            options = [-7, 0, 7]
            options.remove(self.stick_x_values[index_to_change])
            # This does allow for multiple keyframes to have the same stick value in a row.
            # It's important that, if the second consecutive keyframe is a wheelie, it *can* have the same value.
            # But also, enforcing that invariant here would mean that mutations could cascade all the way to the end, which is not good.
            self.stick_x_values[index_to_change] = options[0 if random() < 0.5 else 1]
            # Instead, we enforce the invariant by deleting keyframes with duplicate inputs. This should be fine.
            if self.stick_x_values[index_to_change] == self.stick_x_values[index_to_change+1] and not self.is_wheelie[index_to_change+1]:
                # Delete the one after the one we just changed
                del self.keyframes[index_to_change+1]
                del self.is_wheelie[index_to_change+1]
                del self.stick_x_values[index_to_change+1]
            if self.stick_x_values[index_to_change] == self.stick_x_values[index_to_change-1] and not self.is_wheelie[index_to_change]:
                # Delete the one we just changed
                del self.keyframes[index_to_change]
                del self.is_wheelie[index_to_change]
                del self.stick_x_values[index_to_change]
            return True

    def add(self):
        is_wheelie = random() < 0.1
        insert_index = randint(0, len(self.keyframes))

        f_low = 0 if insert_index == 0 else self.keyframes[insert_index-1] + 1
        f_high = 239 if insert_index == len(self.keyframes) else self.keyframes[insert_index] - 1

        if f_high < f_low:
            return False

        new_f = randint(f_low, f_high)
        for i in range(len(self.keyframes)):
            if i < insert_index:
                if self.is_wheelie[i] and (self.keyframes[i] + 13 >= new_f or (is_wheelie and self.keyframes[i] + 19 >= new_f)):
                    return False
            elif is_wheelie and self.is_wheelie[i] and self.keyframes[i] - 19 <= new_f:
                return False
            
        self.keyframes.insert(insert_index, new_f)
        self.is_wheelie.insert(insert_index, is_wheelie)
        options = [-7, 0, 7]
        self.stick_x_values.insert(insert_index, options[randint(0, 2)])

        return True
    
    def remove(self):
        i = randint(0, len(self.keyframes)-1)

        # I don't think there's any reason to make it more complicated than this?
        # Invariants all don't require checking again on a deleted value, since they
        # only matter if things are "too close". Nothing can possibly get closer, so we good
        del self.keyframes[i]
        del self.is_wheelie[i]
        del self.stick_x_values[i]

        return True

            


def update_frame(frame, frame_of_input):
    global slide
    frames_remaining = 239 - frame_of_input
    
    slide.apply(frame, frame_of_input)
    (a_set, a) = a_forced(frames_remaining)
    if a_set:
        frame.accel = a
    


@event.on_frameadvance
def onFrameAdvance():
    global start_state, best_completion, current_frame, frame_sequence, start_time, slide, best_slide
    stage = classes.RaceManager.state().value
    
    if stage == classes.RaceState.INTRO_CAMERA.value:
        start_time = time()
        savestate.load_from_bytes(start_state)

    if stage == classes.RaceState.COUNTDOWN.value:
        frame = core.get_frame_of_input()

        update_frame(current_frame, frame)
        ttk_lib.write_player_inputs(current_frame)
        frame_sequence.frames.append(copy(current_frame))
    
    if stage == classes.RaceState.RACE.value and start_state != None:
        race_completion = classes.RaceManagerPlayer.race_completion()

        if race_completion > best_completion and len(frame_sequence.frames) == 240:
            print(
                f"New best completion by   {race_completion - best_completion}"
            )
            best_completion = race_completion
            best_slide = slide
            frame_sequence.write_to_file(
                os.path.join(
                    utils.get_script_dir(),
                    "MKW_Inputs",
                    "Startslides",
                    "best_ga_inputs.csv",
                )
            )
            
        slide = deepcopy(best_slide)
        slide.mutate()

        frame_sequence = FrameSequence()
        t = time()
        print(
            f"dt: {t - start_time}\tFinal race completion:   {race_completion}\t\tCurrent best completion: {best_completion}"
        )
        start_time = t
        savestate.load_from_bytes(start_state)


def main() -> None:
    global start_state, best_completion, current_frame, frame_sequence, start_time, slide, best_slide
    
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

    slide = Slide()
    for _ in range(50):
        result = False
        while not result:
            result = slide.add()
    best_slide = slide
    print(len(best_slide.keyframes))

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
    try:
        main()
    except Exception as e:
        print(e)
        global slide
        print(slide.keyframes)
