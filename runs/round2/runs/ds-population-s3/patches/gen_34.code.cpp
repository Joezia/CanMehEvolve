const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    static const MESG* low[256];
    static bool has_high = false;
    static bool init = false;

    if (__builtin_expect(!init, 0))
    {
        for (int i = MESGS - 1; i >= 0; i--)
        {
            const FIT_UINT16 n = mesgs[i].num;
            if (n < 256)
                low[n] = &mesgs[i];
            else
                has_high = true;
        }
        init = true;
    }

    if (__builtin_expect(num < 256, 1))
        return low[num];

    if (has_high)
    {
        for (int i = 0; i < MESGS; i++)
        {
            if (mesgs[i].num == num)
                return &mesgs[i];
        }
    }
    return nullptr;
}
