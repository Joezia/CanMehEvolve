
Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(Profile::GetMesg(mesgNum))
    , profileIndex(Profile::GetFieldIndex(mesgNum, fieldNum))
    , type(FIT_UINT8_INVALID)
    , isFieldExpanded(FIT_FALSE)
{
}
