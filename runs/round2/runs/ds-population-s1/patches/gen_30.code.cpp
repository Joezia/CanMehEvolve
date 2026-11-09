Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(NULL)
    , profileIndex(FIT_UINT8_INVALID)
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
    static FIT_UINT16 cachedMesgNum = 0;
    static const Profile::MESG* cachedProfile = NULL;
    static bool cacheValid = false;

    if (cacheValid && cachedMesgNum == mesgNum)
    {
        profile = cachedProfile;
    }
    else
    {
        profile = Profile::GetMesg(mesgNum);
        cachedMesgNum = mesgNum;
        cachedProfile = profile;
        cacheValid = true;
    }

    if (profile != NULL)
    {
        for (FIT_UINT16 i = 0; i < profile->num_fields; ++i)
        {
            if (profile->fields[i].num == fieldNum)
            {
                profileIndex = static_cast<FIT_UINT8>(i);
                break;
            }
        }
    }
}
