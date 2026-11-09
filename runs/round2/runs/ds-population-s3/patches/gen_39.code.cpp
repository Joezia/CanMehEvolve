const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* index[65536] = { 0 };
    static bool init = false;

    if (!init)
    {
        for (int i = MESGS - 1; i >= 0; i--)
            index[mesgs[i].num] = &mesgs[i];
        init = true;
    }

    return index[num];
}
