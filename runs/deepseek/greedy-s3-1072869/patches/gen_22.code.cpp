const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static FIT_UINT16 table[4096]; // zero-initialized
    static bool initialized = false;
    static bool hasHigh = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (n < 4096)
            {
                if (table[n] == 0)
                    table[n] = static_cast<FIT_UINT16>(i + 1);
            }
            else
            {
                hasHigh = true;
            }
        }
        initialized = true;
    }

    if (num < 4096)
    {
        const FIT_UINT16 idx = table[num];
        if (idx == 0)
            return NULL;
        return &mesgs[idx - 1];
    }

    if (!hasHigh)
        return NULL;

    for (int i = 0; i < MESGS; ++i)
    {
        if (mesgs[i].num == num)
            return &mesgs[i];
    }
    return NULL;
}
