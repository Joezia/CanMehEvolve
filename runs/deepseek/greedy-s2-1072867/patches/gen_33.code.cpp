const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lookup[65536] = {};
    static FIT_UINT16 max_num = 0;
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (lookup[n] == NULL)
                lookup[n] = &mesgs[i];
            if (n > max_num)
                max_num = n;
        }
        initialized = true;
    }

    if (num > max_num)
        return NULL;

    return lookup[num];
}
