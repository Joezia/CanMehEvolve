const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static FIT_UINT16 cachedMesgNum = 0xFFFF;
    static const MESG *cachedMesg = NULL;

    const MESG *mesg;
    if (cachedMesgNum == mesgNum)
    {
        mesg = cachedMesg;
    }
    else
    {
        mesg = GetMesg(mesgNum);
        cachedMesgNum = mesgNum;
        cachedMesg = mesg;
    }

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    const auto fields = mesg->fields;
    const FIT_UINT16 numFields = mesg->numFields;
    for (FIT_UINT16 i = 0; i < numFields; i++)
    {
        if (fields[i].num == fieldNum)
            return i;
    }

    return FIT_UINT16_INVALID;
}
