void MesgBroadcaster::AddListener(HsaHeartRateDataMesgListener& hsaHeartRateDataMesgListener)
{
   hsaHeartRateDataMesgListeners.push_back(&hsaHeartRateDataMesgListener);
// noop-4-13
}
