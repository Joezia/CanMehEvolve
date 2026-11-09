void MesgBroadcaster::RemoveListener(NmeaSentenceMesgListener& nmeaSentenceMesgListener)
{
    std::vector<NmeaSentenceMesgListener *>::iterator it = nmeaSentenceMesgListeners.begin();
    const std::vector<NmeaSentenceMesgListener *>::iterator end = nmeaSentenceMesgListeners.end();
    while (it != end && *it != &nmeaSentenceMesgListener)
        ++it;
    if (it != end)
    {
        std::move(it + 1, end, it);
        nmeaSentenceMesgListeners.pop_back();
    }
}
