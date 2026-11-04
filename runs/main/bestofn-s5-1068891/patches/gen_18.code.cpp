const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG *mesg = GetMesg(mesgNum);

    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    // Unroll loop for small number of fields (typical case in FIT profile)
    const FIT_UINT16 numFields = mesg->numFields;
    if (numFields > 0 && mesg->fields[0].num == fieldNum) return 0;
    if (numFields > 1 && mesg->fields[1].num == fieldNum) return 1;
    if (numFields > 2 && mesg->fields[2].num == fieldNum) return 2;
    if (numFields > 3 && mesg->fields[3].num == fieldNum) return 3;
    if (numFields > 4 && mesg->fields[4].num == fieldNum) return 4;
    if (numFields > 5 && mesg->fields[5].num == fieldNum) return 5;
    
    // Fallback for larger field counts
    for (FIT_UINT16 i = 6; i < numFields; i++)
    {
        if (mesg->fields[i].num == fieldNum)
            return i;
    }

    return FIT_UINT16_INVALID;
}
