const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* slot[65536] = {};
    static bool initialized = false;
    if (!initialized)
    {
        for (int i = static_cast<int>(MESGS) - 1; i >= 0; --i)
        {
            slot[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }
    return slot[num];
}
