void MesgBroadcaster::RemoveListener(StressLevelMesgListener& stressLevelMesgListener)
{
    std::vector<StressLevelMesgListener *>::iterator it = std::find(stressLevelMesgListeners.begin(), stressLevelMesgListeners.end(), &stressLevelMesgListener);
    if (stressLevelMesgListeners.end() != it)
    stressLevelMesgListeners.erase(it);
// noop-2-1
}
