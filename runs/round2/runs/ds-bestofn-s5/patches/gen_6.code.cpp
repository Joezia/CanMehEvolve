const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static FIT_UINT16 cachedMesgNum = FIT_UINT16_INVALID;
    static const MESG *cachedMesg = NULL;
    static FIT_UINT32 generation = 0;
    static FIT_UINT32 fieldStamp[256];
    static FIT_UINT16 fieldIndex[256];

    if (mesgNum != cachedMesgNum)
    {
        cachedMesgNum = mesgNum;
        cachedMesg = GetMesg(mesgNum);

        if (cachedMesg != NULL)
        {
            ++generation;
            if (generation == 0)
            {
                for (FIT_UINT16 i = 0; i < 256; ++i)
                    fieldStamp[i] = 0;
                generation = 1;
            }

            for (FIT_UINT16 i = cachedMesg->numFields; i > 0; --i)
            {
                const FIT_UINT8 num = cachedMesg->fields[i - 1].num;
                fieldStamp[num] = generation;
                fieldIndex[num] = i - 1;
            }
        }
    }

    if (cachedMesg != NULL && fieldStamp[fieldNum] == generation)
        return fieldIndex[fieldNum];

    return FIT_UINT16_INVALID;
}
