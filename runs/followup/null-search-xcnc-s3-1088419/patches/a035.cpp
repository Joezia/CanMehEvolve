void MesgBroadcaster::AddListener(DiveGasMesgListener& diveGasMesgListener)
{
   diveGasMesgListeners.push_back(&diveGasMesgListener);
// noop-3-35
}
