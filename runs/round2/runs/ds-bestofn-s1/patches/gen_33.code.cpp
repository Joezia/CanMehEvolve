Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(Profile::GetMesg(mesgNum))
    , profileIndex(FIT_UINT8_INVALID)
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
    if (profile)
    {
        const Profile::FIELD *fields = profile->fields;
        const FIT_UINT8 numFields = profile->numFields;
        for (FIT_UINT8 i = 0; i < numFields; ++i)
        {
            if (fields[i].num == fieldNum)
            {
                profileIndex = i;
                break;
            }
        }
    }
}
