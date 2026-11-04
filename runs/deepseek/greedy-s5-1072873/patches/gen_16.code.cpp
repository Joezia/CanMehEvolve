const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG** high[256] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; i++)
        {
            FIT_UINT16 n = mesgs[i].num;
            FIT_UINT16 h = n >> 8;
            FIT_UINT16 l = n & 0xFF;

            if (high[h] == NULL)
                high[h] = new const Profile::MESG*[256]();

            if (high[h][l] == NULL)
                high[h][l] = &mesgs[i];
        }
        initialized = true;
    }

    const Profile::MESG** low = high[num >> 8];
    return low ? low[num & 0xFF] : NULL;
}
