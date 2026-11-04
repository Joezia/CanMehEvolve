const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static FIT_UINT16 lookup[65536];
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (lookup[n] == 0)
                lookup[n] = static_cast<FIT_UINT16>(i + 1);
        }
        initialized = true;
    }

    const FIT_UINT16 idx = lookup[num];
    if (idx != 0)
        return &mesgs[idx - 1];

    return NULL;
}
