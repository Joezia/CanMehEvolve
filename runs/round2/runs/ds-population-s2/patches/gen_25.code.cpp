const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* small[512] = {};
    static bool initialized = false;
    static bool has_high = false;
    if (__builtin_expect(!initialized, 0))
    {
        for (int i = MESGS - 1; i >= 0; --i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (n < 512)
                small[n] = &mesgs[i];
            else
                has_high = true;
        }
        initialized = true;
    }

    if (__builtin_expect(num < 512, 1))
        return small[num];

    if (!has_high)
        return nullptr;

    for (int i = 0; i < MESGS; ++i)
        if (mesgs[i].num == num)
            return &mesgs[i];

    return nullptr;
}
