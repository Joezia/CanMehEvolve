const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    struct CacheEntry
    {
        FIT_UINT32 key; // (mesgNum << 16) | state
        const MESG *mesg;
        FIT_UINT16 *index;
    };

    static CacheEntry cache[32] = {};
    static FIT_UINT16 indexPool[32][256];
    static std::array<FIT_UINT16, 256> invalidIndex = []{
        std::array<FIT_UINT16, 256> a;
        a.fill(FIT_UINT16_INVALID);
        return a;
    }();

    const FIT_UINT32 slot = mesgNum & 31;
    CacheEntry &e = cache[slot];
    const FIT_UINT32 expectedKey = (static_cast<FIT_UINT32>(mesgNum) << 16) | 2;

    if (e.key == expectedKey)
    {
        return e.index[fieldNum];
    }

    const FIT_UINT32 state = e.key & 0xFFFF;
    const FIT_UINT16 cachedMesgNum = static_cast<FIT_UINT16>(e.key >> 16);

    if (state != 0 && cachedMesgNum == mesgNum)
    {
        if (e.mesg != NULL)
        {
            FIT_UINT16 *idx = indexPool[slot];
            memset(idx, 0xFF, 256 * sizeof(FIT_UINT16));

            const MESG *mesg = e.mesg;
            for (FIT_UINT16 i = 0; i < mesg->numFields; ++i)
            {
                const FIT_UINT8 num = mesg->fields[i].num;
                if (idx[num] == FIT_UINT16_INVALID)
                    idx[num] = i;
            }
            e.index = idx;
        }
        else
        {
            e.index = invalidIndex.data();
        }
        e.key = expectedKey;
        return e.index[fieldNum];
    }

    e.key = (static_cast<FIT_UINT32>(mesgNum) << 16) | 1;
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
