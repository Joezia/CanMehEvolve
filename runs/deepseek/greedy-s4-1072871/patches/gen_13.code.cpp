const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static FIT_UINT16* fieldTables[65536] = {};
    static FIT_UINT16* invalidTable = NULL;

    FIT_UINT16* table = fieldTables[mesgNum];
    if (table != NULL)
    {
        return table[fieldNum];
    }

    const MESG *mesg = GetMesg(mesgNum);
    if (mesg == NULL)
    {
        if (invalidTable == NULL)
        {
            invalidTable = new FIT_UINT16[256];
            for (FIT_UINT16 i = 0; i < 256; i++)
            {
                invalidTable[i] = FIT_UINT16_INVALID;
            }
        }
        fieldTables[mesgNum] = invalidTable;
        return FIT_UINT16_INVALID;
    }

    table = new FIT_UINT16[256];
    for (FIT_UINT16 i = 0; i < 256; i++)
    {
        table[i] = FIT_UINT16_INVALID;
    }

    for (FIT_UINT16 i = 0; i < mesg->numFields; i++)
    {
        const FIT_UINT16 num = mesg->fields[i].num;
        if (num < 256 && table[num] == FIT_UINT16_INVALID)
        {
            table[num] = i;
        }
    }

    fieldTables[mesgNum] = table;
    return table[fieldNum];
}
