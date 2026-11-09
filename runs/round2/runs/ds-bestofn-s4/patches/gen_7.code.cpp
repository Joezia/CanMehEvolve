const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* by_num[65536] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (by_num[mesgs[i].num] == NULL)
                by_num[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }

    return by_num[num];
}
