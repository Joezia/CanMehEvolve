void MesgBroadcaster::RemoveListener(HrMesgListener& hrMesgListener)
{
    HrMesgListener **begin = hrMesgListeners.data();
    HrMesgListener **end   = begin + hrMesgListeners.size();
    HrMesgListener **it    = begin;
    while (it != end && *it != &hrMesgListener)
        ++it;
    if (it != end)
    {
        HrMesgListener **next = it + 1;
        while (next != end)
        {
            *it = *next;
            ++it;
            ++next;
        }
        hrMesgListeners.pop_back();
    }
}
