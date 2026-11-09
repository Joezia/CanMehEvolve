const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static const MESG* mesgCache[65536];
    static FIT_UINT8 mesgValid[65536];

    const MESG *mesg;
    if (mesgValid[mesgNum])
    {
        mesg = mesgCache[mesgNum];
    }
    else
    {
        mesg = GetMesg(mesgNum);
        mesgCache[mesgNum] = mesg;
        mesgValid[mesgNum] = 1;
    }

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    for (FIT_UINT16 i = 0; i < mesg->numFields; i++)
    {
        if (mesg->fields[i].num == fieldNum)
            return i;
    }

    return FIT_UINT16_INVALID;
}
