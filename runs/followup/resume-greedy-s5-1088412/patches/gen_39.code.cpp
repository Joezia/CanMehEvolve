const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lookup[65536] = {};
    static bool initialized = false;

    if (__builtin_expect(!initialized, 0))
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (lookup[n] == NULL)
                lookup[n] = &mesgs[i];
        }
        initialized = true;
    }

    return lookup[num];
}
