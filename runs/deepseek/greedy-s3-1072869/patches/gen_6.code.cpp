void MesgBroadcaster::RemoveListener(HrvValueMesgListener& hrvValueMesgListener)
{
    HrvValueMesgListener **begin = hrvValueMesgListeners.data();
    HrvValueMesgListener **end = begin + hrvValueMesgListeners.size();
    HrvValueMesgListener **it = begin;
    while (it != end && *it != &hrvValueMesgListener)
        ++it;
    if (it != end)
    {
        HrvValueMesgListener **src = it + 1;
        while (src != end)
            *it++ = *src++;
        hrvValueMesgListeners.pop_back();
    }
}
