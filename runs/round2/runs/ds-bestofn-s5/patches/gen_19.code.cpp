const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static const MESG* mesgCache[65536];
    static FIT_UINT8 mesgFlags[65536]; // bit 0: valid, bit 1: fields[1..] sorted

    FIT_UINT8 flags = mesgFlags[mesgNum];
    const MESG* mesg;
    bool sorted;

    if (flags & 1)
    {
        mesg = mesgCache[mesgNum];
        sorted = (flags & 2) != 0;
    }
    else
    {
        mesg = GetMesg(mesgNum);
        mesgCache[mesgNum] = mesg;

        if (mesg != NULL)
        {
            sorted = true;
            const FIT_UINT16 n = mesg->numFields;
            const FIELD* fields = mesg->fields;

            for (FIT_UINT16 i = 1; i + 1 < n; ++i)
            {
                if (fields[i].num > fields[i + 1].num)
                {
                    sorted = false;
                    break;
                }
            }

            flags = 1 | (sorted ? 2 : 0);
        }
        else
        {
            sorted = false;
            flags = 1;
        }

        mesgFlags[mesgNum] = flags;
    }

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    const FIELD* fields = mesg->fields;
    const FIT_UINT16 n = mesg->numFields;

    if (n == 0)
        return FIT_UINT16_INVALID;

    if (fields[0].num == fieldNum)
        return 0;

    if (sorted)
    {
        FIT_UINT16 lo = 1;
        FIT_UINT16 hi = n;

        while (lo < hi)
        {
            const FIT_UINT16 mid = (lo + hi) >> 1;
            if (fields[mid].num < fieldNum)
                lo = mid + 1;
            else
                hi = mid;
        }

        if (lo < n && fields[lo].num == fieldNum)
            return lo;
    }
    else
    {
        for (FIT_UINT16 i = 1; i < n; ++i)
        {
            if (fields[i].num == fieldNum)
                return i;
        }
    }

    return FIT_UINT16_INVALID;
}
