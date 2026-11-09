
void MesgBroadcaster::RemoveListener(HrvValueMesgListener& hrvValueMesgListener)
{
    auto it = std::find(hrvValueMesgListeners.begin(), hrvValueMesgListeners.end(), &hrvValueMesgListener);
    if (it != hrvValueMesgListeners.end()) {
        hrvValueMesgListeners.erase(it);
    }
}
