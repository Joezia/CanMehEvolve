Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(nullptr)
    , profileIndex(FIT_UINT8_INVALID)
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
    static const Profile::Mesg* cachedProfile[128] = {};
    static FIT_UINT16 cachedMesgNum[128] = {};
    static bool cachedValid[128] = {};

    const unsigned cacheIndex = static_cast<unsigned>(mesgNum) & 127U;
    if (cachedValid[cacheIndex] && cachedMesgNum[cacheIndex] == mesgNum)
    {
        profile = cachedProfile[cacheIndex];
    }
    else
    {
        profile = Profile::GetMesg(mesgNum);
        cachedMesgNum[cacheIndex] = mesgNum;
        cachedProfile[cacheIndex] = profile;
        cachedValid[cacheIndex] = true;
    }

    if (profile)
    {
        for (FIT_UINT8 i = 0; i < profile->numFields; ++i)
        {
            if (profile->fields[i].num == fieldNum)
            {
                profileIndex = i;
                break;
            }
        }
    }
}
