from dolphin import gui
from Modules import mkw_classes as classes

def up(charge):
    return min((0.982*charge) + 0.02, 1.0)

def down(charge):
    return 0.96*charge

def up_inv(charge):
    return max((charge - 0.02)/0.982, 0.0)

def down_inv(charge):
    return min(charge / 0.96, 1.0)

def repeat(f, x, n):
    for _ in range(n):
        x = f(x)
    return x

def boost_possible(charge, frames_remaining):
    if frames_remaining <= 0:
        global min_charge, max_charge
        return min_charge <= charge and charge <= max_charge
    
    global a_forced_if_below, a_fails_if_below
    if charge < a_forced_if_below[frames_remaining]:
        return charge > a_fails_if_below[frames_remaining]
    
    return boost_possible(up(charge), frames_remaining-1) or boost_possible(down(charge), frames_remaining-1)

def a_forced(frames_remaining):
    global holding_a
    if frames_remaining == 0:
        global min_charge
        # Reset this for the next start slide
        # This if statement has to be second because it hates me specifically! cool
        holding_a = False
        # Special case: if you want no boost, you can just release A.
        return (True, min_charge != 0.0)

    if holding_a:
        return (True, True)

    global a_forced_if_below
    if frames_remaining >= len(a_forced_if_below):
        return (False, False)
    
    charge = classes.KartState.start_boost_charge()
    if charge < a_forced_if_below[frames_remaining]:
        holding_a = True
        return (True, True)
    
    # 70 is the last frame where you can't lock yourself out of a start boost by a specific input
    # With the sole exception of being too low, which is already handled by the above case.
    # It is also only possible to lock yourself out this way at charges above 0.5
    # (actually, more like 0.59, but I'm being safe)
    if charge <= 0.5 or frames_remaining >= 70:
        return (False, False)
    
    up_possible = boost_possible(up(charge), frames_remaining-1)
    down_possible = boost_possible(down(charge), frames_remaining-1)
    return (not (up_possible and down_possible), up_possible)

def precalculate_lists():
    if not ('min_charge' in globals() and 'max_charge' in globals()):
        gui.add_osd_message("ERROR: Must define variables min_charge and max_charge before using start_boost module.\nTry using boost_init_XXf.", duration_ms=20000)
        raise Exception()
    global a_forced_if_below, a_fails_if_below, min_charge, max_charge, holding_a
    holding_a = False

    a_forced_if_below = [1.0 if min_charge != 0.0 else min_charge]
    frames_remaining = 1
    while len(a_forced_if_below) < 240:
        thresh = min(repeat(up_inv, max_charge, frames_remaining), down_inv(repeat(up_inv, min_charge, frames_remaining-1)))
        if thresh <= 0:
            break
        frames_remaining += 1
        a_forced_if_below.append(thresh)
    
    a_fails_if_below = [min_charge]
    frames_remaining = 1
    while len(a_fails_if_below) < 240:
        thresh = repeat(up_inv, min_charge, frames_remaining)
        if thresh <= 0:
            break
        frames_remaining += 1
        a_fails_if_below.append(thresh)

def boost_init_00f():
    global min_charge, max_charge
    # This is true because you can always just release A on the last frame and get no boost or burnout
    min_charge = 0.0
    max_charge = 1.0

def boost_init_10f():
    global min_charge, max_charge
    min_charge = 0.85
    max_charge = 0.88

def boost_init_20f():
    global min_charge, max_charge
    min_charge = 0.88
    max_charge = 0.905

def boost_init_30f():
    global min_charge, max_charge
    min_charge = 0.905
    max_charge = 0.925

def boost_init_45f():
    global min_charge, max_charge
    min_charge = 0.925
    max_charge = 0.94

def boost_init_70f():
    global min_charge, max_charge
    min_charge = 0.94
    max_charge = 0.95

def boost_init_burnout():
    global min_charge, max_charge
    min_charge = 0.95
    max_charge = 1.0

def get_range():
    global min_charge, max_charge
    return (min_charge, max_charge)

if __name__ == '__main__':
    boost_init_70f()
    precalculate_lists()
    global a_forced_if_below, a_fails_if_below
    print(repeat(down, 1.0, 5))
    print(a_forced_if_below)