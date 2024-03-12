"""!
@file main.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import thermal_camera as therm
import turret_driver as tur
import actuator_flywheel as act



def actuator_task(shares):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    aim_lock = shares
    
    actuator = act.actuator_driver()
    if_aim = None
    while True:
        if_aim = aim_lock.get()
        actuator.act_test(if_aim)
        yield 0

def turret_task(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    degree,aim_lock = shares
    
    turret = tur.turret_driver()
    
    if_aim = None
    deg = None
    
    while True:
        deg = degree.get()
        if_aim = turret.step_test(deg)
        if if_aim != None:
            aim_lock.put(if_aim)
        yield 0 
            

        
def sensor_task(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    degree = shares
    
    # Stuff copied over from last lab below
    # Code needed to initalize motor
    sensor = therm.thermal_cam()
    if_deg = None
    while True:
        if_deg = sensor.test_MLX_cam(sensor)
        if if_deg != None:
            degree.put(if_deg)
        yield 0 


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    s1 = task_share.Share('f',3, name="My Share1")
    s2 = task_share.Share('h',3, name="My Share2")
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(sensor_task, name="Sensor", priority=1, period=100,
                        profile=True, trace=False, shares=s1)
    task2 = cotask.Task(turret_task, name="Turret", priority=3, period=10,
                        profile=True, trace=False, shares=(s1,s2))
    task3 = cotask.Task(actuator_task, name="Actuator", priority=2, period=100,
                        profile=True, trace=False, shares = s2)
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')