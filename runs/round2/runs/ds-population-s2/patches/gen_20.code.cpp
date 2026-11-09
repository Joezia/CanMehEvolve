const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static FIT_UINT8 mesgState[65536] = {}; // 0 = unknown, 1 = valid, 2 = invalid
    static FIT_UINT16 fieldIndexCache[65536][256];

    FIT_UINT8 state = mesgState[mesgNum];
    if (state == 0)
    {
        const MESG *mesg = GetMesg(mesgNum);
        if (mesg == nullptr)
        {
            mesgState[mesgNum] = 2;
            return FIT_UINT16_INVALID;
        }

        FIT_UINT16 *cache = fieldIndexCache[mesgNum];
        for (int i = 0; i < 256; ++i)
            cache[i] = FIT_UINT16_INVALID;
        for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
        {
            FIT_UINT8 num = mesg->fields[i].num;
            if (cache[num] == FIT_UINT16_INVALID)
                cache[num] = i;
        }

        mesgState[mesgNum] = 1;
    }
    else if (state == 2)
    {
        return FIT_UINT16_INVALID;
    }

    return fieldIndexCache[mesgNum][fieldNum];
}
