const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* pool[256][256];
    static bool used[256] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            const FIT_UINT16 n = mesgs[i].num;
            const FIT_UINT16 hb = n >> 8;
            const FIT_UINT16 lb = n & 0xFF;
            used[hb] = true;
            if (pool[hb][lb] == NULL)
                pool[hb][lb] = &mesgs[i];
        }
        initialized = true;
    }

    const FIT_UINT16 hb = num >> 8;
    if (!used[hb])
        return NULL;
    return pool[hb][num & 0xFF];
}
