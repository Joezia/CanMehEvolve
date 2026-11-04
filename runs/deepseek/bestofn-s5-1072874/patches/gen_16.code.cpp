const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static FIT_UINT16 lookup[65536];
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (lookup[mesgs[i].num] == 0)
                lookup[mesgs[i].num] = static_cast<FIT_UINT16>(i + 1);
        }
        initialized = true;
    }

    const FIT_UINT16 idx = lookup[num];
    return idx ? &mesgs[idx - 1] : NULL;
}
