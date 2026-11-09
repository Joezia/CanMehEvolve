const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    struct CacheEntry
    {
        unsigned int key;
        FIT_UINT16 index[256];
    };

    static CacheEntry cache[32];

    const unsigned int key = static_cast<unsigned int>(mesgNum) + 1u;
    CacheEntry &entry = cache[mesgNum & 31u];

    if (entry.key != key)
    {
        entry.key = key;

        for (FIT_UINT16 i = 0; i < 256; ++i)
            entry.index[i] = 0;

        const MESG *mesg = GetMesg(mesgNum);
        if (mesg != NULL)
        {
            for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
            {
                const FIT_UINT16 num = mesg->fields[i].num;
                if (num < 256 && entry.index[num] == 0)
                    entry.index[num] = static_cast<FIT_UINT16>(i + 1);
            }
        }
    }

    const FIT_UINT16 v = entry.index[fieldNum];
    return v ? static_cast<FIT_UINT16>(v - 1) : FIT_UINT16_INVALID;
}
