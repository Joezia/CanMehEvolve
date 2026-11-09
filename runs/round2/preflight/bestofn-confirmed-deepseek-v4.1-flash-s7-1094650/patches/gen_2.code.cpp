const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    struct CacheEntry
    {
        FIT_UINT16 mesgNum;
        bool valid;
        FIT_UINT16 index[256];
    };

    static CacheEntry cache[256];

    CacheEntry &entry = cache[mesgNum & 0xFF];
    if (!entry.valid || entry.mesgNum != mesgNum)
    {
        entry.mesgNum = mesgNum;
        entry.valid = true;

        for (FIT_UINT16 i = 0; i < 256; ++i)
            entry.index[i] = FIT_UINT16_INVALID;

        for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
        {
            const FIT_UINT8 num = mesg->fields[i].num;
            if (entry.index[num] == FIT_UINT16_INVALID)
                entry.index[num] = i;
        }
    }

    return entry.index[fieldNum];
}
