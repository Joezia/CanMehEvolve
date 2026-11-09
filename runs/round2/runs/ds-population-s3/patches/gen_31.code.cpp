const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* index[65536];
    static bool init = false;

    if (__builtin_expect(!init, 0))
    {
        for (int i = MESGS - 1; i >= 0; i--)
            index[mesgs[i].num] = &mesgs[i];
        init = true;
    }

    return index[num];
}
