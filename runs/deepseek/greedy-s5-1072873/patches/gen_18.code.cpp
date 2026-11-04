const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    struct CacheEntry
    {
        FIT_UINT32 key;
        const MESG *mesg;
        FIT_UINT16 index[256];
    };

    static CacheEntry cache[16] = {};

    const FIT_UINT32 base = static_cast<FIT_UINT32>(mesgNum) << 2;
    const FIT_UINT32 key1 = base | 1;
    const FIT_UINT32 key2 = base | 2;

    CacheEntry &e = cache[mesgNum & 15];

    if (e.key == key2)
        return e.index[fieldNum];

    if (e.key == key1)
    {
        std::memset(e.index, 0xFF, sizeof(e.index));
        if (e.mesg != NULL)
        {
            const MESG *mesg = e.mesg;
            for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
            {
                const FIT_UINT8 num = mesg->fields[i].num;
                if (e.index[num] == FIT_UINT16_INVALID)
                    e.index[num] = i;
            }
        }
        e.key = key2;
        return e.index[fieldNum];
    }

    e.key = key1;
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
