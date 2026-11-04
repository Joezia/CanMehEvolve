void MesgBroadcaster::RemoveListener(HrMesgListener& hrMesgListener)
{
    HrMesgListener ** const first = hrMesgListeners.data();
    HrMesgListener ** const last  = first + hrMesgListeners.size();
    HrMesgListener ** it = first;
    while (it != last && *it != &hrMesgListener)
        ++it;
    if (it != last)
        hrMesgListeners.erase(hrMesgListeners.begin() + (it - first));
}
