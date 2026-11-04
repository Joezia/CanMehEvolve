const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

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
