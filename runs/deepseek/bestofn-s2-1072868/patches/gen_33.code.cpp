const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static FIT_UINT16 cachedMesgNum = FIT_UINT16_INVALID;
    static const MESG *cachedMesg = NULL;
    static FIT_UINT16 fieldCache[256];
    static FIT_UINT8 fieldGeneration[256] = {0};
    static FIT_UINT8 currentGeneration = 0;

    if (mesgNum != cachedMesgNum)
    {
        cachedMesg = GetMesg(mesgNum);
        cachedMesgNum = mesgNum;

        if (++currentGeneration == 0)
        {
            std::memset(fieldGeneration, 0, sizeof(fieldGeneration));
            currentGeneration = 1;
        }
    }

    const MESG *mesg = cachedMesg;
    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    if (fieldGeneration[fieldNum] == currentGeneration)
        return fieldCache[fieldNum];

    FIT_UINT16 index = FIT_UINT16_INVALID;
    const FIELD *field = mesg->fields;
    const FIT_UINT16 numFields = mesg->numFields;

    for (FIT_UINT16 i = 0; i < numFields; ++i, ++field)
    {
        if (field->num == fieldNum)
        {
            index = i;
            break;
        }
    }

    fieldGeneration[fieldNum] = currentGeneration;
    fieldCache[fieldNum] = index;
    return index;
}
