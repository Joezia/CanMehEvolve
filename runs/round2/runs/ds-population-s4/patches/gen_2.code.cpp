Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(Profile::GetMesg(mesgNum))
    , profileIndex(FIT_UINT8_INVALID)
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
    for (FIT_UINT8 i = 0; i < profile.numFields; i++)
    {
        if (profile.fields[i].num == fieldNum)
        {
            profileIndex = i;
            break;
        }
    }
}
