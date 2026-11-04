const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    const MESG* mesg = GetMesg(mesgNum);
    if (mesg == NULL)
        return FIT_UINT16_INVALID;

    struct FieldIndexTable
    {
        FIT_UINT16 index[MESGS][256];

        FieldIndexTable()
        {
            for (int m = 0; m < MESGS; ++m)
            {
                for (int f = 0; f < 256; ++f)
                    index[m][f] = FIT_UINT16_INVALID;

                for (FIT_UINT16 i = 0; i < mesgs[m].numFields; ++i)
                {
                    const FIT_UINT8 number = mesgs[m].fields[i].num;
                    if (index[m][number] == FIT_UINT16_INVALID)
                        index[m][number] = i;
                }
            }
        }
    };

    static const FieldIndexTable table;
    return table.index[mesg - mesgs][fieldNum];
}
