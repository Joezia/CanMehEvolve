void MesgBroadcaster::AddListener(FileCreatorMesgListener& fileCreatorMesgListener)
{
   fileCreatorMesgListeners.push_back(&fileCreatorMesgListener);
// noop-2-24
}
