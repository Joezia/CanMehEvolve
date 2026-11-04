const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* lookup[512] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (n < 512 && lookup[n] == NULL)
                lookup[n] = &mesgs[i];
        }
        initialized = true;
    }

    if (num < 512)
        return lookup[num];

    for (int i = 0; i < MESGS; i++)
    {
        if (mesgs[i].num == num)
            return &mesgs[i];
    }

    return NULL;
}
