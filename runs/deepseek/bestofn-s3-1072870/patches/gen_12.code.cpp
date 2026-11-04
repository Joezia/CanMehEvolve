const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    struct CacheEntry
    {
        FIT_UINT32 tag;
        FIT_UINT16 index;
    };

    static CacheEntry cache[4096];

    const FIT_UINT32 key = (static_cast<FIT_UINT32>(mesgNum) << 8) | fieldNum;
    const FIT_UINT32 tag = key + 1;
    CacheEntry &entry = cache[(key ^ (key >> 8)) & 4095];

    if (entry.tag == tag)
        return entry.index;

    const MESG *mesg = GetMesg(mesgNum);
    FIT_UINT16 index = FIT_UINT16_INVALID;

    if (mesg != NULL)
    {
        const Field *fields = mesg->fields;
        const FIT_UINT16 numFields = mesg->numFields;

        for (FIT_UINT16 i = 0; i < numFields; i++)
        {
            if (fields[i].num == fieldNum)
            {
                index = i;
                break;
            }
        }
    }

    entry.tag = tag;
    entry.index = index;
    return index;
}
