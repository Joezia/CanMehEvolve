const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static FIT_UINT16 slot[65536] = {};
    static const bool initialized = [] {
        for (int i = static_cast<int>(MESGS) - 1; i >= 0; --i)
        {
            slot[mesgs[i].num] = static_cast<FIT_UINT16>(i + 1);
        }
        return true;
    }();
    (void)initialized;

    const FIT_UINT16 s = slot[num];
    return (s != 0) ? &mesgs[s - 1] : NULL;
}
