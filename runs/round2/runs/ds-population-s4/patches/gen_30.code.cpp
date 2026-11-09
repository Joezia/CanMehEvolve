const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* index[65536] = {};
    static bool initialized = false;
    if (!initialized)
    {
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (index[n] == NULL)
                index[n] = &mesgs[i];
        }
        initialized = true;
    }
    return index[num];
}
