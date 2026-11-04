const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    struct CacheEntry
    {
        FIT_UINT16 mesgNum;
        FIT_UINT16 state;
        const MESG *mesg;
        FIT_UINT16 index[256];
    };

    static CacheEntry cache[16] = {};

    CacheEntry &e = cache[mesgNum & 15];

    if (e.state == 2 && e.mesgNum == mesgNum)
    {
        return e.mesg ? e.index[fieldNum] : FIT_UINT16_INVALID;
    }

    if (e.state != 0 && e.mesgNum == mesgNum)
    {
        if (e.mesg != NULL)
        {
            for (int i = 0; i < 256; ++i)
                e.index[i] = FIT_UINT16_INVALID;

            const MESG *mesg = e.mesg;
            for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
            {
                const FIT_UINT8 num = mesg->fields[i].num;
                if (e.index[num] == FIT_UINT16_INVALID)
                    e.index[num] = i;
            }
        }
        e.state = 2;
        return e.mesg ? e.index[fieldNum] : FIT_UINT16_INVALID;
    }

    e.mesgNum = mesgNum;
    e.state = 1;
    e.mesg = GetMesg(mesgNum);

    if (e.mesg == NULL)
        return FIT_UINT16_INVALID;

    const MESG *mesg = e.mesg;
    const FIELD *field = mesg->fields;
    const FIELD *end = field + mesg->numFields;
    for (; field != end; ++field)
    {
        if (field->num == fieldNum)
            return static_cast<FIT_UINT16>(field - mesg->fields);
    }

    return FIT_UINT16_INVALID;
}
