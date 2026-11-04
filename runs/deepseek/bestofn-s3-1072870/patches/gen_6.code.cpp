void MesgBroadcaster::RemoveListener(HrvValueMesgListener& hrvValueMesgListener)
{
    HrvValueMesgListener **begin = hrvValueMesgListeners.data();
    HrvValueMesgListener **end = begin + hrvValueMesgListeners.size();
    HrvValueMesgListener **it = begin;
    while (it != end && *it != &hrvValueMesgListener)
        ++it;
    if (it != end)
        hrvValueMesgListeners.erase(hrvValueMesgListeners.begin() + (it - begin));
}
