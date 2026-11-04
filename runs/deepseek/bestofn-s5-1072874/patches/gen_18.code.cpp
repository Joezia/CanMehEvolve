const FIT_UINT16 Profile::GetFieldIndex(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
{
    static const int CACHE_SIZE = 128;
    static FIT_UINT16 cachedMesgNum[CACHE_SIZE];
    static const MESG* cachedMesg[CACHE_SIZE];
    static FIT_UINT16 fieldIndex[CACHE_SIZE][256];
    static bool initialized[CACHE_SIZE] = {false};

    const int idx = mesgNum % CACHE_SIZE;

    if (!initialized[idx] || cachedMesgNum[idx] != mesgNum) {
        cachedMesgNum[idx] = mesgNum;
        cachedMesg[idx] = GetMesg(mesgNum);
        if (cachedMesg[idx] != NULL) {
            for (int i = 0; i < 256; i++) {
                fieldIndex[idx][i] = FIT_UINT16_INVALID;
            }
            const MESG* mesg = cachedMesg[idx];
            for (FIT_UINT16 i = 0; i < mesg->numFields; i++) {
                FIT_UINT8 num = mesg->fields[i].num;
                if (fieldIndex[idx][num] == FIT_UINT16_INVALID) {
                    fieldIndex[idx][num] = i;
                }
            }
        }
        initialized[idx] = true;
    }

    if (cachedMesg[idx] == NULL) {
        return FIT_UINT16_INVALID;
    }

    return fieldIndex[idx][fieldNum];
}
