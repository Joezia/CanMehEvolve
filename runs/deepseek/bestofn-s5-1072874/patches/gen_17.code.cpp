Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(nullptr)
    , profileIndex(FIT_UINT8_INVALID)
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
    static FIT_UINT16 cachedMesgNum = 0xFFFF;
    static const Profile::MESG* cachedProfile = nullptr;

    if (mesgNum == cachedMesgNum)
    {
        profile = cachedProfile;
    }
    else
    {
        profile = Profile::GetMesg(mesgNum);
        cachedMesgNum = mesgNum;
        cachedProfile = profile;
    }

    if (profile)
    {
        for (FIT_UINT8 i = 0; i < profile->num_fields; ++i)
        {
            if (profile->fields[i].num == fieldNum)
            {
                profileIndex = i;
                break;
            }
        }
    }
}
