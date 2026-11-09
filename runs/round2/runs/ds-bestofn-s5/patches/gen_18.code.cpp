const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static const MESG* mesgCache[65536] = {};
    const MESG* mesg = mesgCache[mesgNum];
    if (mesg == NULL)
    {
        mesg = GetMesg(mesgNum);
        if (mesg == NULL)
        {
            mesgCache[mesgNum] = reinterpret_cast<const MESG*>(1);
            return FIT_UINT16_INVALID;
        }
        mesgCache[mesgNum] = mesg;
    }
    else if (mesg == reinterpret_cast<const MESG*>(1))
    {
        return FIT_UINT16_INVALID;
    }

    static const MESG* lastMesg = NULL;
    static bool fieldTableBuilt = false;
    static FIT_UINT16 fieldIndexTable[256];

    if (mesg != lastMesg)
    {
        lastMesg = mesg;
        fieldTableBuilt = false;
    }
    else if (!fieldTableBuilt)
    {
        for (FIT_UINT16 i = 0; i < 256; ++i)
            fieldIndexTable[i] = FIT_UINT16_INVALID;
        const FIELD* fields = mesg->fields;
        const FIT_UINT16 numFields = mesg->numFields;
        for (FIT_UINT16 i = 0; i < numFields; ++i)
        {
            const FIT_UINT8 num = fields[i].num;
            if (fieldIndexTable[num] == FIT_UINT16_INVALID)
                fieldIndexTable[num] = i;
        }
        fieldTableBuilt = true;
        return fieldIndexTable[fieldNum];
    }
    else
    {
        return fieldIndexTable[fieldNum];
    }

    const FIELD* fields = mesg->fields;
    const FIT_UINT16 numFields = mesg->numFields;
    for (FIT_UINT16 i = 0; i < numFields; ++i)
    {
        if (fields[i].num == fieldNum)
            return i;
    }

    return FIT_UINT16_INVALID;
}
