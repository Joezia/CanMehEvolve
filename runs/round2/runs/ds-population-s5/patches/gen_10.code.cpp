const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    static FIT_UINT16 cache[65536][256];
    static bool built[65536];

    if (!built[mesgNum])
    {
        for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
        {
            const FIT_UINT8 num = mesg->fields[i].num;
            if (cache[mesgNum][num] == 0)
                cache[mesgNum][num] = (FIT_UINT16)(i + 1);
        }
        built[mesgNum] = true;
    }

    const FIT_UINT16 val = cache[mesgNum][fieldNum];
    return val ? (FIT_UINT16)(val - 1) : FIT_UINT16_INVALID;
}
