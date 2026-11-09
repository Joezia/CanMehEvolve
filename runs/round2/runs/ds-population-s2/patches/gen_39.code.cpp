const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    if (mesgNum < 256)
    {
        static FIT_UINT32 cache[256 * 256];
        const FIT_UINT32 idx = (FIT_UINT32(mesgNum) << 8) | fieldNum;
        const FIT_UINT32 v = cache[idx];
        if (v != 0)
            return FIT_UINT16(v - 1);

        const MESG *mesg = GetMesg(mesgNum);
        FIT_UINT16 result = FIT_UINT16_INVALID;
        if (mesg != NULL)
        {
            for (FIT_UINT16 i = 0; i < mesg->numFields; i++)
            {
                if (mesg->fields[i].num == fieldNum)
                {
                    result = i;
                    break;
                }
            }
        }
        cache[idx] = FIT_UINT32(result) + 1;
        return result;
    }

    static FIT_UINT32 cache_keys[16384];
    static FIT_UINT16 cache_vals[16384];
    const FIT_UINT32 key = (FIT_UINT32(mesgNum) << 8) | fieldNum;
    const FIT_UINT32 storedKey = key + 1;
    const FIT_UINT32 slot = (mesgNum * 31u + fieldNum) & 16383;
    if (cache_keys[slot] == storedKey)
        return cache_vals[slot];

    const MESG *mesg = GetMesg(mesgNum);
    FIT_UINT16 result = FIT_UINT16_INVALID;
    if (mesg != NULL)
    {
        for (FIT_UINT16 i = 0; i < mesg->numFields; i++)
        {
            if (mesg->fields[i].num == fieldNum)
            {
                result = i;
                break;
            }
        }
    }
    cache_keys[slot] = storedKey;
    cache_vals[slot] = result;
    return result;
}
