const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    struct FieldCacheEntry
    {
        FIT_UINT32 key;
        FIT_UINT16 idx[256];
    };

    static FieldCacheEntry fieldCache[512];
    static const MESG *mesgCache[65536];
    static signed char mesgStatus[65536]; // 0 = unknown, 1 = valid, -1 = invalid

    const FIT_UINT32 key = (FIT_UINT32)mesgNum + 1;
    FieldCacheEntry &entry = fieldCache[mesgNum & 511];

    if (entry.key == key)
        return entry.idx[fieldNum];

    const signed char status = mesgStatus[mesgNum];
    if (status == 0)
    {
        const MESG *mesg = GetMesg(mesgNum);
        if (mesg == NULL)
        {
            mesgStatus[mesgNum] = -1;
            return FIT_UINT16_INVALID;
        }
        mesgCache[mesgNum] = mesg;
        mesgStatus[mesgNum] = 1;
    }
    else if (status < 0)
    {
        return FIT_UINT16_INVALID;
    }

    const MESG *mesg = mesgCache[mesgNum];

    for (int i = 0; i < 256; ++i)
        entry.idx[i] = FIT_UINT16_INVALID;

    const FIT_UINT16 numFields = mesg->numFields;
    for (FIT_UINT16 i = 0; i < numFields; ++i)
    {
        const FIT_UINT8 num = mesg->fields[i].num;
        if (entry.idx[num] == FIT_UINT16_INVALID)
            entry.idx[num] = i;
    }

    entry.key = key;
    return entry.idx[fieldNum];
}
