
void MesgBroadcaster::RemoveListener(WorkoutStepMesgListener& workoutStepMesgListener)
{
    auto it = std::find(workoutStepMesgListeners.begin(), workoutStepMesgListeners.end(), &workoutStepMesgListener);
    if (it != workoutStepMesgListeners.end()) {
        workoutStepMesgListeners.erase(it);
    }
}
