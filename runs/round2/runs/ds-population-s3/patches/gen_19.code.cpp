const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static FIT_UINT16 index[65536] = { 0 };
    static bool init = false;

    if (!init)
    {
        for (int i = MESGS - 1; i >= 0; i--)
            index[mesgs[i].num] = (FIT_UINT16)(i + 1);
        init = true;
    }

    const FIT_UINT16 v = index[num];
    return v ? &mesgs[v - 1] : NULL;
}
