
void MesgBroadcaster::AddListener(RecordMesgListener& recordMesgListener)
{
   recordMesgListeners.push_back(&recordMesgListener);
}
