const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static FIT_UINT32 mesgKeys[64] = {0};
    static FIT_UINT16 fieldIndices[64][256];
    static FIT_UINT32 lastKey = 0;
    static FIT_UINT16 *lastMap = NULL;

    const FIT_UINT32 key = static_cast<FIT_UINT32>(mesgNum) + 1;

    if (lastKey == key)
        return lastMap[fieldNum];

    const FIT_UINT32 slot = (static_cast<FIT_UINT32>(mesgNum) * 2654435761u) >> 26;
    FIT_UINT16 *map;

    if (mesgKeys[slot] == key)
    {
        map = fieldIndices[slot];
    }
    else
    {
        map = fieldIndices[slot];

        for (FIT_UINT16 i = 0; i < 256; i++)
            map[i] = FIT_UINT16_INVALID;

        const MESG *mesg = GetMesg(mesgNum);
        if (mesg != NULL)
        {
            const FIELD *fields = mesg->fields;
            const FIT_UINT16 numFields = mesg->numFields;

            for (FIT_UINT16 i = 0; i < numFields; i++)
            {
                const FIT_UINT8 num = fields[i].num;
                if (map[num] == FIT_UINT16_INVALID)
                    map[num] = i;
            }
        }

        mesgKeys[slot] = key;
    }

    lastKey = key;
    lastMap = map;
    return map[fieldNum];
}
