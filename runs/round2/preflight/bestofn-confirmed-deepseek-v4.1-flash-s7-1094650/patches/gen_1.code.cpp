const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* cache[65536] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (cache[mesgs[i].num] == NULL)
                cache[mesgs[i].num] = &mesgs[i];
        }
        initialized = true;
    }

    return cache[num];
}
