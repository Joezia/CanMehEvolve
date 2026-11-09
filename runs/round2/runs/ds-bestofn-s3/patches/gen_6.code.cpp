void MesgBroadcaster::RemoveListener(HrvValueMesgListener& hrvValueMesgListener)
{
    if (hrvValueMesgListeners.empty())
        return;

    HrvValueMesgListener ** const data = hrvValueMesgListeners.data();
    HrvValueMesgListener ** const end = data + hrvValueMesgListeners.size();
    for (HrvValueMesgListener ** it = data; it != end; ++it)
    {
        if (*it == &hrvValueMesgListener)
        {
            hrvValueMesgListeners.erase(hrvValueMesgListeners.begin() + (it - data));
            return;
        }
    }
}
