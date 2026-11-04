const Profile::MESG* Profile::GetMesg(const FIT_UINT16 num)
{
    enum { HASH_SIZE = 1024, HASH_MASK = HASH_SIZE - 1 };
    static FIT_UINT32 table[HASH_SIZE];
    static bool initialized = false;

    if (!initialized)
    {
        for (int i = 0; i < MESGS; ++i)
        {
            const FIT_UINT16 n = mesgs[i].num;
            FIT_UINT32 slot = n & HASH_MASK;
            for (;;)
            {
                const FIT_UINT32 e = table[slot];
                if (e == 0)
                {
                    table[slot] = (static_cast<FIT_UINT32>(n) << 16) |
                                  static_cast<FIT_UINT32>(i + 1);
                    break;
                }
                if ((e >> 16) == n)
                    break;
                slot = (slot + 1) & HASH_MASK;
            }
        }
        initialized = true;
    }

    FIT_UINT32 slot = num & HASH_MASK;
    for (;;)
    {
        const FIT_UINT32 e = table[slot];
        if (e == 0)
            return NULL;
        if ((e >> 16) == num)
            return &mesgs[(e & 0xFFFFu) - 1];
        slot = (slot + 1) & HASH_MASK;
    }
}
