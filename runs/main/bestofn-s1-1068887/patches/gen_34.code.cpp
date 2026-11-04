
void MesgBroadcaster::RemoveListener(HrMesgListener& hrMesgListener)
{
    auto it = std::find(hrMesgListeners.begin(), hrMesgListeners.end(), &hrMesgListener);
    if (it != hrMesgListeners.end())
        hrMesgListeners.erase(it);
}
