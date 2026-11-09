void MesgBroadcaster::RemoveListener(HrMesgListener& hrMesgListener)
{
    HrMesgListener *const target = &hrMesgListener;
    HrMesgListener **const data = hrMesgListeners.data();
    HrMesgListener **const end = data + hrMesgListeners.size();
    for (HrMesgListener **p = data; p != end; ++p)
    {
        if (*p == target)
        {
            hrMesgListeners.erase(hrMesgListeners.begin() + (p - data));
            return;
        }
    }
}
