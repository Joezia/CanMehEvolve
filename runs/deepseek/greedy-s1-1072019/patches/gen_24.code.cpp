Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(FIT_NULL)
    , profileIndex(FIT_UINT8_INVALID)
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
    static FIT_UINT16 mesgCacheKey[16];
    static const Profile::MESG* mesgCacheProfile[16];
    static bool mesgCacheValid[16] = {};

    const int mesgCacheIdx = mesgNum & 15;
    if (!mesgCacheValid[mesgCacheIdx] || mesgCacheKey[mesgCacheIdx] != mesgNum)
    {
        mesgCacheKey[mesgCacheIdx] = mesgNum;
        mesgCacheProfile[mesgCacheIdx] = Profile::GetMesg(mesgNum);
        mesgCacheValid[mesgCacheIdx] = true;
    }
    profile = mesgCacheProfile[mesgCacheIdx];

    static FIT_UINT16 fieldCacheMesgNum[256];
    static FIT_UINT8 fieldCacheIndex[256];
    static bool fieldCacheValid[256] = {};

    if (!fieldCacheValid[fieldNum] || fieldCacheMesgNum[fieldNum] != mesgNum)
    {
        FIT_UINT8 index = FIT_UINT8_INVALID;
        if (profile != FIT_NULL)
        {
            for (FIT_UINT8 i = 0; i < profile->numFields; ++i)
            {
                if (profile->fields[i].num == fieldNum)
                {
                    index = i;
                    break;
                }
            }
        }
        fieldCacheMesgNum[fieldNum] = mesgNum;
        fieldCacheIndex[fieldNum] = index;
        fieldCacheValid[fieldNum] = true;
    }
    profileIndex = fieldCacheIndex[fieldNum];
}
