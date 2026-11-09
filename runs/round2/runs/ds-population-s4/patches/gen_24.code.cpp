void MesgBroadcaster::RemoveListener(WorkoutStepMesgListener& workoutStepMesgListener)
{
    WorkoutStepMesgListener ** const begin = workoutStepMesgListeners.data();
    WorkoutStepMesgListener ** const end   = begin + workoutStepMesgListeners.size();
    WorkoutStepMesgListener ** it = begin;
    while (it != end && *it != &workoutStepMesgListener)
        ++it;
    if (it != end)
        workoutStepMesgListeners.erase(workoutStepMesgListeners.begin() + (it - begin));
}
