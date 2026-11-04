const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* lookup[256] = {};
    static const Profile::MESG* high[MESGS] = {};
    static int high_count = 0;
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (n < 256)
            {
                if (lookup[n] == NULL)
                    lookup[n] = &mesgs[i];
            }
            else
            {
                high[high_count++] = &mesgs[i];
            }
        }
        initialized = true;
    }

    if (num < 256)
        return lookup[num];

    for (int i = 0; i < high_count; i++)
    {
        if (high[i]->num == num)
            return high[i];
    }

    return NULL;
}
