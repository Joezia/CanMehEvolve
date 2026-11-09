const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static const MESG *mesgCache[65536];
    static bool mesgValid[65536];

    const MESG *mesg;
    if (mesgValid[mesgNum])
    {
        mesg = mesgCache[mesgNum];
    }
    else
    {
        mesg = GetMesg(mesgNum);
        mesgCache[mesgNum] = mesg;
        mesgValid[mesgNum] = true;
    }

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    const FIELD *fields = mesg->fields;
    const FIT_UINT16 numFields = mesg->numFields;
    for (FIT_UINT16 i = 0; i < numFields; i++)
    {
        if (fields[i].num == fieldNum)
            return i;
    }

    return FIT_UINT16_INVALID;
}
