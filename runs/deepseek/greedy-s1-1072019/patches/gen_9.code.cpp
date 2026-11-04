const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const Profile::MESG* low[256] = {};
    static const Profile::MESG* highPool[256][256] = {};
    static const Profile::MESG** high[256] = {};
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (n < 256)
            {
                if (low[n] == nullptr)
                    low[n] = &mesgs[i];
            }
            else
            {
                const unsigned hi = n >> 8;
                const unsigned lo = n & 0xFF;
                if (high[hi] == nullptr)
                    high[hi] = highPool[hi];
                if (highPool[hi][lo] == nullptr)
                    highPool[hi][lo] = &mesgs[i];
            }
        }
        initialized = true;
    }

    if (num < 256)
        return low[num];

    const Profile::MESG** block = high[num >> 8];
    return block ? block[num & 0xFF] : nullptr;
}
